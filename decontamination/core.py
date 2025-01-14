# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['logger', 'MINHASH_SEED', 'NON_ALPHA', 'hash_content', 'query_content', 'jaccard_similarity', 'convert_list_to_dict',
           'config_lists', 'process_ds_config', 'process_record', 'parallelized_function', 'BenchmarkCleaner']

# %% ../nbs/00_core.ipynb 2
import datasets
import logging
import multiprocessing
import os
import pickle
import re
import requests
import time

import numpy as np

from datasets import concatenate_datasets, Dataset, load_dataset, load_from_disk, Features, Sequence, Value
from datasketch import LeanMinHash, MinHash, MinHashLSH
from pathlib import Path
from rich.logging import RichHandler
from tqdm.auto import tqdm

# %% ../nbs/00_core.ipynb 3
multiprocessing.set_start_method("fork", force=True)
datasets.logging.set_verbosity_error()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(RichHandler(rich_tracebacks=True))
logger.propagate = False

# %% ../nbs/00_core.ipynb 5
MINHASH_SEED = 42
NON_ALPHA = re.compile("[^A-Za-z_0-9]")

# %% ../nbs/00_core.ipynb 6
def hash_content(
    idx: int, # index of the document
    content: str, # content of the document
    *,
    num_perm: int # number of permutations
    ): # The MinHash signature and the index of the record.
    """
    Hash the content of a record using MinHash. This function should be
    used with multiprocessing and it scales well with the number of cores.
    """
    m = MinHash(num_perm=num_perm, seed=MINHASH_SEED)
    m.update_batch([token.encode("utf-8") for token in {t for t in NON_ALPHA.split(content) if t}])
    return {"__signature__": m.hashvalues, "__id__": idx}

# %% ../nbs/00_core.ipynb 8
def query_content(
    idx: int, # index of the document
    signature: np.ndarray, # MinHash signature of the document
    *,
    index: MinHashLSH # The MinHashLSH index. It is shared across all processes when using multiprocessing with fork without copy.
    ): # The query result.
    """
    Query the MinHashLSH index for the record. This function can be used with multiprocessing
    as long as the index is shared across processes.
    Parameters.
    """
    return {
        "__neighbors__": [
            str(dup_idx)
            for dup_idx in index.query(
                LeanMinHash(seed=MINHASH_SEED, hashvalues=signature),
            )
        ],
        "__id__": idx,
    }

# %% ../nbs/00_core.ipynb 9
def jaccard_similarity(
    s1: str, # The first string to compare.
    s2: str # The second string to compare.
    ) -> float: # The Jaccard similarity between the two strings.
    """
    Calculate the jaccard similarity between two code snippets.
    """
    tokens1 = set([t for t in NON_ALPHA.split(s1) if t.strip()])
    tokens2 = set([t for t in NON_ALPHA.split(s2) if t.strip()])
    return len(tokens1 & tokens2) / max(1, len(tokens1 | tokens2))

# %% ../nbs/00_core.ipynb 11
def convert_list_to_dict(list):
    result = {}
    for item in list:
        config = item['config']
        split = item['split']
        if split == "train": continue
        if config in result:
            result[config].append(split)
        else:
            result[config] = [split]
    return result

# %% ../nbs/00_core.ipynb 12
def config_lists(name):
    token = os.environ.get("HF_ACCESS_TOKEN")
    if token is None:
        raise ValueError("HF_ACCESS_TOKEN is not set")
    headers = {"Authorization": f"Bearer {token}"}
    API_URL = f"https://datasets-server.huggingface.co/splits?dataset={name}"
    def query():
        response = requests.request("GET", API_URL, headers=headers)
        return response.json()
    data = query()

    return convert_list_to_dict(data["splits"])

