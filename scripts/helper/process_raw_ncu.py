# This script reads ncu-rep directly via python

import pandas as pd
import csv,sys,os,io


input_file = 'rnnt-offline.ncu-rep'        #sys.argv[1]
wrk = 'rnnt'                               #sys.argv[2]
base_name = os.path.splitext(input_file)[0]
output_file1 = "rnnt_processed_test.csv"   #wrk + "/" + wrk + "_processed_test.csv"
output_file2 = "rnnt_kernels_test.csv"     #wrk + "/" + wrk + "_kernels_test.csv"

#if os.path.exists(output_file1) and os.path.exists(output_file2):
#    print("processed and kernel files exist")
#    sys.exit()


def read_raw():
    print("Reading ncu raw file... ")
    sys.path.insert(1, '/opt/NVIDIA-Nsight-Compute-2022.2/extras/python')
    import ncu_report
    my_context = ncu_report.load_report(input_file)
    my_range = my_context.range_by_idx(0)
    id = -1
    df = pd.DataFrame(columns=['ID','Kernel Name','gpc__cycles_elapsed.avg','launch__thread_count','smsp__inst_executed.sum'])
    for i in range(0, my_range.num_actions()):
      my_action = my_range.action_by_idx(i)
      my_id = i
      kname = my_action.name()
      cycles = my_action.metric_by_name('gpc__cycles_elapsed.avg').as_double()
      insts = my_action.metric_by_name('smsp__inst_executed.sum').as_uint64()
      nthreads = my_action.metric_by_name('launch__thread_count').as_uint64()
      tmp_row = {'ID':my_id, 'Kernel Name':kname, 'gpc__cycles_elapsed.avg':cycles, 'smsp__inst_executed.sum':insts, 'launch__thread_count':nthreads}
      tmp = pd.DataFrame([tmp_row])
      df = pd.concat([df, tmp], axis=0, ignore_index=True)
    return df

def build_dict(df):
    print("Building dictionary... ")
    my_dict = {}
    for name, df_group in df.groupby('Kernel Name'):
        #print(df_group)
        df1 = df_group.transpose().drop('Kernel Name')
        df1.columns = range(df1.columns.size)
        my_dict[name] = df1
    return my_dict


def export_processed(weights, of1, of2):
    print("Writing result to csv file... ")
    f1 = open(of1, 'w', newline='')
    f2 = open(of2, 'w', newline='')
    wr = csv.writer(f1)
    for key in my_dict.keys():
        wr.writerow([key])
        df = my_dict[key]
        df.to_csv(f1)
    weights.to_csv(f2)
    f1.close()
    f2.close()


def get_weights(my_dict):
    df2 = pd.DataFrame(columns=['Name','Invocations', 'Cycles','Instructions','IPC', 'Instruction Weight', 'Cycle Weight'])
    for key in my_dict:
        df = my_dict[key]
        n_invoc = len(df.columns)
        cycles = df.loc['gpc__cycles_elapsed.avg',:].sum()
        insts = df.loc['smsp__inst_executed.sum',:].sum()
        ipc = insts/cycles
        df2.loc[len(df2)] = [key, n_invoc, cycles, insts, ipc, 0.0, 0.0]
    i_sum = df2['Instructions'].sum()
    c_sum = df2['Cycles'].sum()
    df2['Instruction Weight'] = df2['Instructions']/i_sum
    df2['Cycle Weight'] = df2['Cycles']/c_sum
    df2.sort_values(by=['Instruction Weight'], inplace=True, ascending=False)
    #print(df2)
    return df2



df = read_raw()
my_dict = build_dict(df)
weights = get_weights(my_dict)  
export_processed(weights, output_file1, output_file2) 
