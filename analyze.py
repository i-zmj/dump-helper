#!/usr/bin/env python3

# This script should been run with python3
import sys
import os
import subprocess
import re
import threading
import configparser
import time

progressed_list_value = 0
lock = threading.Lock()

# minidump_stackwalk
if sys.platform == "win32":
    minidump_stackwalk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minidump-stackwalk.exe")
else:
    minidump_stackwalk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minidump-stackwalk")

# addr2line
if sys.platform == "win32":
    addr2line_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addr2line.exe")
else:
    addr2line_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "addr2line")

def get_lines_from_address(lib_path, dict, line):
    words = re.findall(r'\blib\w+\.so\b', line)
    line_lib_path = lib_path + words[0]
    lib_address = line.split("0x")[1].split(" ")[0].strip()

    # Run addr2line
    ret = subprocess.run(addr2line_path + " -e " + line_lib_path + " -f -C -p -i " + lib_address, shell=True, stdout=subprocess.PIPE)
    dict[line] = ret.stdout.decode('utf-8')

    # Update progressed_list_value
    global progressed_list_value

    with lock:
        progressed_list_value += 1
        print("\rProgressed: " + str(progressed_list_value) + "/" + str(len(dict)), end='')

if sys.version_info[0] < 3:
    print("This script should been run with python3")

# Read args
if len(sys.argv) < 3:
    # If IniConfig file [cache.ini] exists and conf[lib_path] is available
    if os.path.exists(".cache.ini"):
        config = configparser.ConfigParser()
        config.read(".cache.ini")
        if sys.platform in config and "lib_path" in config[sys.platform]:
            lib_path = config[sys.platform]["lib_path"]
            if lib_path[-1] != "/":
                lib_path += "/"
            print("Use lib_path from .cache.ini: " + lib_path)
        else:
            print("Read .cache.ini failed. [conf/lib_path] is NOT available!")
            print("Please run script with <lib_path> again!")
            sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 analyse.py <dump_file_path> <lib_path>")
        sys.exit(1)
else:
    lib_path = sys.argv[2]
    config = configparser.ConfigParser()
    config.read(".cache.ini")
    # Create key and value
    if sys.platform not in config:
        config[sys.platform] = {}
    config[sys.platform]["lib_path"] = lib_path
    with open(".cache.ini", "w") as configfile:
        config.write(configfile)


dump_file_path = sys.argv[1]

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

# Add txt extension to dump file
brief_file_path = dump_file_path + ".txt"
full_file_path = dump_file_path + ".full"

symbol_task_list = {}

# Run minidump_stackwalk
print("Run minidump_stackwalk...", end='')

pre_run_time = time.time()
ret = subprocess.run(minidump_stackwalk_path + " " + dump_file_path + " " + lib_path, shell=True, stdout=subprocess.PIPE)
print("Done! (" + str(round(time.time() - pre_run_time, 2)) + "s)")

lines = ret.stdout.decode('utf-8').split("\n")

# Find the line that contains the lib name and address
for line in lines:

    if (".lib" in line or ".so" in line) and "0x" in line:
        # Extract lib name and address
        words = re.findall(r'\blib\w+\.so\b', line)
        if len(words) > 0:
            line_lib_path = lib_path + words[0]

            if os.path.exists(line_lib_path):

                if not line in symbol_task_list:
                    # Save line into dictionary
                    symbol_task_list[line] = "NONE"

print("Found available " + str(len(symbol_task_list)) + " lines.")

# Convert symbol task with multi thread
# Create 8 threads

pre_run_time = time.time()

# Multithread
threads = []
for task in symbol_task_list:
    t = threading.Thread(target=get_lines_from_address, args=(lib_path, symbol_task_list, task))
    threads.append(t)
    t.start()
    
# Wait all threads
for t in threads:
    t.join()

print("\nDone! (" + str(round(time.time() - pre_run_time, 2)) + "s)")

thread_count = 0
print_stack_count = 0

print("============= Recent Stack =============")

# Write final file
with open(brief_file_path, 'w') as brief_file:

    with open(full_file_path, 'w') as full_file:

        for line in lines:

            # Print first thread's stack(Mostly crashed thread)
            if "Thread" in line:
                thread_count += 1

            if ".so +" in line or ".lib +" in line:
                print_stack_count += 1

            if "Found by " in line or "fp = 0x" in line or "sp = 0x" in line or "0 = 0x" in line or "2 = 0x" in line or "4 = 0x" in line or "6 = 0x" in line or "8 = 0x" in line or "pc = 0x" in line:
                full_file.write(line + "\n")

            else:
                if line in symbol_task_list:
                    result = symbol_task_list[line].strip().split("\n")
                    
                    brief_file.write(line + " | " + result[0] + "\n")
                    full_file.write(line + " | " + result[0] + "\n")
                    
                    # Print some stacks on console
                    if thread_count == 1 and print_stack_count < 10:
                        print(line + " | " + result[0])

                    for r in result[1:]:
                        brief_file.write("    " + r + "\n")
                        full_file.write("    " + r + "\n")

                        # Print some stacks on console
                        if thread_count == 1 and print_stack_count < 10:
                            print("    " + r)
                else:
                    brief_file.write(line + "\n")
                    full_file.write(line + "\n")

                    # Print some stacks on console
                    if thread_count == 1 and print_stack_count < 10:
                        print(line)

print("============= Recent Stack =============")

print("Output results >> " + brief_file_path)

# Print Done
print("Done!")
