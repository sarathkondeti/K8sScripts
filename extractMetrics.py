#!/usr/bin/python3
import subprocess
import sys
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
nsys_stats = "nsys stats --report gpukernsum --format csv --output nsys_stat nsys_prof.qdrep"
cli_cmd = nsys_stats.split()
print("2/3 running nsys stats kernel")
print(cli_cmd)
subprocess.call(cli_cmd)
