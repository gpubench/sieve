#   Profiling an application with 600K kernel invocations is slow.
#   You can split the profiling process in five separate runs and then merge the results.
#
#   Nsight Compute commands look like this
#   nv-nsight-cu-cli --metrics gpc__cycles_elapsed.avg,smsp__inst_executed.sum --kill on \
#                    -c 200000 \
#                    -f -o run_1 \
#                    ./application_command_with_arguments
#   nv-nsight-cu-cli --metrics gpc__cycles_elapsed.avg,smsp__inst_executed.sum --kill on \
#                    -s 200000 -c 200000 \
#                    -f -o run_2 \
#                    ./application_command_with_arguments
#   nv-nsight-cu-cli --metrics gpc__cycles_elapsed.avg,smsp__inst_executed.sum --kill on \
#                    -s 400000 -c 200000 \
#                    -f -o run_3 \
#                    ./application_command_with_arguments
#   You will see two files:  run_1.ncu-rep    run_2.ncu_rep    run_3.ncu-rep
#
#   Convert ncu-rep files to csv
#   nv-nsight-cu-cli --csv --page raw -i run_1.ncu-rep > run_1.csv
#   nv-nsight-cu-cli --csv --page raw -i run_2.ncu-rep > run_2.csv
#   nv-nsight-cu-cli --csv --page raw -i run_3.ncu-rep > run_3.csv
#   
#   Run this script to merge the csv files. Edit the range numbers. For 3 files use range(1,4)


import pandas as pd

big_df = pd.DataFrame()
for i in range(1,4):
    fname = 'run_' + str(i) + '.csv'
    if i == 1:
        small_df = pd.read_csv(fname)
    else:
        small_df = pd.read_csv(fname, skiprows=[1])
    #print(small_df)
    frames = [big_df, small_df]
    big_df = pd.concat(frames, ignore_index=True) 
    i += 1
big_df['ID'] = big_df.index - 1
#print(big_df)
big_df.to_csv('run_raw.csv',index=False)
