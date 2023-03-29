#!/usr/bin/python3
import subprocess

# Get the app run command
print("Enter app run command: ",end='')
app_cmd = input()
print(app_cmd)

# nsys profile parsing
#nsys profile -f true -o report ./heartwall ../../data/heartwall/test.avi 1
nsys_prof = "profile -f true -o nsys_report "
subprocess.call(["nsys","profile", "-f", "true","-o","nsys_report",
                "./heartwall", "../../data/heartwall/test.avi", "1"]);


# nsys stats --report gpukernsum --format csv --output lol report1.qdrep
