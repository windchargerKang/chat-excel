# Chat-Excel: Excel转SQL工具

这是一个简单而强大的工具，可以将Excel文件转换为SQL数据库表。它能够自动解析Excel文件的结构，推断数据类型，并生成相应的SQL建表语句和数据插入语句。

## 功能特点

- 支持多种SQL方言（MySQL、SQLite、PostgreSQL）
- 自动推断列数据类型
- 处理多个工作表
- 支持表名前缀
- 智能处理空值和特殊字符
- 命令行界面，易于使用

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

### 1、命令行方式
1. 这将解析Excel文件并将SQL语句输出到控制台。
```bash
python core/chat_excel.py 你的文件.xlsx
```

2. 保存到文件

```bash
python chat_excel.py 你的文件.xlsx -o 输出.sql
```

3. 指定SQL方言

```bash
python chat_excel.py 你的文件.xlsx -d sqlite
```

支持的方言：`mysql`（默认）、`sqlite`、`postgresql`

### 2、页面调试方式

1. 启动调试服务器
```bash
python api.py
```

2. 打开浏览器访问 `http://localhost:8000`

3. 上传Excel文件并查看生成的SQL

## 核心模块

- `core/excel_parser.py`: Excel解析模块
- `core/sql_generator.py`: SQL生成模块
- `core/chat_excel.py`: 命令行入口