#!/usr/bin/python3
import subprocess

# Get the app run command
print("Enter app run command: ",end='')
app_cmd = input()

# nsys profile parsing
#nsys profile -f true -o report ./heartwall ../../data/heartwall/test.avi 1
nsys_prof = "nsys profile -f true -o nsys_report"
cli_cmd = nsys_prof.split(' ') + app_cmd.split(' ');
print(cli_cmd)
#subprocess.call(["nsys","profile", "-f", "true","-o","nsys_report",
#                "./heartwall", "../../data/heartwall/test.avi", "1"]);
subprocess.call(cli_cmd)


# nsys stats --report gpukernsum --format csv --output lol report1.qdrep
