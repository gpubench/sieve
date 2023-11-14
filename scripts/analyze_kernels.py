import pandas as pd
import csv,sys
import io,os,sys
from math import isnan
import numpy as np
from numpy import array, linspace
from sklearn.neighbors import KernelDensity
from matplotlib.pyplot import plot
from scipy.signal import argrelextrema

wrk = sys.argv[3]
input_file = wrk + "/" + sys.argv[1]              # Reading _processed.csv file from raw processing script
base_name = os.path.splitext(sys.argv[1])[0]
cv_thresh = float(sys.argv[2])
output_file1 = wrk + "/" + base_name + "_stats_" + str(cv_thresh) + ".csv"           # This file contains additional information about kernels for debug purpose
output_file2 = wrk + "/" + base_name + "_report_" + str(cv_thresh) + ".csv"          # This file shows all candidates
output_file3 = wrk + "/" + base_name + "_tiers_" + str(cv_thresh) + ".csv"           # This file shows statistic about tier numbers
if os.path.isfile(output_file1) and os.path.isfile(output_file2) and os.path.isfile(output_file3):
    print("Stat, report and tier files exist")
    sys.exit()
    
f1 = open(output_file1, 'w', newline='')
f2 = open(output_file2, 'w', newline='')
f3 = open(output_file3, 'w', newline='')
wr1 = csv.writer(f1)
wr2 = csv.writer(f2)
wr3 = csv.writer(f3)
csv_data = ["ID", "Name", "Tier", "CTA size", "Inst percent", "Instructions", "Cycle percent", "Cycles", "Invoc IPC","Cluster_wg","Cluster_cv"]
wr2.writerow(csv_data)

# Tiers
t1 = 0
t2 = 0
t3 = 0

# This shows the number index of the parameter for the kernel in _processed.csv.
# First row is the ID, second is the cycle number and so on
cycle_number = 1
cta_number = 2
inst_number = 3
id_number = 0
#ipc_number = 9
final_kernels = []

# For each kenel in _processed.csv, there are: column number (0, 1, ...) and four rows mentioned earlier
# First read and kernel name and then read 5 consecutive lines and build the dictionary
def read_input():
    wrk = {}
    cnt1 = 0
    with open(input_file ) as fp:
        while True:
            cnt1 += 1
            line = fp.readline()
            if not line:
                break
            key = line.strip()
            txt = [ fp.readline().strip() for i in range(5) ]
            txt = '\n'.join(txt)
            wrk[key] = txt
            #print(txt)
    #print(wrk.items())
    my_dict = { k: pd.read_csv(io.StringIO(v), index_col=[0]) for k, v in wrk.items() }
    print("  Input file read")
    return my_dict

def get_basic_stats(row):
    max_value = np.max(row)
    min_value = np.min(row)
    mean_value = np.mean(row)
    std_value = np.std(row)
    cv = std_value/mean_value
    return max_value, min_value, mean_value, std_value, cv


def find_id_ipc(df, cta, inst):
    for c in df.columns:
        column = df[c]
        if column[cta_number] == cta and column[inst_number] == inst:
            return column[id_number], column[inst_number]/column[cycle_number], column[cycle_number]
    return -1,-1,-1 # This shows a bug then... the given inst and cta sizes must have a match in df

def find_cta(df, inst):
    for c in df.columns:
        column = df[c]
        if column[inst_number] == inst:
            return column[cta_number]
 
def find_inst(df, cta):
    for c in df.columns:
        column = df[c]
        if column[cta_number] == cta:
            return column[inst_number]
 
           
def get_histogram(row):
      df = row.value_counts(normalize=True).mul(100).round(1)
      counts = [df.iloc[i] for i in range(min(len(df), 100))]
      v = df.keys().tolist()
      values = [v[i] for i in range(min(len(v), 100))]
      return counts, values
  

def write_report(tier_num, sub_tier_num, key, idx, ipc, cycles, cta_size, inst_percent, cycle_percent, inst):
    csv_data = [str(idx), key, 
                str(tier_num)+'.'+str(sub_tier_num), 
                str(cta_size), str(inst_percent), str(inst), str(inst_percent), str(cycles), str(ipc)]
    wr2.writerow(csv_data)

    
