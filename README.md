# Android平台Breakpad生成的dump文件解析脚本

本项目用于快速解析dump文件。
当前仅支持Linux平台，其他平台待完善。

## 运行原理

1. 利用dump_syms工具生成sym文件。
2. 利用dmp和sym文件，生成.stack（.full.stack）文件。

## 使用方法

1. 生成sym文件。
   a. 将so, lib文件拖拽到dump_syms.exe文件上，生成sym文件。（可批量拖拽）
   b. 工具生成的sym将会被自动移动到symbols目录下。 目录结构为/symbols/{so文件名}/{so id}/
2. 解析dump文件。
   a. 将dump文件拖拽到stackwalk.exe文件上，解析dump文件。
   b. 解析结果将保存到.stack文件中。
   c. 堆栈的前20行关键信息，将被输出到控制台。

## V2.0 特性

- 移除addr2line方式进行代码行解析，采用dump_syms工具分析so文件的方式，建立符号表数据库。
- 使用minidump-stackwalk，输入dmp和sym文件，直接输出解析后的堆栈信息。
- 提供dump_syms脚本，用于生成sym文件。

## 第三方库

### rust-minidump/rust-minidump

Git：https://github.com/rust-minidump/rust-minidump.git 
Version 0.21.1 (2024-03-01)

### mozilla/dump_syms

Git: https://github.com/mozilla/dump_syms.git
Version 2.3.1