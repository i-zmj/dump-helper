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
print(f"work_dir: {work_dir}")

dump_syms_path = os.path.join(work_dir, "third-party", f"dump_syms{exec_postfix}")
if not os.path.exists(dump_syms_path):
    print(f"\n>>>> ERROR: Tools [{dump_syms_path}] not exists!\n")
    input("Press Enter to exit...")
    exit(1)

def dump_syms(so_path):
    if not os.path.exists(so_path):
        print("\n>>>> ERROR: File [{so_path}] not exists!\n")
        return

    # dump symbols
    so_target_path = os.path.join(f"{work_dir}\\symbols", os.path.basename(so_path))
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
    symbols_folder = os.path.join(f"{work_dir}\\symbols", os.path.basename(so_path), id)
    if not os.path.exists(symbols_folder):
        os.makedirs(symbols_folder)

    target_sym_path = os.path.join(symbols_folder, os.path.basename(so_path) + ".sym")
    if os.path.exists(target_sym_path):
        print("symbols already exists. skip.")
        return

    print(f"move {so_target_path}.sym to {target_sym_path}")
    os.rename(f"{so_target_path}.sym", target_sym_path)



if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: %s <so_path>" % sys.argv[0])
        input("Press Enter to exit...")
        exit(1)

    for so_path in sys.argv[1:]:
        dump_syms(so_path)

    # pause
    input("DONE!\nPress Enter to exit...")