# This script reads csv files and prints total kernels and invocation statistics

import pandas as pd
import csv

df = pd.DataFrame(columns=['Workload', 'Total Kernels', 'Total Invocations'])
benchmarks = ['3d-unet', 'bert']


def read_raw(input_file):
    #print("Reading raw file... ")
    df = pd.read_csv(input_file, skiprows=[1], usecols=['Kernel Name'])
    return df

def build_dict(df):
    #print("Building dictionary... ")
    my_dict = {}
    for name, df_group in df.groupby('Kernel Name'):
        #print(df_group)
        df1 = df_group.transpose().drop('Kernel Name')
        df1.columns = range(df1.columns.size)
        my_dict[name] = df1
    return my_dict

def get_info(my_dict):
    tk = len(my_dict)
    ti = 0
    for key in my_dict:
        df = my_dict[key]
        n_invoc = len(df.columns)
        ti += n_invoc
    return tk, ti


for bench in benchmarks:
    print(bench, end=' ', flush=True)
    input_file = 'raw/' + bench + '_raw.csv'
    df2 = read_raw(input_file)
    my_dict = build_dict(df2)
    total_kernels, total_invoc = get_info(my_dict)
    tmp_row = {'Workload':bench, 
               'Total Kernels':total_kernels, 
               'Total Invocations':total_invoc }
    tmp = pd.DataFrame([tmp_row])
    df = pd.concat([df, tmp], axis=0, ignore_index=True)
print()
print(df)
print(df.to_latex())
