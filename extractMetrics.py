#!/usr/bin/python3
import subprocess
import sys
import pandas as pd
import time
#parameters
metrics = "smsp__inst_executed.avg.per_cycle_active,"
metrics+= "smsp__sass_average_branch_targets_threads_uniform.pct,"
metrics+= "smsp__sass_average_data_bytes_per_sector_mem_global_op_ld.pct,"
metrics+= "smsp__thread_inst_executed_per_inst_executed.ratio"

sections = " --section SpeedOfLight --section MemoryWorkloadAnalysis "


nsys_prof = "nsys profile -f true -o nsys_prof"

nsys_stats = "nsys stats --report gpukernsum "
nsys_stats += "--force-overwrite true --force-export true "
nsys_stats += "--format csv --output nsys_stat nsys_prof.qdrep"

ncu_cmd = "ncu -c 5 -s 10 -f -o ncu_report "
ncu_cmd += " --metric " + metrics + sections
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
    df = pd.read_csv("ncu_temp.csv")

    _df = df[df["Metric Name"] == "smsp__inst_executed.avg.per_cycle_active"]
    _df = _df.aggregate({"Metric Value":['mean']})
    dic["ipc"].append("{:.2f}".format(_df['Metric Value']['mean']))

    _df = df[df["Metric Name"] == "smsp__sass_average_branch_targets_threads_uniform.pct"]
    _df = _df.aggregate({"Metric Value":['mean']})
    dic["divergence"].append("{:.2f}".format(_df['Metric Value']['mean']))

    _df = df[df["Metric Name"] == "smsp__sass_average_data_bytes_per_sector_mem_global_op_ld.pct"]
    _df = _df.aggregate({"Metric Value":['mean']})
    dic["glbefficiency"].append("{:.2f}".format(_df['Metric Value']['mean']))

    _df = df[df["Metric Name"] == "smsp__thread_inst_executed_per_inst_executed.ratio"]
    _df = _df.aggregate({"Metric Value":['mean']})
    dic["warpefficiency"].append("{:.2f}".format(_df['Metric Value']['mean']))

    _df = df[df["Metric Name"] == "L2 Hit Rate"]
    _df = _df.aggregate({"Metric Value":['mean']})
    dic["l2hitrate"].append("{:.2f}".format(_df['Metric Value']['mean']))

    _df = df[df["Metric Name"] == "Compute (SM) [%]"]
    _df = _df.aggregate({"Metric Value":['mean']})
    compute = _df['Metric Value']['mean']
    _df = df[df["Metric Name"] == "Memory [%]"]
    _df = _df.aggregate({"Metric Value":['mean']})
    memory = _df['Metric Value']['mean']
    dic["compmemratio"].append("{:.2f}".format(compute/memory))


# collect ncu Metrics
def runNcu(app_cmd):
    df = pd.read_csv("nsys_stat_gpukernsum.csv")
    print(df.head(5))
    print("Enter the #kernels for profiling: ",end='');
    kernels = int(input())

    dic = {'time(%)':[],'totaltime(ns)':[],'instances':[],'avgtime(ns)':[],'kernel':[],
            'ipc':[],'divergence':[],'glbefficiency':[],'warpefficiency':[],'l2hitrate':[],'compmemratio':[]}

    for kernel in range(kernels):
        dic['time(%)'].append(df['Time(%)'][kernel])
        dic['totaltime(ns)'].append(df['Total Time (ns)'][kernel])
        dic['instances'].append(df['Instances'][kernel])
        kernel_name = df["Name"][kernel]
        dic['kernel'].append(kernel_name)
        dic['avgtime(ns)'].append(df['Average (ns)'][kernel])

        kernel_regex = kernel_name.split('.(<',1)[0]
        cli_cmd = ncu_cmd + kernel_regex
        cli_cmd = cli_cmd.split() + app_cmd
        print(cli_cmd)
        subprocess.call(cli_cmd)
        f = open('ncu_temp.csv', 'w')
        process = subprocess.Popen(ncu_csv.split(), stdout=f)
        f.close()
        time.sleep(1)  # sometimes, read_csv in processKernel() doesn't if this sleep() is removed.
        processKernel(dic)
    return dic

def main():
    app_cmd = parseAppCmd()
    runNsysProf(app_cmd)
    dic=runNcu(app_cmd)
    df = pd.DataFrame(dic)
    print("Enter output file name: ",end='')
    output_file = input()
    df.to_csv(output_file+".csv")

if __name__ == "__main__":
    main()
