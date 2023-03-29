#!/usr/bin/python3
import subprocess
import sys
import pandas as pd
#parameters
metrics = "smsp__inst_executed.avg.per_cycle_active,"
metrics+= "smsp__sass_average_branch_targets_threads_uniform.pct,"
metrics+= "lts__t_sector_hit_rate.pct,"
metrics+= "smsp__thread_inst_executed_per_inst_executed.ratio"

nsys_prof = "nsys profile -f true -o nsys_prof"

nsys_stats = "nsys stats --report gpukernsum "
nsys_stats += "--force-overwrite true --force-export true "
nsys_stats += "--format csv --output nsys_stat nsys_prof.qdrep"

ncu_cmd = "ncu -c 5 -f -o ncu_report "
ncu_cmd += " --metric " + metrics
ncu_cmd += " --kernel-name regex:"

ncu_csv = "ncu --import  ncu_report.ncu-rep --csv"

# -----------------------------------------------------------------
# Get the app run command
def parseAppCmd():
    app_cmd = sys.argv[1:]
    if len(app_cmd)==0:
        print("please provide app run cmd as argument")
        exit();
    return app_cmd
# -----------------------------------------------------------------
# nsys profile parsing
def runNsysProf(app_cmd):
    cli_cmd = nsys_prof.split(' ') + app_cmd;
    print("1/3 running nsys profile")
    print(cli_cmd)
    subprocess.call(cli_cmd)
    # nsys kernel stats
    cli_cmd = nsys_stats.split()
    print("2/3 running nsys stats kernel")
    print(cli_cmd)
    subprocess.call(cli_cmd)
    # print top ~5 kernels
    df = pd.read_csv("nsys_stat_gpukernsum.csv")

# ------------------------------------------------------------------
# ncu helper functions
def processKernel(dic):
    metrics_names = metrics.split(',');
    metrics_values=[]
    df = pd.read_csv("ncu_temp.csv",index_col="Metric Name")
    for metric in metrics_names:
        _df = df.loc[metric]
        sum=0;
        count=0;
        for i in range(len(_df)):
            sum += _df["Metric Value"][i]
            count += 1
        dic[metric].append(sum/count)

# collect ncu Metrics
def runNcu(app_cmd):
    df = pd.read_csv("nsys_stat_gpukernsum.csv")
    print(df.head(5))
    print("Enter the #kernels for profiling: ",end='');
    kernels = int(input())

    dic = {'runtime(%)':[],'runtime(ns)':[],'kernel':[]}
    for m in metrics.split(','):
        dic[m] = []

    for kernel in range(kernels):
        dic['runtime(%)'].append(df['Time(%)'][kernel])
        dic['runtime(ns)'].append(df['Total Time (ns)'][kernel])
        kernel_name = df["Name"][kernel]
        dic['kernel'].append(kernel_name)
        kernel_regex = kernel_name.split('.(<',1)[0]
        cli_cmd = ncu_cmd + kernel_regex
        cli_cmd = cli_cmd.split() + app_cmd
        print(cli_cmd)
        subprocess.call(cli_cmd)
        with open('ncu_temp.csv', 'w') as f:
            process = subprocess.Popen(ncu_csv.split(), stdout=f)
        processKernel(dic)
    return dic

def main():
    app_cmd = parseAppCmd()
    #kernels = runNsysProf(app_cmd)
    dic=runNcu(2,app_cmd);
    print(dic)

if __name__ == "__main__":
    main()
