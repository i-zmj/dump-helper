# Android平台Breakpad生成的dump文件解析脚本

本项目用于快速解析dump文件。
当前仅支持Linux平台，其他平台待完善。

## 运行原理

1. 利用dump_syms工具生成sym文件。
2. 利用minidump_stackwalk工具，输入dmp和sym文件，生成.stack（.raw）文件。

## 使用方法

1. 将so，dmp文件直接拖拽到dump_helper上，即可解析。
   a. dump-helper将优先解析so文件，生成sym文件。
   b. dump-helper将解析dmp文件，生成.stack和.raw文件。
2. 将一个目录直接拖拽到dump_helper上，会递归获取里面所有的文件。进行解析。

## 特性

- 合并dump_syms和minidump_stackwalk，可根据文件后缀识别该如何处理文件。

## 第三方库

### rust-minidump/rust-minidump

Git：https://github.com/rust-minidump/rust-minidump.git 
> Version 0.24.0 (2025-01-03)

### mozilla/dump_syms

Git: https://github.com/mozilla/dump_syms.git
> 2.3.4 - 2024-09-06
