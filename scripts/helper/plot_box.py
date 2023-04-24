import pandas as pd
import csv,sys
import os
import numpy as np
import matplotlib.pyplot as plt

pwd = os.getcwd()
benchmarks = ['gru', 'gst', 'gms', 'lmc', 'lmr', 'dcg', 'lgt', 'nst', 'rfl', 'spt']
cv_value = sys.argv[1]


def get_columns():
    for bench in benchmarks:
        workload = bench + '/' + bench + '_ipc_report_' + cv_value + '.csv'
        yield pd.read_csv(workload, usecols=['Sample/real ratio'])['Sample/real ratio'].rename(bench)

big_df = pd.concat(get_columns(), axis=1)
#print(big_df)
ax = big_df.boxplot(column=['gru', 'gst', 'gms', 'lmc', 'lmr', 'dcg', 'lgt', 'nst', 'rfl', 'spt'],
                      return_type='axes')  

myFig = plt.figure();
bp = big_df.boxplot()
out_file = 'box_plots/cv_' + cv_value + '.png'
myFig.savefig(out_file, format="png")
