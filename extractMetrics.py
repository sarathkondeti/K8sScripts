#!/usr/bin/python3
import subprocess
import sys
import pandas as pd
# Get the app run command
app_cmd = sys.argv[1:]
if len(app_cmd)==0:
    print("please provide app run cmd as argument")
    exit();

# nsys profile parsing
nsys_prof = "nsys profile -f true -o nsys_prof"
cli_cmd = nsys_prof.split(' ') + app_cmd;
print("1/3 running nsys profile")
print(cli_cmd)
subprocess.call(cli_cmd)

# nsys kernel stats
nsys_stats = "nsys stats --report gpukernsum "
nsys_stats += "--force-overwrite true --force-export true "
nsys_stats += "--format csv --output nsys_stat nsys_prof.qdrep"
cli_cmd = nsys_stats.split()
print("2/3 running nsys stats kernel")
print(cli_cmd)
subprocess.call(cli_cmd)

# print top ~5 kernels
df = pd.read_csv("nsys_stat_gpukernsum.csv")
print(df.head(5))
print("Enter the #kernels for profiling: ",end='');
kernels = int(input())

# collect ncu Metrics
ncu_cmd = "ncu -c 5 -f -o ncu_report "
ncu_cmd += "--metric smsp__inst_executed.avg.per_cycle_active,smsp__sass_average_branch_targets_threads_uniform.pct,lts__t_sector_hit_rate.pct,smsp__thread_inst_executed_per_inst_executed.ratio "
ncu_cmd += "--kernel-name regex:"

ncu_csv = "ncu --import  ncu_report.ncu-rep --csv > ncu.csv"
ncu_csv = ncu_csv.split()
for kernel in range(kernels):
    kernel_name = df["Name"][kernel]
    kernel_regex = kernel_name.spilt('(<',1)[0]
    print(kernel_name)
    cli_cmd = ncu_cmd + kernel_regex
    cli_cmd = cli_cmd.split() + app_cmd
    subprocess.call(cli_cmd)
    subprocess.call(ncu_csv)
