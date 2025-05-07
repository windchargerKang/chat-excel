#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
示例脚本：演示如何使用Chat-Excel工具

这个脚本创建一个示例Excel文件，然后使用Chat-Excel工具将其转换为SQL。
"""

import os
import pandas as pd
import subprocess
from pathlib import Path

# 创建examples目录（如果不存在）
examples_dir = Path(__file__).parent
examples_dir.mkdir(exist_ok=True)

# 示例Excel文件路径
excel_file = examples_dir / "sample_data.xlsx"

def create_sample_excel():
    """创建一个示例Excel文件，包含两个工作表"""
    # 创建示例数据 - 员工表
    employees_data = {
        "员工ID": [1, 2, 3, 4, 5],
        "姓名": ["张三", "李四", "王五", "赵六", "钱七"],
        "部门": ["技术部", "市场部", "财务部", "人事部", "技术部"],
        "入职日期": pd.date_range(start="2020-01-01", periods=5, freq="M"),
        "薪资": [10000.50, 12000.75, 9000.25, 8500.00, 11000.00],
        "是否在职": [True, True, False, True, True]
    }
    
    # 创建示例数据 - 部门表
    departments_data = {
        "部门ID": [1, 2, 3, 4],
        "部门名称": ["技术部", "市场部", "财务部", "人事部"],
        "部门主管": ["张三", "李四", "王五", "赵六"],
        "人数": [20, 15, 10, 5],
        "预算": [1000000, 800000, 500000, 300000]
    }
    
    # 创建DataFrame
    employees_df = pd.DataFrame(employees_data)
    departments_df = pd.DataFrame(departments_data)
    
    # 创建Excel文件，包含两个工作表
    with pd.ExcelWriter(excel_file) as writer:
        employees_df.to_excel(writer, sheet_name="员工", index=False)
        departments_df.to_excel(writer, sheet_name="部门", index=False)
    
    print(f"示例Excel文件已创建: {excel_file}")

def convert_to_sql():
    """使用Chat-Excel工具将示例Excel文件转换为SQL"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    
    # 输出SQL文件路径
    sql_file = examples_dir / "sample_data.sql"
    
    # 构建命令
    cmd = [
        "python", 
        str(project_root / "chat_excel.py"),
        str(excel_file),
        "-o", str(sql_file),
        "-d", "mysql",
        "-p", "sample_"
    ]
    
    # 执行命令
    print("正在转换Excel文件为SQL...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"转换成功！SQL文件已保存到: {sql_file}")
        print("\n生成的SQL文件内容预览:")
        with open(sql_file, "r", encoding="utf-8") as f:
            content = f.read(1000)  # 只读取前1000个字符作为预览
            print(content + ("..." if len(content) >= 1000 else ""))
    else:
        print("转换失败！错误信息:")
        print(result.stderr)

def main():
    # 创建示例Excel文件
    create_sample_excel()
    
    # 转换为SQL
    convert_to_sql()
    
    print("\n示例演示完成！")
    print("你可以查看生成的示例文件，并尝试使用不同的参数运行chat_excel.py")

if __name__ == "__main__":
    main()