def print_remaining(my_dict):
    for key in list(my_dict.keys()):
        df = my_dict[key]
        num_invoc = len(df.columns)
        cta_row = df.iloc[cta_number]
        cta_max, cta_min, cta_mean, cta_std, cta_cv = get_basic_stats(cta_row)
        cta_counts, cta_values = get_histogram(cta_row)
        wr = csv.writer(f1)
        wr.writerow([key])
        f1.write("Invocations," + str(num_invoc) + "\n")
        f1.write("CTA min," + str(cta_min) + "\n")
        f1.write("CTA max," + str(cta_max) + "\n")
        f1.write("CTA mean," + str(cta_mean) + "\n")
        f1.write("CTA std," + str(cta_std) + "\n")
        f1.write("CTA cv," + str(cta_cv) + "\n")
        f1.write("CTA Histogram counts (%),")
        for i in cta_counts:
            f1.write(str(i) + ",")
        f1.write("\n")
        f1.write("CTA Histogram values,")
        for i in cta_values:
            f1.write(str(i) + ",")
        f1.write("\n")
      
def get_dominant_inst(df):
    df2 = df.loc[[cycle_number,inst_number]].reset_index(drop=True)
    print(df2)
    unique_i = np.unique(df2.loc[1]).tolist()
    print(unique_i)
    sum_c = df2.loc[0].sum()
    sum_i = df2.loc[1].sum()
    print(sum_i, sum_c)
    df_dom_inst = pd.DataFrame(columns=['inst', 'i_weight', 'c_weight', 'i_c_w'])
    for u in unique_i:
        sum_u_i = 0
        sum_u_c = 0
        for c in df2.columns:
            column = df2[c]
            if u == column[1]:
                sum_u_i += column[1]
                sum_u_c += column[0]
        w1 = sum_u_i/sum_i
        w2 = sum_u_c/sum_c
        row = {'inst':u, 'i_weight':w1, 'c_weight':w2, 'i_c_w':w1+w2}
        df_temp = pd.DataFrame([row])
        df_dom_inst = pd.concat([df_dom_inst, df_temp], axis=0, ignore_index=True)    
    print(df_dom_inst)
    df_dom_inst.sort_values(by=['i_c_w'], inplace=True, ascending=False,ignore_index=True)
    print(df_dom_inst)   
    percent = 0.0
    cnt = 0
    can_insts = []
    df_dom_inst['i_weight'] = df_dom_inst['i_weight']
    df_dom_inst['c_weight'] = df_dom_inst['c_weight']
    df_dom_inst['i_c_w'] = df_dom_inst['i_c_w']
    df_dom_inst['inst'] = df_dom_inst['inst']
    while percent <= 90.0 and cnt < len(df_dom_inst):
        w = df_dom_inst['i_c_w'].iloc[cnt]
        percent += w
        ci = df_dom_inst['inst'].iloc[cnt]
        can_insts.append(ci)
        cnt += 1
    return can_insts, df_dom_inst

  
def write_tier1(num_invoc, 
                inst_max,
                inst_sum, cycle_sum, cta_max):
    f1.write("Tier,1\n")
    f1.write("Invocations," + str(num_invoc) + "\n")
    f1.write("CTA," + str(cta_max) + "\n")
    f1.write("Inst," + str(inst_max) + "\n")
    f1.write("Inst count," + str(inst_sum) + "\n")
    f1.write("Cycle count," + str(cycle_sum) + "\n")
    f1.write("IPC," + str(inst_sum/cycle_sum) + "\n")
    f1.write("\n")    
    
def write_report_new(tier_num, key, invoc_id, ipc, invoc_cycles, cta_max, inst, inst_percent, cycle_percent, wg, cv):
    csv_data = [str(invoc_id), key, 
                str(tier_num), 
                str(cta_max), str(inst_percent), str(inst), str(cycle_percent), str(invoc_cycles), str(ipc), str(wg), str(cv)]
    wr2.writerow(csv_data)
 
