import pandas as pd
import numpy as np
import csv,sys,os
from IPython.display import display

base_name = sys.argv[1]
cv_value = sys.argv[2]
if1 = base_name + "/" + base_name + '_kernels.csv'
if2 = base_name + "/" + base_name + '_processed_report_' + str(cv_value) + '.csv'
of = base_name + "/" + base_name + '_ipc_report_' + str(cv_value) + '.csv'
of2 = "final.txt"
of3 = ".temp.txt"
my_dict = {}



df1 = pd.read_csv(if1, thousands=',', usecols=['Name', 'IPC', 'Cycles', 'Instructions'])
app_inst = df1['Instructions'].sum()
app_cycles = df1['Cycles'].sum()
app_ipc = app_inst/app_cycles
#print(df1)


df2 = pd.read_csv(if2, thousands=',', usecols=['Name', 'Inst percent', 'Invoc IPC', 'Instructions', 'Cycles','Cluster_wg','Cluster_cv'])
sample_inst = df2['Instructions'].sum()
sample_cycles = df2['Cycles'].sum()
#print(df)
for name, df_group in df2.groupby('Name'):
    my_dict[name] = df_group[['Inst percent', 'Invoc IPC']].T

cnt = 1
f1 = open(of, 'w', newline='')
wr1 = csv.writer(f1)
csv_data = ["Num", "Name", "Sample IPC", "Real IPC", "Sample/real ratio"]
wr1.writerow(csv_data)
app_sample_ipc = 0.0


df3 = pd.DataFrame(columns=['Name', 'Weight', 'Sample IPC','w/ipc'])


for key in my_dict:
    df = my_dict[key]
    ipcs = df.iloc[1,:].astype(float)
    wgs = df.iloc[0,:].astype(float)
    sum_w = wgs.sum()
    w_i = wgs/ipcs
    sum_w_i = w_i.sum()
    sample_ipc = sum_w/sum_w_i
    
    row = df1.loc[ df1['Name'] == key.replace('"', '')]
    kernel_ipc = row.at[row.index[0],'IPC']
    
    csv_data = [str(cnt), str(key), 
                str(sample_ipc), str(kernel_ipc),
                str(sample_ipc/kernel_ipc)]
    wr1.writerow(csv_data)
    cnt += 1

    row = df1.loc[ df1['Name'] == key.replace('"', '')]
    kernel_i = row.at[row.index[0],'Instructions']
    kernel_w = kernel_i/app_inst
    tmp_row = {'Name':key, 'Weight':kernel_w, 'Sample IPC':sample_ipc, 'w/ipc':kernel_w/sample_ipc}
    tmp = pd.DataFrame([tmp_row])
    df3 = pd.concat([df3, tmp], axis=0, ignore_index=True)
#print(df3)

sum_w = df3['Weight'].sum()
sum_w_ipc = df3['w/ipc'].sum()
app_sample_ipc = sum_w/sum_w_ipc
c_tilda = app_inst/app_sample_ipc


v1 = df2['Cluster_wg']
v2 = df2['Cluster_cv']
s = 0
for x, y in zip(v1, v2):
    s += x * y
wam = s / sum(v1)
#print(wam)
    


f2 = open(of2, 'a', newline='')
f2.write(base_name + " cv " + cv_value + "\n")
f2.write("App IPC " + str(app_ipc) + "\n")
f2.write("App sample IPC " + str(app_sample_ipc) + "\n")
f2.write("Sample_app_ipc_ratio " + str(app_sample_ipc/app_ipc) + "\n")
f2.write("App_sample_ipc_ratio " + str(app_ipc/app_sample_ipc) + "\n")
f2.write("app_sample_ins_ratio " + str(app_inst/sample_inst) + "\n")
f2.write("No. sampled kernels " + str(len(df2)) + "\n")
f2.write("App sample inst " + str(sample_inst) + "\n")
f2.write("App cycles " + str(app_cycles) + "\n")
f2.write("App sample cycles " + str(c_tilda) + "\n")
f2.write("App CV " + str(wam) + "\n\n")


f3 = open(of3, 'w', newline='')
f3.write(str(abs(app_cycles-c_tilda)*100/app_cycles) + "\n")
f3.write(str(app_inst/sample_inst) + "\n")
f3.write(str(app_cycles/sample_cycles) + "\n")
f3.write(str(c_tilda) + "\n")
f3.write(str(wam))

f1.close()
f2.close()
f3.close()
