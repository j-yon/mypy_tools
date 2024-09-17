#!/usr/bin/env python3

import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse

scale_dic = {'B': 0, 'KB': 1, 'MB': 2, 'GB': 3, 'TB': 4}

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create plots from pickle files containing data from Valgrind's massif tool")
    parser.add_argument('dataset', help='specify which data set to plot')
    parser.add_argument('--system', nargs='?', help='specify a system to plot, default all')
    parser.add_argument('--scale', nargs='?', default='B', help='scale the memory values to [ KB | MB | GB | TB ], default no scaling')
    return parser.parse_args()

def main() -> None:
    args = parse()

    df = pd.read_pickle(f'~/chem/dlpno_testing/pkl/massif_{args.dataset}.pkl')

    scale = scale_dic[args.scale.upper()]

    max_time = 0
    max_heap = 0

    if args.system:
        time = np.array(df.loc[:, f'{args.system}_time'])
        mem_heap = np.array(df.loc[:, f'{args.system}_heap'])
        mem_heap = np.divide(mem_heap, 1024 ** scale)

        max_time = max(time)
        max_heap = max(mem_heap)

        plt.plot(time, mem_heap, color='k')

    else:
        for time_col, mem_col in zip(df.filter(like='_time'), df.filter(like='_heap')):
            time = np.array(df.loc[:, time_col])
            mem_heap = np.array(df.loc[:, mem_col])
            mem_heap = np.divide(mem_heap, 1024 ** scale)

            if max_time < max(time):
                max_time = max(time)
            if max_heap < max(mem_heap):
                max_heap = max(mem_heap)

            plt.plot(time, mem_heap)

    plt.xlim(0, max_time)
    plt.ylim(0, max_heap)
    plt.xlabel("Instructions executed")
    plt.ylabel(f"Heap allocated ({args.scale})")

    if args.system:
        plt.savefig(f"{args.system}.png", bbox_inches='tight', dpi=1200)
    else:
        plt.savefig(f"{args.dataset}.png", bbox_inches='tight', dpi=1200)

if __name__ == "__main__":
    main()