def write_tier2(num_invoc, 
            inst_max, inst_min, inst_mean, inst_std, inst_cv, inst_counts, inst_values, selected_inst_size,
            cta_max, cta_min, cta_mean, cta_std, cta_cv, cta_counts, cta_values, selected_cta_size,
            inst_sum, cycle_sum):
    f1.write("Tier,2\n")
    f1.write("Invocations," + str(num_invoc) + "\n")
    f1.write("CTA min," + str(cta_min) + "\n")
    f1.write("CTA max," + str(cta_max) + "\n")
    f1.write("CTA mean," + str(cta_mean) + "\n")
    f1.write("CTA std," + str(cta_std) + "\n")
    f1.write("CTA CV," + str(cta_cv) + "\n")
    f1.write("CTA selected," + str(selected_cta_size) + "\n")
    f1.write("CTA bins (%),")
    for i in cta_counts:
        f1.write(str(i) + ",")
    f1.write("\n")
    f1.write("CTA values,")
    for i in cta_values:
        f1.write(str(i) + ",")
    f1.write("\n")     
    f1.write("Inst min," + str(inst_min) + "\n")
    f1.write("Inst max," + str(inst_max) + "\n")
    f1.write("Inst mean," + str(inst_mean) + "\n")
    f1.write("Inst std," + str(inst_std) + "\n")
    f1.write("Inst CV," + str(inst_cv) + "\n")
    f1.write("Inst bins (%),")
    for i in inst_counts:
        f1.write(str(i) + ",")
    f1.write("\n")
    f1.write("Inst values,")
    for i in inst_values:
        f1.write(str(i) + ",")
    f1.write("\n")  
    f1.write("Inst selected," + str(selected_inst_size) + "\n")
    f1.write("Inst count," + str(inst_sum) + "\n")
    f1.write("Cycle count," + str(cycle_sum) + "\n")
    f1.write("IPC," + str(inst_sum/cycle_sum) + "\n")
    f1.write("\n")    

def get_cv(a):
    mean_value = np.mean(a)
    std_value = np.std(a)
    cv = std_value/mean_value
    return cv

# Finding unique instructions in a Tier-3 kernel
def get_unique(df, total_inst):
    df2 = df.iloc[[cycle_number,inst_number]].reset_index(drop=True)
    #print(df2)
    unique_i = np.unique(df2.loc[1]).tolist()
    #print(unique_i)
    sum_c = df2.loc[0].sum()
    sum_i = df2.loc[1].sum()
    #print(sum_i, sum_c)
    df_dom_inst = pd.DataFrame(columns=['inst', 'i_weight', 'c_weight','cluster_weight', 'cycles_vec'])
    for u in unique_i:
        sum_u_i = 0
        sum_u_c = 0
        cnt = 0
        cycle_vector = []
        for c in df2.columns:
            column = df2[c]
            if u == column[1]:
                sum_u_i += column[1]
                sum_u_c += column[0]
                cnt += 1
                cycle_vector.append(column[0])
        w1 = sum_u_i/sum_i
        w2 = sum_u_c/sum_c
        cluster_weight = sum_u_i/total_inst
        row = {'inst':u, 'i_weight':w1, 'c_weight':w2,
               'cluster_weight':cluster_weight, 'cycles_vec':cycle_vector}
        df_temp = pd.DataFrame([row])
        df_dom_inst = pd.concat([df_dom_inst, df_temp], axis=0, ignore_index=True)    
    #print(df_dom_inst)
    df_dom_inst.sort_values(by=['i_weight'], inplace=True, ascending=False,ignore_index=True)
    #print(df_dom_inst)  
    return df_dom_inst, len(unique_i)
    

# Use KDE to subpartition the 1D numbers (unique instructions in a Tier-3 kernel)
# If you want to know the basic code for KDE, see
# https://www.kaggle.com/code/mahmoodnaderan/kernel-density-estimation-kde
def my_kde(v):
    a = array(np.sort(v)).reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=1).fit(a)
    s = linspace(min(a),max(a))
    e = kde.score_samples(s.reshape(-1,1))
    mi = argrelextrema(e, np.less_equal,order=1)[0]
    u = []
    x = []
    l = len(s[mi])
    #print(l)
    #print(len(s))
    #print(mi)
    #print(s[mi])
    #print ("Minima:", s[mi])
    for i in range(l):
        x.clear()
        y = s[mi][i]
        for j in a:
            if j < y:
                x.append(j.item())
                a = np.delete(a, np.where(a == j.item())[0])
        if len(x) == 0:
            continue
        u.append(x.copy()) 
    # Anything in 'a' larger than the largest minima! so they are not captured by the loop.
    u.append(a.tolist())
    #print(u)
    return u