# %% ../nbs/00_core.ipynb 14
def process_ds_config(name, ds_dict, output_dir):
    for config, splits in ds_dict.items():
        for split in splits:
            config_name = f"{name}_{config}_{split}"
            benchmarks_path = os.path.join(output_dir, config_name)
            try:
                ds = load_dataset(name, config, split=split, num_proc=os.cpu_count())
            except Exception as e:
                logger.error(e)
                logger.error(f"Failed to load {name} {config} {split}")
                continue
            remove_columns = []
            for column, val_type in ds.features.items():
                if val_type.dtype != "string":
                    remove_columns.append(column)
            
            ds = ds.remove_columns(remove_columns)
            yield ds, config_name

# %% ../nbs/00_core.ipynb 16
def process_record(record, check_for_fp, ds, column, benchmarks, threshold):
    if check_for_fp:
        neighbors = set(record["__neighbors__"])
        curr_text = ds[record["__id__"]][column]
        for neighbor in neighbors:
            reference = benchmarks[int(neighbor)]
            reference_text = reference["__content__"]
            if jaccard_similarity(curr_text, reference_text) >= threshold:
                break
        else:
            return
    return record["__id__"]

def parallelized_function(queried, check_for_fp, ds, column, benchmarks, threshold, num_workers):
    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.starmap(process_record, [(record, check_for_fp, ds, column, benchmarks, threshold) for record in queried])
        dup_ids = {result for result in results if result is not None}
    return dup_ids

