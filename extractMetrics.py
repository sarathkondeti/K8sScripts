#!/usr/bin/python3
import subprocess
import sys
# Get the app run command
app_cmd = sys.argv[1:]
if len(app_cmd)==0:
    print("please provide app run cmd as argument")
    exit();
# nsys profile parsing
#nsys profile -f true -o report ./heartwall ../../data/heartwall/test.avi 1
nsys_prof = "nsys profile -f true -o nsys_report"
cli_cmd = nsys_prof.split(' ') + app_cmd;
print("Running command")
print(cli_cmd)
#subprocess.call(["nsys","profile", "-f", "true","-o","nsys_report",
#                "./heartwall", "../../data/heartwall/test.avi", "1"]);
subprocess.call(cli_cmd)


# nsys stats --report gpukernsum --format csv --output lol report1.qdrep
