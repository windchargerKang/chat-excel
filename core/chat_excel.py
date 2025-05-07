#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chat-Excel: 将Excel文件转换为SQL库表

这个工具可以读取Excel文件，并将其转换为SQL建表语句和数据插入语句。
"""

import os
import sys
import pandas as pd
import click
from pathlib import Path
from dotenv import load_dotenv

from excel_parser import ExcelParser
from sql_generator import SQLGenerator

# 加载环境变量
load_dotenv()

@click.command()
@click.argument('excel_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='输出SQL文件的路径')
@click.option('--dialect', '-d', type=click.Choice(['mysql', 'sqlite', 'postgresql']), default='mysql', help='SQL方言')
@click.option('--sheet', '-s', help='指定要处理的工作表名称，默认处理所有工作表')
@click.option('--table-prefix', '-p', help='表名前缀')
@click.option('--header-row', '-hr', type=int, default=1, help='表头所在行索引，从1开始')
@click.option('--data-start-row', '-dr', type=int, default=2, help='数据起始行索引，从2开始')
@click.option('--valid-column-start', '-cs', type=str, default='A', help='有效列起始列名，从A列开始')
@click.option('--valid-column-end', '-ce', type=str, help='有效列结束列名，默认为None表示所有列')
def main(excel_file, output, dialect, sheet, table_prefix, header_row, data_start_row, valid_column_start, valid_column_end):
    """将Excel文件转换为SQL库表。

    EXCEL_FILE: Excel文件的路径
    """
    try:
        # 创建解析器和生成器
        parser = ExcelParser(excel_file)
        generator = SQLGenerator(dialect=dialect, table_prefix=table_prefix)
        
        # 解析Excel文件
        if sheet:
            sheets_data = {sheet: parser.parse_sheet(
                sheet, 
                header_row=header_row, 
                data_start_row=data_start_row, 
                valid_column_start=valid_column_start, 
                valid_column_end=valid_column_end
            )}
        else:
            sheets_data = parser.parse_all_sheets(
                header_row=header_row, 
                data_start_row=data_start_row, 
                valid_column_start=valid_column_start, 
                valid_column_end=valid_column_end
            )
        
        # 生成SQL语句
        sql_statements = []
        for sheet_name, data in sheets_data.items():
            table_name = f"{table_prefix or ''}{sheet_name}"
            create_table = generator.generate_create_table(table_name, data)
            insert_data = generator.generate_insert_data(table_name, data)
            
            sql_statements.append(create_table)
            sql_statements.append(insert_data)
        
        # 合并所有SQL语句
        all_sql = '\n\n'.join(sql_statements)
        
        # 输出SQL语句
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(all_sql)
            click.echo(f"SQL已保存到 {output}")
        else:
            click.echo(all_sql)
            
        click.echo("转换完成！")
        
    except Exception as e:
        import traceback
        error_msg = f"错误: {str(e)}\n\n详细错误信息:\n{traceback.format_exc()}"
        click.echo(error_msg, err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()