# Android平台Breakpad生成的dump文件解析脚本

本项目用于快速解析dump文件。
当前仅支持Linux平台，其他平台待完善。

## 第三方库

### rust-minidump

Git：https://github.com/rust-minidump/rust-minidump.git 
Version 0.21.1 (2024-03-01)

### addr2line

msys2
Ubuntu

## 准备环境

### 1. 安装python3

Ubuntu建议使用apt进行python的安装

```bash
sudo apt install -y python3`
```

## 运行

由于addr2line比较卡顿。对于比较大的文件，建议使用多线程的方式进行解析。
本工具支持多线程

基本运行方式：
```bash
python3 analyze.py <dump_file_path> <lib_path>
```

内部执行命令：
- 使用minidump_stackwalk命令读取堆栈信息。
- 筛选信息中包含.lib和.so的内容。
- 使用addr2line命令将.lib和.so和地址信息，转换成堆栈信息。
