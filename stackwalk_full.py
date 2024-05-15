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

stackwalk_path = os.path.join(work_dir, "third-party", f"minidump-stackwalk{exec_postfix}")
if not os.path.exists(stackwalk_path):
    print(f"\n>>>> ERROR: Tools [{stackwalk_path}] not exists!\n")
    input("Press Enter to exit...")
    exit(1)

def stack_walk(dump_path):
    if not os.path.exists(dump_path):
        print("dump file not exists: %s" % dump_path)
        return

    # stack walk
    symbol_path = os.path.join(work_dir, "symbols");
    stack_walk_cmd = f"{stackwalk_path} {dump_path} {symbol_path} --dump > {dump_path}.full.stack"
    print(stack_walk_cmd)
    subprocess.run(stack_walk_cmd, shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: %s <dump_path>" % sys.argv[0])
        exit(1)

    for dump_path in sys.argv[1:]:
        stack_walk(dump_path)

    # pause
    input("Press Enter to exit...")