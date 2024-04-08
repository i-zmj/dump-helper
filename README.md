# Android平台Breakpad生成的dump文件解析脚本

本项目用于快速解析dump文件。
当前仅支持Linux平台，其他平台待完善。

## 准备环境

### 1.安装编译breakpad

1. 下载准备好的库
```bash
git clone https://gitee.com/girakoo/breadpad.git
```

2. 编译库
```bash
./configure && make -j12  
```

3. 安装库
```bash
sudo make install
```

**更新记录：**

[2024/04/08] 更新breakpad和lss库

- breakpad: https://github.com/google/breakpad
- lss: https://chromium.googlesource.com/linux-syscall-support/

### 2. 安装python3

Ubuntu建议使用apt进行python的安装

```bash
sudo apt install -y python3`
```

## 运行

由于addr2line比较卡顿。对于比较大的文件，建议使用多线程的方式进行解析。
本工具支持多线程

基本运行方式：
```bash
python3 analysis.py <dump_file_path> <lib_path>
```

内部执行命令：
- 使用minidump_stackwalk命令读取堆栈信息。
- 使用addr2line命令解析堆栈信息。