def get_candidates(v, df):
    #print(v)
    u = my_kde(v)
    #print(u)
    #print("First kde groups:", len(u))
    x = []
    for v in u:
        #print(v)
        mean = np.mean(v)
        std = np.std(v)
        cv = std/mean
        # If the subpartition needs another KDE pass, do it again
        if cv > 0.5:
            #plt.clf()
            uu = my_kde(v)
            for y in uu:
                x.append(y)
            continue
        else:
            x.append(v)
    #print(x)
    #print("Final kde groups:", len(x))
    cnt = 0
    df_cluster = pd.DataFrame(columns=['cluster', 'content', 'i_weight', 'c_weight', 'cluster_weight', 'cycles_vec','cluster_cv','selected'])
    for v in x:
        wi_sum = 0
        wc_sum = 0
        new_cluster_weight = 0
        new_cycles_vector = []
        for e in v:
            r = df.loc[ df['inst'] == e]
            wi = r.at[r.index[0],'i_weight']
            wc = r.at[r.index[0],'c_weight']
            wcl = r.at[r.index[0],'cluster_weight']
            cvec = r.at[r.index[0],'cycles_vec']
            wi_sum += wi
            wc_sum += wc
            new_cluster_weight += wcl
            for c in cvec:
                new_cycles_vector.append(c)
        v2 = np.sort(v)
        med = v2[len(v2)//2]
        clcv = get_cv(new_cycles_vector)
        row = {'cluster':cnt, 'content':v, 'i_weight':wi_sum, 'c_weight':wc_sum, 
               'cluster_weight':new_cluster_weight, 'cycles_vec':new_cycles_vector,
               'cluster_cv':clcv,
               'selected':med}
        df_temp = pd.DataFrame([row])
        df_cluster = pd.concat([df_cluster, df_temp], axis=0, ignore_index=True)
        cnt += 1
    #print(df_cluster)    
    return df_cluster



def write_tier3_1(num_invoc, 
                inst_max, inst_min, inst_mean, inst_std, inst_cv,
                cta_max, cta_min, cta_mean, cta_std, cta_cv, cta_counts, cta_valuese,
                inst_sum, cycle_sum):
    f1.write("Tier,3\n")
    f1.write("Invocations," + str(num_invoc) + "\n")
    f1.write("CTA min," + str(cta_min) + "\n")
    f1.write("CTA max," + str(cta_max) + "\n")
    f1.write("CTA mean," + str(cta_mean) + "\n")
    f1.write("CTA std," + str(cta_std) + "\n")
    f1.write("CTA CV," + str(cta_cv) + "\n")
    f1.write("CTA bins (%),")
    for i in cta_counts:
        f1.write(str(i) + ",")
    f1.write("\n")
    f1.write("CTA values,")
    for i in cta_values:
        f1.write(str(i) + ",")
    f1.write("\n")
    f1.write("Inst min," + str(inst_min) + "\n")
    f1.write("Inst max," + str(inst_max) + "\n")
    f1.write("Inst mean," + str(inst_mean) + "\n")
    f1.write("Inst std," + str(inst_std) + "\n")
    f1.write("Inst CV," + str(inst_cv) + "\n")
    f1.write("Inst count," + str(inst_sum) + "\n")
    f1.write("Cycle count," + str(cycle_sum) + "\n")
    f1.write("IPC," + str(inst_sum/cycle_sum) + "\n")
          
def write_tier3_2(selected_inst_size, selected_cta_size):
    f1.write("Selected CTA," + str(selected_cta_size) + "\n")
    f1.write("Seelected inst," + str(selected_inst_size) + "\n")

                

my_dict = read_input()
num_kernels = len(my_dict)
unique_vec = []
clusters = {}
cnt = 0
total_inst = 0
for key in list(my_dict.keys()):
    df = my_dict[key]
    inst_row = df.iloc[inst_number]
    inst_sum = inst_row.sum()
    total_inst += inst_sum


# Main code starts here    
for key in list(my_dict.keys()):
    #print(key)
    df = my_dict[key]
    num_invoc = len(df.columns)
    inst_row = df.iloc[inst_number]
    cta_row = df.iloc[cta_number]
    cycle_row = df.iloc[cycle_number]
    inst_sum = inst_row.sum()
    cycle_sum = cycle_row.sum()
    inst_max, inst_min, inst_mean, inst_std, inst_cv = get_basic_stats(inst_row)
    cta_max, cta_min, cta_mean, cta_std, cta_cv = get_basic_stats(cta_row)
    f1.write("\n")
    wr1.writerow([key])
    if inst_std == 0:
        # Constant instructions
        # Be sure that cta size is also constant for this type. 
        t1 += 1
        assert cta_std == 0
        invoc_id, invoc_ipc, invoc_cycles = find_id_ipc(df, cta_max, inst_max)
        cycle_max, cycle_min, cycle_mean, cycle_std, cycle_cv = get_basic_stats(cycle_row)
        wg = inst_sum/total_inst
        cv = cycle_cv
        clusters[cnt] = [wg, cv]
        cnt += 1        
        write_tier1(num_invoc, 
                    inst_max, 
                    inst_sum, cycle_sum, cta_max)
        write_report_new(1, key, invoc_id, inst_max/invoc_cycles, invoc_cycles, cta_max, inst_max, 1, 1, wg, cv)
    elif inst_cv < cv_thresh:
        # Variable instructions with small variation
        # Find an invocation which has dominant CTA size. 
        # then pick one instance
        t2 += 1
        cta_counts, cta_values = get_histogram(cta_row)
        selected_cta_size = cta_values[0]
        selected_inst = df.iloc[inst_number].loc[df.iloc[cta_number]==selected_cta_size]
        inst_counts, inst_values = get_histogram(selected_inst)
        selected_inst_size = inst_values[0]
        invoc_id, invoc_ipc, invoc_cycles = find_id_ipc(df, selected_cta_size, selected_inst_size)
        assert invoc_id != -1 and invoc_ipc != -1 and invoc_cycles != -1
        cycle_max, cycle_min, cycle_mean, cycle_std, cycle_cv = get_basic_stats(cycle_row)
        wg = inst_sum/total_inst
        cv = cycle_cv
        clusters[cnt] = [wg, cv]
        cnt += 1        
        write_tier2(num_invoc, 
                    inst_max, inst_min, inst_mean, inst_std, inst_cv, inst_counts, inst_values, selected_inst_size,
                    cta_max, cta_min, cta_mean, cta_std, cta_cv, cta_counts, cta_values, selected_cta_size,
                    inst_sum, cycle_sum)
        write_report_new(2, key, invoc_id, selected_inst_size/invoc_cycles, invoc_cycles, selected_cta_size, selected_inst_size, 1, 1, wg, cv)
    else:
        # Variable instructions with large variation, Tier-3
        t3 += 1
        #print(key)
        # Find unique instruction sizes
        df_dom_inst, unique_len = get_unique(df, total_inst)
        unique_inst = df_dom_inst['inst'].tolist()
        assert unique_len > 1
        unique_vec.append(unique_len)
        candidate_cluster = get_candidates(unique_inst, df_dom_inst)
        cta_counts, cta_values = get_histogram(cta_row)
        write_tier3_1(num_invoc, 
                        inst_max, inst_min, inst_mean, inst_std, inst_cv,
                        cta_max, cta_min, cta_mean, cta_std, cta_cv, cta_counts, cta_values,
                        inst_sum, cycle_sum)
        for i in range(0, len(candidate_cluster)):
            cl_id = candidate_cluster.iloc[i]['cluster']
            cl_content = candidate_cluster.iloc[i]['content']
            cli_weight = candidate_cluster.iloc[i]['i_weight']
            clc_weight = candidate_cluster.iloc[i]['c_weight']
            selected_inst_size = candidate_cluster.iloc[i]['selected']
            selected_cta_size = find_cta(df, selected_inst_size)
            invoc_id, invoc_ipc, invoc_cycles = find_id_ipc(df, selected_cta_size, selected_inst_size)
            assert invoc_id != -1 and invoc_ipc != -1 and invoc_cycles != -1
            wg = candidate_cluster.iloc[i]['cluster_weight']
            cv = candidate_cluster.iloc[i]['cluster_cv']
            clusters[cnt] = [wg, cv]
            cnt += 1
            write_tier3_2(selected_inst_size, selected_cta_size)
            write_report_new(3, key, invoc_id, selected_inst_size/invoc_cycles, invoc_cycles, selected_cta_size, selected_inst_size, cli_weight, clc_weight, wg, cv)
        f1.write("\n")
        #print(key, '->', unique_insts, '->', unique_inst_len)
    del my_dict[key] 
        

f1.write("\nNumber of kernels," + str(num_kernels))
f1.write("\nNumber of tier1," + str(t1))
f1.write("\nNumber of tier2," + str(t2))
f1.write("\nNumber of tier3," + str(t3))

tier_data = [num_kernels, t1, t2, t3]
wr3.writerow(tier_data)

f1.close()
f2.close()
f3.close()
print("  Stat file:", output_file1)
print("  Report file:", output_file2)

#print(str(num_kernels), "->", t1, ",", t2, ",", t3)
