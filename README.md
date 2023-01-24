decontamination
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

This repository is heavily inspired by the [BigCode
repository](https://github.com/bigcode-project/bigcode-analysis/tree/main/data_analysis/decontamination)
and is mostly a refactoring of their code. Specifically, the main person
who worked on this repository is [Chenghao
Mou](https://github.com/ChenghaoMou) (Awesome work!).

## Install

``` sh
pip install decontamination
```

## How to use

First you need to specify which benchmarks you want to clean your data
of. You can do this by creating dictionary with the benchmark name in
huggingface’s datasets repository as the key and the name of the column
containing the benchmark data as the value. For example, if you want to
clean your data of the `HumanEval` and `LAMBADA` benchmarks, you would
do the following:

``` python
!export HF_ACCESS_TOKEN=<TOKEN>
```

``` python
from datasets import load_dataset
from decontamination.core import BenchmarkCleaner

# load your dataset
dataset = load_dataset("bigcode/the-stack-smol", data_dir="data/python", split="train")

benchmarks = ["openai_humaneval", "lambada"]
cleaner = BenchmarkCleaner(benchmarks, "/tmp/benchmarks", threshold=0.1, num_perm=128)

# clean the dataset
cleaned_dataset = cleaner.clean(dataset, column="content", check_for_fp=True)
```

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #7fbfbf; text-decoration-color: #7fbfbf">[01/24/23 00:27:37] </span><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Benchmark datasets already exist. Skipping hashing.                        <a href="file:///work/decontamination/decontamination/core.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">core.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///work/decontamination/decontamination/core.py#181" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">181</span></a>
</pre>

    /home/nathan/miniconda3/envs/decontamination/lib/python3.10/site-packages/datasets/arrow_dataset.py:1533: FutureWarning: 'fs' was is deprecated in favor of 'storage_options' in version 2.8.0 and will be removed in 3.0.0.
    You can remove this warning by passing 'storage_options=fs.storage_options' instead.
      warnings.warn(
    Checking for false positives...: 100%|██████████| 8636/8636 [00:33<00:00, 261.25it/s]
    Checking for false positives...: 100%|██████████| 8805/8805 [06:58<00:00, 21.06it/s]
    Checking for false positives...: 100%|██████████| 8722/8722 [06:39<00:00, 21.82it/s]
    Filtering duplicates... #0: 100%|██████████| 1/1 [00:00<00:00, 140.36ba/s]

    Filtering duplicates... #1: 100%|██████████| 1/1 [00:00<00:00, 123.28ba/s]
    Filtering duplicates... #2: 100%|██████████| 1/1 [00:00<00:00, 169.47ba/s]





    Filtering duplicates... #3: 100%|██████████| 1/1 [00:00<00:00, 141.77ba/s]




    Filtering duplicates... #4: 100%|██████████| 1/1 [00:00<00:00, 142.31ba/s]





    Filtering duplicates... #5: 100%|██████████| 1/1 [00:00<00:00, 139.13ba/s]






    Filtering duplicates... #6: 100%|██████████| 1/1 [00:00<00:00, 156.00ba/s]







    Filtering duplicates... #7: 100%|██████████| 1/1 [00:00<00:00, 139.18ba/s]








    Filtering duplicates... #8: 100%|██████████| 1/1 [00:00<00:00, 162.53ba/s]









    Filtering duplicates... #9: 100%|██████████| 1/1 [00:00<00:00, 140.68ba/s]










    Filtering duplicates... #10: 100%|██████████| 1/1 [00:00<00:00, 138.69ba/s]











    Filtering duplicates... #11: 100%|██████████| 1/1 [00:00<00:00, 145.31ba/s]












    Filtering duplicates... #12: 100%|██████████| 1/1 [00:00<00:00, 144.74ba/s]













    Filtering duplicates... #13: 100%|██████████| 1/1 [00:00<00:00, 157.68ba/s]





























    Filtering duplicates... #14: 100%|██████████| 1/1 [00:00<00:00, 95.45ba/s]
    Filtering duplicates... #15: 100%|██████████| 1/1 [00:00<00:00, 135.26ba/s]
















    Filtering duplicates... #16: 100%|██████████| 1/1 [00:00<00:00, 136.07ba/s]



































    Filtering duplicates... #17: 100%|██████████| 1/1 [00:00<00:00, 107.33ba/s]
    Filtering duplicates... #18: 100%|██████████| 1/1 [00:00<00:00, 141.83ba/s]
    Filtering duplicates... #19: 100%|██████████| 1/1 [00:00<00:00, 139.11ba/s]
    Filtering duplicates... #20: 100%|██████████| 1/1 [00:00<00:00, 137.10ba/s]
    Filtering duplicates... #21: 100%|██████████| 1/1 [00:00<00:00, 146.80ba/s]
    Filtering duplicates... #22: 100%|██████████| 1/1 [00:00<00:00, 147.25ba/s]
    Filtering duplicates... #23: 100%|██████████| 1/1 [00:00<00:00, 149.84ba/s]
    Filtering duplicates... #24: 100%|██████████| 1/1 [00:00<00:00, 132.19ba/s]
    Filtering duplicates... #25: 100%|██████████| 1/1 [00:00<00:00, 24.02ba/s]
    Filtering duplicates... #30: 100%|██████████| 1/1 [00:00<00:00, 119.37ba/s]
    Filtering duplicates... #29: 100%|██████████| 1/1 [00:00<00:00, 98.58ba/s]
    Filtering duplicates... #28: 100%|██████████| 1/1 [00:00<00:00, 85.76ba/s]
    Filtering duplicates... #26: 100%|██████████| 1/1 [00:00<00:00, 76.09ba/s]
    Filtering duplicates... #31: 100%|██████████| 1/1 [00:00<00:00, 69.66ba/s]
    Filtering duplicates... #27: 100%|██████████| 1/1 [00:00<00:00, 62.54ba/s]

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #7fbfbf; text-decoration-color: #7fbfbf">[01/24/23 00:41:50] </span><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Data Number                   : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">10000</span>                                      <a href="file:///work/decontamination/decontamination/core.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">core.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///work/decontamination/decontamination/core.py#277" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">277</span></a>
</pre>
<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #7fbfbf; text-decoration-color: #7fbfbf">                    </span><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Duplicate Number              : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3932</span>                                       <a href="file:///work/decontamination/decontamination/core.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">core.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///work/decontamination/decontamination/core.py#278" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">278</span></a>
</pre>
<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #7fbfbf; text-decoration-color: #7fbfbf">                    </span><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Duplicate Rate                : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">39.32</span>%                                     <a href="file:///work/decontamination/decontamination/core.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">core.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///work/decontamination/decontamination/core.py#279" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">279</span></a>
</pre>
<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #7fbfbf; text-decoration-color: #7fbfbf">                    </span><span style="color: #000080; text-decoration-color: #000080">INFO    </span> Total Time                    : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">853.66</span> seconds                             <a href="file:///work/decontamination/decontamination/core.py" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">core.py</span></a><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">:</span><a href="file:///work/decontamination/decontamination/core.py#280" target="_blank"><span style="color: #7f7f7f; text-decoration-color: #7f7f7f">280</span></a>
</pre>
