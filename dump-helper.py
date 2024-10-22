#!/usr/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess


def colorful_print(level, msg):
    if level == 'error':
        print(f"\033[31m{msg}\033[0m")
    elif level == 'warning':
        print(f"\033[33m{msg}\033[0m")
    elif level == 'info':
        print(f"\033[32m{msg}\033[0m")
    else:
        print(msg)

colorful_print('info', "********************************************************")
colorful_print('info', "* Project: https://gitee.com/izmj/dump_helper          *")
colorful_print('info', "* Current Version: v2.3                                *")
colorful_print('info', "********************************************************")

work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

if sys.platform == "win32":
    exec_postfix = ".exe" 
    exec_path = "third-party/x86_64/win32"
elif sys.platform == "linux":
    exec_postfix = ""
    exec_path = "third-party/x86_64/linux"
elif sys.platform == "darwin":
    exec_postfix = ""
    exec_path = "third-party/x86_64/darwin"
else:
    colorful_print('error', f"Unsupported platform: {sys.platform}")
    input("Press Enter to exit...")
    exit(1)

# If current script is not end with .py
if not sys.argv[0].endswith(".py"):
    exec_path = 'res';

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Check dump_syms
dump_syms_path = get_resource_path(os.path.join(exec_path, f"dump_syms{exec_postfix}"))
if not os.path.exists(dump_syms_path):
    colorful_print('error', f">>>> ERROR: Tools [{dump_syms_path}] not exists!")
    input("Press Enter to exit...")
    exit(1)

# Check stackwalk
stackwalk_path = get_resource_path(os.path.join(exec_path , f"minidump-stackwalk{exec_postfix}"))
if not os.path.exists(stackwalk_path):
    colorful_print('error', f">>>> ERROR: Tools [{stackwalk_path}] not exists!")
    input("Press Enter to exit...")
    exit(1)

def dump_syms(so_path):
    if not os.path.exists(so_path):
        colorful_print('error', f">>>> ERROR: File [{so_path}] not exists!")
        return

    # dump symbols
    so_target_path = os.path.join(work_dir, "symbols", os.path.basename(so_path))
    if not os.path.exists(so_target_path):
        os.makedirs(so_target_path)

    dump_syms_cmd = f"{dump_syms_path} {so_path} > {so_target_path}.sym"
    
    subprocess.run(dump_syms_cmd, shell=True)

    # read id of symbols
    with open(f"{so_target_path}.sym", "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            colorful_print('error', "dump symbols failed")
            return
        id = lines[0].split()[3]
        colorful_print('info', f"symbol id: {id}\n")

    # move symbols to symbols folder
    symbols_folder = os.path.join(work_dir, "symbols", os.path.basename(so_path), id)
    if not os.path.exists(symbols_folder):
        os.makedirs(symbols_folder)

    target_sym_path = os.path.join(symbols_folder, os.path.basename(so_path) + ".sym")
    if os.path.exists(target_sym_path):
        colorful_print('warning', "symbols already exists! skip.")
        return

    os.rename(f"{so_target_path}.sym", target_sym_path)

def stack_walk(dump_path):
    if not os.path.exists(dump_path):
        colorful_print('error', "dump file not exists: %s" % dump_path)
        return

    if os.path.exists(dump_path + ".stack"):
        colorful_print('warning', "stack walk already exists! skip.")
        return

    # stack walk
    symbol_path = os.path.join(work_dir, "symbols");
    stack_walk_cmd = f"{stackwalk_path} {dump_path} {symbol_path} > {dump_path}.stack"
    subprocess.run(stack_walk_cmd, shell=True)

    stack_walk_cmd = f"{stackwalk_path} {dump_path} {symbol_path} --dump > {dump_path}.raw"
    subprocess.run(stack_walk_cmd, shell=True)

    colorful_print('info', "********************* Recent Stack *********************")

    # read stack
    with open(f"{dump_path}.stack", "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            colorful_print('error', "stack walk failed!")
            return
        
        print_lines = 20

        # print 20 lines
        for line in lines:
            line = line.strip()
            if ".so" in line or ".lib" in line or "Thread" in line or "Crash" in line:
                print(line)
                print_lines -= 1
                if print_lines == 0:
                    break

    colorful_print('info', "********************************************************")

if __name__ == "__main__":

    args = []
    if len(sys.argv) < 2:
        # Wait user input library or dump file to process
        while True:
            file = input("Please input library or dump file(one by one):")
            if file == "":
                break

            args.append(file)
    else:
        args = sys.argv[1:]

    if len(args) == 0:
        colorful_print("error", "No libraries or dump files input. Exit.")
        exit(1)

    # If put a directory, get all files in it.
    for dir_path in args:
        if os.path.isdir(dir_path):
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    args.append(os.path.join(root, file))

    # Parse libraries
    for so_path in args:
        # Fix param that endsWith space
        so_path = so_path.strip()
        if so_path.endswith(".so") or so_path.endswith(".dll") or so_path.endswith(".lib"):
            colorful_print('info', "********************* Dump Symbol **********************")
            colorful_print("debug", f"Processing library {so_path}...")
            dump_syms(so_path)

    # Parse dump files
    for dump_path in args:
        # Fix param that endsWith space
        dump_path = dump_path.strip()
        if dump_path.endswith(".dmp") or dump_path.endswith(".minidump"):
            colorful_print('info', "********************** Stack Walk **********************")
            colorful_print("debug", f"Processing dump file {dump_path}...")
            stack_walk(dump_path)

    # pause
    input("Press Enter to exit...")