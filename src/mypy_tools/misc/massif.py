import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

scale_dic = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}


def massif_visualize(dataset: str, system=None, scale="B") -> None:
    """
    Create plot from pickle file containing data from Valgrind's massif tool

    :param dataset: name of the dataset to plot data from
    :param system: name of a system in dataset to plot by itself, default None
    :param scale: scale to use for memory in plot, default [B]ytes
    """

    path = f"/theoryfs2/ds/jadeny/chem/dlpno_testing/pkl/massif_{dataset}.pkl"
    try:
        df = pd.read_pickle(path)
    except OSError as e:
        print(f"Unable to open {path}: {e}", file=sys.stderr)
        return

    scale_factor = scale_dic[scale.upper()]

    max_time = 0
    max_heap = 0

    if system:
        time = np.array(df.loc[:, f"{system}_time"])
        mem_heap = np.array(df.loc[:, f"{system}_heap"])
        mem_heap = np.divide(mem_heap, 1024**scale_factor)

        max_time = max(time)
        max_heap = max(mem_heap)

        plt.plot(time, mem_heap, color="k")

    else:
        for time_col, mem_col in zip(df.filter(like="_time"), df.filter(like="_heap")):
            time = np.array(df.loc[:, time_col])
            mem_heap = np.array(df.loc[:, mem_col])
            mem_heap = np.divide(mem_heap, 1024**scale_factor)

            if max_time < max(time):
                max_time = max(time)
            if max_heap < max(mem_heap):
                max_heap = max(mem_heap)

            plt.plot(time, mem_heap)
            print("plot created")

    plt.xlim(0, max_time)
    plt.ylim(0, max_heap)
    plt.xlabel("Instructions executed")
    plt.ylabel(f"Heap allocated ({scale})")

    if system:
        plt.savefig(f"{system}.png", bbox_inches="tight", dpi=1200)
    else:
        plt.savefig(f"{dataset}.png", bbox_inches="tight", dpi=1200)


def massif_to_pkl(output: str, system: str, dataset: str) -> None:
    """
    Add data from massif output to a pickle file

    :param output: the path to the output file from massif
    :param system: the name of the system analyzed
    :param dataset: the dataset to add the massif output to
    """

    time = []
    mem_heap = []
    mem_heap_extra = []
    with open(output, "r") as f:
        for line in f.readlines():
            if "time=" in line:
                time.append(line.split("=")[1].strip())
            elif "mem_heap_extra" in line:
                mem_heap_extra.append(line.split("=")[1].strip())
            elif "mem_heap" in line:
                mem_heap.append(line.split("=")[1].strip())

    time = np.array([eval(i) for i in time])
    mem_heap = np.array([eval(i) for i in mem_heap]) + np.array(
        [eval(i) for i in mem_heap_extra]
    )

    try:
        df = pd.read_pickle(
            f"/theoryfs2/ds/jadeny/chem/dlpno_testing/pkl/massif_{dataset}.pkl"
        )
        # need to make equal length
        df[f"{system}_time"] = time
        df[f"{system}_heap"] = mem_heap

    except Exception:
        df = pd.DataFrame({f"{system}_time": time, f"{system}_heap": mem_heap})

    df.name = dataset
    df.to_pickle(f"/theoryfs2/ds/jadeny/chem/dlpno_testing/pkl/massif_{dataset}.pkl")
