import pandas as pd
import csv,sys,os,math
import matplotlib.pyplot as plt
import statistics as s
import openpyxl

####################
## Edit this part
cv_list = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']
benchmarks = ['my_workload']        # List of benchmarks, e.g. ['resnet50', '3d-unet']
interpreter = 'python3'             # E.g. python or python3
root_path = '/disk2/ncu2/'          # Folder that contains raw csv files. Each file ends with '_raw.csv'. For example 'my_workload_raw.csv'
excel_file = 'data-frames.xlsx'     # Final xlsx file that contains speedup and error for benchmarks list
##
####################


df_bench_dict = {}
def process_all():
    for bench in benchmarks:
        # Final dataframe columns: CV value, Instruction speedup, Cycle speedup, Error, Projected cycles, Average CV within clusters
        df_bench = pd.DataFrame(columns=['CV', 'SP-I', 'SP-C', 'ER', 'Proj-C', 'CV-AVG'])
        print("==================================")
        print("> Bench: " + bench)
        
        # for each bench name, create a folder
        if not os.path.exists(bench):
            os.makedirs(bench)
            
        # Nsight raw file must ends with _raw.csv
        input_file = root_path + bench + '_raw.csv'
        if not os.path.isfile(input_file):
            print(input_file, "not found")
            sys.exit()
        
        print("----- Running post-process -----")
        command = interpreter + ' process_raw.py ' + input_file + ' ' + bench
        os.system(command)
        
        # process_raw.py executes once for each bench name. Then iterate over CV values.
        er_vec = []
        spi_vec = []
        spc_vec = []
        for cv in cv_list:
            input_file = bench + '_processed.csv'
            if not os.path.isfile(bench + '/' + input_file):
                print(bench, "/", input_file, "not found")
                sys.exit()
            print("cv =", cv)
            command = interpreter + ' analyze_kernels.py ' + input_file + ' ' + cv + ' ' + bench
            print(" ----- Running Analyze -----")
            os.system(command)
    
            input_file = bench
            command = interpreter + ' compare_ipcs.py ' + input_file + ' ' + cv
            print(" ----- Running compare -----")
            os.system(command)
            
            # Read file that contains information about the analyzed benchmark with the given CV
            with open('.temp.txt') as f:
                lines = f.read().splitlines()
            er = round(float(lines[0]), 3)       # Error value
            spi = math.floor(float(lines[1]))    # Speedup (instructions)
            spc = math.floor(float(lines[2]))    # Speedup (cycles)
            c_tilda = float(lines[3])            # ~C (estimated cycle count)
            cv_avg = float(lines[4])             # Average CV value in clusters
            tmp_row = {'CV':cv, 'SP-I':spi, 'SP-C':spc, 'ER':er, 'Proj-C':c_tilda,'CV-AVG':cv_avg}
            tmp = pd.DataFrame([tmp_row])
            df_bench = pd.concat([df_bench, tmp], axis=0, ignore_index=True)
            er_vec.append(er)       # Vectors are used for caluclating the averages
            spi_vec.append(spi)
            spc_vec.append(spc)
            #print(df_bench)
        df_bench_dict[bench] = df_bench
    return df_bench_dict


def save_dict(df_bench_dict):
    if not os.path.isfile(excel_file):
        wb = openpyxl.Workbook()
        wb.save(filename=excel_file)
    for key in df_bench_dict:
        df = df_bench_dict[key]
        #print(i, "\n", df)
        with pd.ExcelWriter(excel_file, mode='a', if_sheet_exists='replace') as writer:  
            df.to_excel(writer, sheet_name=key)



def save_mean(df_bench_dict):
    spi_mean_list = []
    spc_mean_list = []
    er_mean_list = []
    df_cv_list = []
    for cv in cv_list:
        spi_list = []
        spc_list = []
        er_list = []
        df_of_cv = pd.DataFrame(columns=['Name','ER','SP-I','SP-C','Proj-C','CV']) 
        for key in df_bench_dict:
            df = df_bench_dict[key]
            row = df.loc[ df['CV'] == cv ]
            spi = row.at[row.index[0],'SP-I']
            spc = row.at[row.index[0],'SP-C']
            er = row.at[row.index[0],'ER']
            spi_list.append(spi)
            spc_list.append(spc)
            er_list.append(er)
            tmp_row = {'Name':key, 'ER':er, 'SP-I':spi, 'SP-C':spc, 'CV':cv}
            tmp = pd.DataFrame([tmp_row])
            df_of_cv = pd.concat([df_of_cv, tmp], axis=0, ignore_index=True)
        spi_mean = s.harmonic_mean(spi_list)
        spc_mean = s.harmonic_mean(spc_list)
        er_mean = s.mean(er_list)
        spi_mean_list.append(spi_mean)
        spc_mean_list.append(spc_mean)
        er_mean_list.append(er_mean)
        df_cv_list.append(df_of_cv)
    df0 = pd.DataFrame(cv_list)
    df1 = pd.DataFrame(spi_mean_list)
    df2 = pd.DataFrame(spc_mean_list)
    df3 = pd.DataFrame(er_mean_list)
    df1 = pd.concat([df1, df0], axis=1, ignore_index=True)
    df2 = pd.concat([df2, df1], axis=1, ignore_index=True)
    df3 = pd.concat([df3, df2], axis=1, ignore_index=True)
    df3.columns = ['ER','SP-I','SP-C','CV']
    # Write the aevrage values for all workloads for each CV
    with pd.ExcelWriter(excel_file, mode='a', if_sheet_exists='replace') as writer:  
        df3.to_excel(writer, sheet_name='sp-er-mean')
        
    # Write benchmarks per CV 
    i = 0
    for x in df_cv_list:
        with pd.ExcelWriter(excel_file, mode='a', if_sheet_exists='replace') as writer:  
            x.to_excel(writer, sheet_name=cv_list[i])
        i += 1
    
df_bench_dict = process_all()
save_dict(df_bench_dict)
save_mean(df_bench_dict)
