#!/usr/env python3
# -*- coding: utf-8 -*-

import os

if __name__ == "__main__":
    # 利用pyinstaller将脚本打包成可执行文件
    os.system("pyinstaller -F dump_syms.py")
    os.system("pyinstaller -F stackwalk.py")
    os.system("pyinstaller -F stackwalk_full.py")