# %% ../nbs/00_core.ipynb 17
class BenchmarkCleaner:
    """
    A class to clean the benchmark dataset.
    """
    def __init__(
        self,
        benchmark_names: list, # The list of benchmark names to clean.
        output_dir: str, # The output directory to save the cleaned datasets and intermediate results.
        threshold: float = 0.5, # The threshold to use for the MinHashLSH index.
        num_perm: int = 128, # The number of permutations to use for the MinHashLSH index.
        num_workers: int = 1 # The number of workers to use for the MinHashLSH index.
    ):
        self.bm_names = benchmark_names
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.threshold = threshold
        self.num_perm = num_perm
        self.num_workers = num_workers
        self.hash_benchmark_datasets()

    def hash_benchmark_datasets(self):
        # grab all directories in the output directory and subdirectories
        self.benchmarks_paths = [
            str(path.parent)
            for path in Path(self.output_dir).rglob("*.json")
        ]
        if len(self.benchmarks_paths) == 0:
            global_idx = 0
            for name in self.bm_names:
                ds_dict = config_lists(name)
                for benchmark_ds, config_name in process_ds_config(name, ds_dict, self.output_dir,):
                    benchmark_ds = benchmark_ds.map(
                            function=lambda x: {
                                **hash_content(
                                    global_idx,
                                    " ".join(
                                        [x[col] for col in benchmark_ds.column_names if x[col] is not None]
                                    ),
                                    num_perm=self.num_perm,
                                ),
                                "__content__": " ".join(
                                    [x[col] for col in benchmark_ds.column_names if x[col] is not None]
                                ),
                            },
                            num_proc=self.num_workers,
                            desc=f"Fingerprinting...",
                        )
                    # Save the benchmark dataset.
                    benchmarks_path = os.path.join(self.output_dir, config_name)
                    benchmark_ds.save_to_disk(benchmarks_path, max_shard_size="1GB")
                    self.benchmarks_paths.append(benchmarks_path)
                    global_idx += 1
        else:
            logger.info("Benchmark datasets already exist. Skipping hashing.")

    def clean(
        self,
        ds: Dataset, # The dataset to clean.
        column: str, # The column to clean.
        check_for_fp: bool = True, # Whether to check for false positives.
    ):
        """
        Clean the dataset. This function does the following:
        1. Hash the content of the provided dataset using MinHash.
        2. Iterate over the benchmark datasets and hash their content.
        3. Query the MinHashLSH index for each record in the provided dataset against the benchmark datasets.
        4. Filter out the records that have a high similarity with the benchmark datasets.
        5. Return the cleaned dataset.
        """
        start_time = time.time()
        DATA_SIZE = len(ds)
        ids = [i for i in range(len(ds))]
        ds = ds.add_column("__id__", ids)
        # ds = ds.map(
        #     lambda _, idx: {"__id__": idx},
        #     with_indices=True,
        #     num_proc=self.num_workers,
        #     desc="Adding index to dataset...",
        # )
        hashed_ds = ds.map(
            function=hash_content,
            fn_kwargs={"num_perm": self.num_perm},
            input_columns=["__id__", column],
            remove_columns=[column],
            num_proc=self.num_workers,
            desc=f"Fingerprinting dataset...",
        )
        # remove unused columns
        hashed_ds = hashed_ds.remove_columns([c for c in hashed_ds.column_names if c not in ["__id__", "__signature__"]])
        benchmarks = []
        print(f"Number of benchmark datasets: {len(self.benchmarks_paths)}")
        # self.benchmarks_paths = self.benchmarks_paths[:100]
        for path in tqdm(self.benchmarks_paths, desc="Loading benchmark datasets..."):
            benchmarks.append(load_from_disk(path))
        benchmarks = concatenate_datasets(benchmarks)
        # Update indices to be global.
        ids = [i for i in range(len(benchmarks))]
        benchmarks = benchmarks.remove_columns(["__id__"])
        benchmarks = benchmarks.add_column("__id__", ids)
        minhash_path = os.path.join(self.output_dir, "minhash_index.pkl")
        if os.path.exists(minhash_path):
            logger.info("MinHashLSH index already exists. Loading from disk...")
            with open(minhash_path, "rb") as f:
                minhash = pickle.load(f)
        else:
            logger.info("MinHashLSH index does not exist. Creating...")
            # Create the MinHashLSH index.
            minhash = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
            with minhash.insertion_session() as session:
                for record in tqdm(benchmarks, desc="Inserting benchmarks into MinHashLSH index..."):
                    session.insert(record["__id__"], LeanMinHash(seed=MINHASH_SEED, hashvalues=record["__signature__"]))

            # Save the MinHashLSH index.
            with open(os.path.join(self.output_dir, "minhash_index.pkl"), "wb") as f:
                pickle.dump(minhash, f)
            
            logger.info("MinHashLSH index created and saved to disk.")
        
        logger.info("Querying MinHashLSH index...")
        # Query the MinHashLSH index for each record in the provided dataset against the benchmark datasets.
        queried = hashed_ds.map(
            function=lambda x, y: query_content(x, y, index=minhash),
            # num_proc=self.num_workers,
            input_columns=[
                "__id__",
                "__signature__",
            ],
            remove_columns=["__signature__"],
            desc="Querying...",
            features=Features(
                {
                    "__id__": Value("uint64"),
                    "__neighbors__": Sequence(Value("string")),
                }
            ),
        ).filter(
            lambda x: len(x["__neighbors__"]) > 0,
            num_proc=self.num_workers,
            desc=f"Filtering...",
        )

        dup_ids = []
        for record in queried:
            dup_id = process_record(record, check_for_fp, ds, column, benchmarks, self.threshold)
            if dup_id is not None:
                dup_ids.append(dup_id)
        # process_record, [(record, check_for_fp, ds, column, benchmarks, threshold) for record in queried
        # dup_ids = parallelized_function(queried, check_for_fp, ds, column, benchmarks, self.threshold, self.num_workers)
        
        # Filter out the duplicate ids.
        final_data = ds.filter(
            lambda idx: idx not in dup_ids,
            input_columns=["__id__"],
            num_proc=self.num_workers,
            desc="Filtering duplicates...",
        )

        FINAL_DATA_SIZE = len(final_data)
        DUP_SIZE = DATA_SIZE - FINAL_DATA_SIZE

        logger.info(f"{'Data Number':<30}: {DATA_SIZE}")
        logger.info(f"{'Duplicate Number':<30}: {DUP_SIZE}")
        logger.info(f"{'Duplicate Rate':<30}: {DUP_SIZE / DATA_SIZE:.2%}")
        logger.info(f"{'Total Time':<30}: {time.time() - start_time:.2f} seconds")

        return final_data
