# Sieve scripts
Sieve contains a set of Python scripts that processes the profiled application and reports representative kernel IDs as well as various other information including error and speedup. Scripts are based on Nvidia devices, though the methodology is applicable to other GPU platforms as well.

If you want to use scripts for your own application, the overview is:

1.  Profile the application with profiler, e.g. Nvidia Nsight Compute, and convert the result to raw csv readable file.
2.  Modify the main Sieve script for your purpose to find the representative kernels.
3.  Use modified Accel-Sim tracer to generate the traces of selected kernels.

Below, you will find the details of steps.

Using Nsight Compute command line, the first step is to profile the application. The important thing is to ensure that two metrics are included in the collection list, *instruction* and *cycle* counts. A typical command looks like
```
nv-nsight-cu-cli \
    --cache-control none
    --metrics smsp__inst_executed.sum,gpc__cycles_elapsed.avg  \
	-f -o app_name \
	./app_cmd_with_options
```
Note that for an application with very large number of kernel invocations, Nsight Compute speed gradually slows. It is recommended to either limit the profiled invocation number via `--kill on -c 200000` (exit after profiling 200k kernel invocations) or profile the application section by section. Please see the `helper/merge_raw.py` for more information.

Once the profiler is finished, you will see the report file `app_name.ncu-rep`. The next step is to convert the report to a readable CSV format. The command is:
```
nv-nsight-cu-cli --csv --page raw -i app_name.ncu-rep > app_name_raw.csv
```
Note that the csv file must end with `_raw.csv` and all raw files must be in `raw/` folder as the main Sieve script works in this way.

After profiling all applications and generating raw csv files, the next step is to modify the main script and run it. The main script is `run_all.py` and on top of the script, you will see the list of variables that you should change based on your need.

- `cv_list` which is the list of Coefficient of Variation values. For example, `cv_list=['0.1','0.2']`
- `benchmarks` which is a list of workload names separated by comma. For example, `benchmarks=['app_name']`. Note that the script automatically appends `_raw.csv` to the workload name.
- `root_path` which is the path containing scripts and also `raw/` folder that contains raw CSV files.
- `excel_file` which is the final report file name.

After setting the variables, run the script with the following command:

```
python3 run_all.py
```

For each workload, various files are generated, but in the end all results are summarized in the `excel_file`.
