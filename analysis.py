#!/usr/bin/env python3

# This script should been run with python3
import sys
import os
import subprocess
import re
import threading

progressed_list_value = 0
lock = threading.Lock()

def get_lines_with_index(lib_path, dict, start, end):
    key_list = list(dict.keys())
    # Loop dict from start to end
    for i in range(start, end):
        line = key_list[i]
        words = re.findall(r'\blib\w+\.so\b', line)
        line_lib_path = lib_path + words[0]
        lib_address = line.split("0x")[1].split(" ")[0].strip()

        # Run addr2line
        ret = subprocess.run("addr2line -e " + line_lib_path + " -f -C -p -i " + lib_address, shell=True, stdout=subprocess.PIPE)
        dict[line] = ret.stdout.decode('utf-8')

        # Update progressed_list_value
        global progressed_list_value

        with lock:
            progressed_list_value += 1
            print("Progressed: " + str(progressed_list_value) + "/" + str(len(dict)), end='\r')

if sys.version_info[0] < 3:
    print("This script should been run with python3")

# Read args
if len(sys.argv) < 3:
    print("Usage: python3 analysis.py <dump_file_path> <lib_path>")
    sys.exit(1)

dump_file_path = sys.argv[1]
lib_path = sys.argv[2]

# Get absolute path
dump_file_path = os.path.abspath(dump_file_path)
lib_path = os.path.abspath(lib_path)

# If lib_path do NOT endwiths /
if lib_path[-1] != "/":
    lib_path += "/"

# Check dump file
if not os.path.exists(dump_file_path):
    print("Dump file not found")
    sys.exit(1)

# Check lib path    
if not os.path.exists(lib_path):
    print("Lib path not found")
    sys.exit(1)

# Check command minidump_stackwalk
if subprocess.run(["which", "minidump_stackwalk"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode != 0:
    print("minidump_stackwalk not found")
    print("Please build and install breakpad from https://gitee.com/girakoo/breadpad.git")
    sys.exit(1)

# Add txt extension to dump file
final_file_path = dump_file_path + ".txt"

symbol_task_list = {}

# Run minidump_stackwalk
print("Run minidump_stackwalk...")
ret = subprocess.run("minidump_stackwalk " + dump_file_path + " " + lib_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
lines = ret.stdout.decode('utf-8').split("\n")

# Find the line that contains the lib name and address
for line in lines:

    if (".lib" in line or ".so" in line) and "0x" in line:
        # Extract lib name and address
        words = re.findall(r'\blib\w+\.so\b', line)
        if len(words) > 0:
            line_lib_path = lib_path + words[0]

            if os.path.exists(line_lib_path):

                # Save line into dictionary
                symbol_task_list[line] = "NONE"

print("Found available " + str(len(symbol_task_list)) + " lines.")

# Convert symbol task with multi thread
# Create 8 threads
num_tasks = 8
split_size = int(len(symbol_task_list) / num_tasks) + 1
threads = []

print("Run addr2line with " + str(num_tasks) + " threads...")
for i in range(num_tasks):
    start = i * split_size
    end = (i + 1) * split_size
    if i == num_tasks - 1:
        end = len(symbol_task_list)
        
    t = threading.Thread(target=get_lines_with_index, args=(lib_path, symbol_task_list, start, end))
    threads.append(t)
    t.start()
    
# Wait all threads
for t in threads:
    t.join()

print("Output results >> " + final_file_path)

# Write final file
with open(final_file_path, 'w') as f1:
    for line in lines:

        if "Found by" in line or "fp = " in line or "sp = " in line:
            if "--details" in sys.argv :
                f1.write(line + "\n")
        else:
            if line in symbol_task_list:
                result = symbol_task_list[line].strip().split("\n")
                f1.write(line + " | " + result[0] + "\n")
                
                for r in result[1:]:
                    f1.write("    " + r + "\n")
            else:
                f1.write(line + "\n")

# Print Done
print("Done!")
