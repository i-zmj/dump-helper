#!/usr/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

if sys.platform == "win32":
    exec_postfix = ".exe" 
else: 
    exec_postfix = ""

work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

print("********************************************************")
print("* Project: https://gitee.com/izmj/dump_helper          *")
print("* Current Version: v2.2                                *")
print("********************************************************")

# Check dump_syms
dump_syms_path = os.path.join(work_dir, f"dump_syms{exec_postfix}")
if not os.path.exists(dump_syms_path):
    print(f"\n>>>> ERROR: Tools [{dump_syms_path}] not exists!\n")
    input("Press Enter to exit...")
    exit(1)

# Check stackwalk
stackwalk_path = os.path.join(work_dir, f"minidump-stackwalk{exec_postfix}")
if not os.path.exists(stackwalk_path):
    print(f"\n>>>> ERROR: Tools [{stackwalk_path}] not exists!\n")
    input("Press Enter to exit...")
    exit(1)

def dump_syms(so_path):
    if not os.path.exists(so_path):
        print("\n>>>> ERROR: File [{so_path}] not exists!\n")
        return

    # dump symbols
    so_target_path = os.path.join(work_dir, "symbols", os.path.basename(so_path))
    if not os.path.exists(so_target_path):
        print(f"create directory: {so_target_path}")
        os.makedirs(so_target_path)

    dump_syms_cmd = f"{dump_syms_path} {so_path} > {so_target_path}.sym"
    print(dump_syms_cmd)
    subprocess.run(dump_syms_cmd, shell=True)

    # read id of symbols
    with open(f"{so_target_path}.sym", "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            print("dump symbols failed")
            return
        id = lines[0].split()[3]
        print("\n============= Symbol ID =============")
        print(f"symbol id: {id}")
        print("=====================================")

    # move symbols to symbols folder
    symbols_folder = os.path.join(work_dir, "symbols", os.path.basename(so_path), id)
    if not os.path.exists(symbols_folder):
        os.makedirs(symbols_folder)

    target_sym_path = os.path.join(symbols_folder, os.path.basename(so_path) + ".sym")
    if os.path.exists(target_sym_path):
        print("symbols already exists. skip.")
        return

    print(f"move {so_target_path}.sym to {target_sym_path}")
    os.rename(f"{so_target_path}.sym", target_sym_path)

def stack_walk(dump_path):
    if not os.path.exists(dump_path):
        print("dump file not exists: %s" % dump_path)
        return

    # stack walk
    symbol_path = os.path.join(work_dir, "symbols");
    stack_walk_cmd = f"{stackwalk_path} {dump_path} {symbol_path} > {dump_path}.stack"
    print(stack_walk_cmd)
    subprocess.run(stack_walk_cmd, shell=True)

    stack_walk_cmd = f"{stackwalk_path} {dump_path} {symbol_path} --dump > {dump_path}.raw"
    print(stack_walk_cmd)
    subprocess.run(stack_walk_cmd, shell=True)

    print("\n============= Recent Stack =============")

    # read stack
    with open(f"{dump_path}.stack", "r") as f:
        lines = f.readlines()
        if len(lines) < 2:
            print("stack walk failed")
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <so_path>" % sys.argv[0])
        print("Usage: %s <dump_path>" % sys.argv[0])
        print("Usage: %s <so_path> <dump_path>" % sys.argv[0])

        input("Press Enter to exit...")
        exit(1)

    # Parse libraries
    for so_path in sys.argv[1:]:
        if so_path.endswith(".so") or so_path.endswith(".dll") or so_path.endswith(".lib"):
            dump_syms(so_path)

    # Parse dump files
    for dump_path in sys.argv[1:]:
        if dump_path.endswith(".dmp") or dump_path.endswith(".minidump"):
            stack_walk(dump_path)

    # pause
    input("Press Enter to exit...")