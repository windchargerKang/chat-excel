#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel解析模块

负责读取Excel文件并解析其中的数据结构。
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

class ExcelParser:
    """Excel文件解析器
    
    用于读取Excel文件并解析其中的数据结构，包括表头、数据类型等信息。
    """
    
    def __init__(self, excel_file):
        """初始化Excel解析器
        
        Args:
            excel_file (str): Excel文件路径
        """
        self.excel_file = Path(excel_file)
        if not self.excel_file.exists():
            raise FileNotFoundError(f"找不到Excel文件: {excel_file}")
        
        # 读取Excel文件
        self.excel = pd.ExcelFile(self.excel_file)
    
    def get_sheet_names(self):
        """获取所有工作表名称
        
        Returns:
            list: 工作表名称列表
        """
        return self.excel.sheet_names
    
    def parse_sheet(self, sheet_name, header_row, data_start_row, valid_column_start, valid_column_end=None):
        """解析指定的工作表
        
        Args:
            sheet_name (str): 工作表名称
            header_row (int, optional): 表头所在行索引，默认为0（第一行）
            data_start_row (int, optional): 数据开始行索引，默认为1（第二行）
            valid_column_start (int, optional): 有效列起始索引，默认为0（第一列）
            valid_column_end (int, optional): 有效列结束索引，默认为None（表示所有列）
            
        Returns:
            dict: 包含表头、数据类型和数据的字典
        """
        # 读取整个工作表数据，不指定header
        df_raw = pd.read_excel(self.excel, sheet_name=sheet_name, header=None)
        
        # 将行索引转换为从0开始
        header_row_idx = header_row
        data_start_row_idx = data_start_row
        
        # 从指定行获取表头
        if header_row_idx >= len(df_raw):
            raise ValueError(f"表头行索引 {header_row} 超出了工作表范围")
            
        # 获取指定范围的列
        if valid_column_end is not None and valid_column_end < valid_column_start:
            raise ValueError(f"结束列索引 {valid_column_end} 在起始列索引 {valid_column_start} 之前")
        
        # 提取表头行
        headers_row = df_raw.iloc[header_row_idx]
        
        # 提取指定列范围的表头
        if valid_column_end is None:
            headers = headers_row.iloc[valid_column_start:].tolist()
        else:
            headers = headers_row.iloc[valid_column_start:valid_column_end+1].tolist()
        
        # 处理空列名和重复列名
        headers = [self._handle_empty_column_name(col, idx) for idx, col in enumerate(headers)]
        
        # 处理重复列名
        if len(headers) != len(set(headers)):
            # 添加数字后缀处理重复列名
            seen_columns = {}
            new_headers = []
            for header in headers:
                count = seen_columns.get(header, 0)
                new_header = f"{header}_{count}" if count else header
                new_headers.append(new_header)
                seen_columns[header] = count + 1
            headers = new_headers
        
        # 提取数据部分
        if valid_column_end is None:
            data_df = df_raw.iloc[data_start_row_idx:, valid_column_start:].copy()
        else:
            data_df = df_raw.iloc[data_start_row_idx:, valid_column_start:valid_column_end+1].copy()
        
        # 设置列名
        data_df.columns = headers
        
        # 推断数据类型
        column_types = self._infer_column_types(data_df)
        
        # 处理空值
        data_df = self._handle_null_values(data_df, column_types)
        
        return {
            'headers': headers,
            'types': column_types,
            'data': data_df.to_dict('records')
        }
    
    def parse_all_sheets(self, header_row, data_start_row, valid_column_start, valid_column_end=None):
        """解析所有工作表
        
        Args:
            header_row (int, optional): 表头所在行索引，默认为0（第一行）
            data_start_row (int, optional): 数据开始行索引，默认为1（第二行）
            valid_column_start (str, optional): 有效列起始列名，默认为'A'（第一列）
            valid_column_end (str, optional): 有效列结束列名，默认为None（表示所有列）
            
        Returns:
            dict: 以工作表名称为键，解析结果为值的字典
        """
        result = {}
        for sheet_name in self.get_sheet_names():
            result[sheet_name] = self.parse_sheet(
                sheet_name, 
                header_row=header_row, 
                data_start_row=data_start_row, 
                valid_column_start=valid_column_start, 
                valid_column_end=valid_column_end
            )
        return result
    
    def _clean_column_name(self, column_name):
        """处理列名，保留原始列名
        
        Args:
            column_name (str): 原始列名
            
        Returns:
            str: 处理后的列名
        """
        # 转换为字符串
        column_name = str(column_name)
        
        # 如果为空或仅包含空白字符，使用默认名称
        if pd.isna(column_name) or str(column_name).strip() == '':
            return 'column'
            
        # 保留原始列名
        return str(column_name)
    
    def _infer_column_types(self, df):
        """推断DataFrame中各列的SQL数据类型
        
        Args:
            df (DataFrame): 待推断类型的DataFrame
            
        Returns:
            dict: 列名到SQL类型的映射
        """
        column_types = {}
        
        for column in df.columns:
            # 获取非空值
            non_null_values = df[column].dropna()
            
            if len(non_null_values) == 0:
                # 如果全是空值，默认为TEXT
                column_types[column] = 'TEXT'
                continue
            
            # 检查是否为整数
            if pd.api.types.is_integer_dtype(non_null_values):
                # 检查值的范围确定整数类型
                max_val = non_null_values.max()
                min_val = non_null_values.min()
                
                if min_val >= 0:
                    if max_val <= 255:
                        column_types[column] = 'TINYINT UNSIGNED'
                    elif max_val <= 65535:
                        column_types[column] = 'SMALLINT UNSIGNED'
                    elif max_val <= 4294967295:
                        column_types[column] = 'INT UNSIGNED'
                    else:
                        column_types[column] = 'BIGINT UNSIGNED'
                else:
                    if min_val >= -128 and max_val <= 127:
                        column_types[column] = 'TINYINT'
                    elif min_val >= -32768 and max_val <= 32767:
                        column_types[column] = 'SMALLINT'
                    elif min_val >= -2147483648 and max_val <= 2147483647:
                        column_types[column] = 'INT'
                    else:
                        column_types[column] = 'BIGINT'
            
            # 检查是否为浮点数
            elif pd.api.types.is_float_dtype(non_null_values):
                # 检查精度
                max_decimals = 0
                for val in non_null_values:
                    if isinstance(val, (float, np.float64, np.float32)) and not np.isnan(val):
                        decimals = len(str(val).split('.')[-1])
                        max_decimals = max(max_decimals, decimals)
                
                if max_decimals > 0:
                    column_types[column] = f'DECIMAL(20,{min(max_decimals, 10)})'
                else:
                    column_types[column] = 'DECIMAL(20,0)'
            
            # 检查是否为日期时间
            elif pd.api.types.is_datetime64_dtype(non_null_values):
                # 检查是否包含时间信息
                has_time = False
                for val in non_null_values:
                    if pd.notna(val) and (val.hour != 0 or val.minute != 0 or val.second != 0):
                        has_time = True
                        break
                
                if has_time:
                    column_types[column] = 'DATETIME'
                else:
                    column_types[column] = 'DATE'
            
            # 检查是否为布尔值
            elif pd.api.types.is_bool_dtype(non_null_values):
                column_types[column] = 'BOOLEAN'
            
            # 其他情况作为文本处理
            else:
                # 检查文本长度
                max_length = 0
                for val in non_null_values:
                    if isinstance(val, str):
                        max_length = max(max_length, len(val))
                
                if max_length <= 255:
                    column_types[column] = f'VARCHAR({max(max_length, 50)})'
                else:
                    column_types[column] = 'TEXT'
        
        return column_types
    
    def _handle_null_values(self, df, column_types):
        """处理DataFrame中的空值
        
        Args:
            df (DataFrame): 待处理的DataFrame
            column_types (dict): 列类型映射
            
        Returns:
            DataFrame: 处理后的DataFrame
        """
        # 设置pandas选项以避免FutureWarning
        pd.set_option('future.no_silent_downcasting', True)
        for column, dtype in column_types.items():
            # 对于数值类型，将NaN替换为None（SQL中的NULL）
            if 'INT' in dtype or 'DECIMAL' in dtype:
                df[column] = df[column].apply(lambda x: None if pd.isna(x) else x)
            
            # 对于字符串类型，将NaN替换为空字符串
            elif 'VARCHAR' in dtype or dtype == 'TEXT':
                # 使用更安全的方式处理字符串，避免Series的歧义
                df[column] = df[column].fillna('')
                # 确保值是字符串类型
                df[column] = df[column].astype(str)
            
            # 对于日期类型，保持NaN
            elif dtype in ['DATE', 'DATETIME']:
                df[column] = df[column].apply(lambda x: None if pd.isna(x) else x)
            
            # 对于布尔类型，将NaN替换为False
            elif dtype == 'BOOLEAN':
                # 使用更安全的方式处理布尔值，避免Series的歧义
                df[column] = df[column].fillna(False)
                # 确保值是布尔类型
                df[column] = df[column].astype(bool)
        
        return df
    
    def _handle_empty_column_name(self, column_name, idx):
        """处理空列名
        
        Args:
            column_name (str): 原始列名
            idx (int): 列索引
            
        Returns:
            str: 处理后的列名
        """
        # 如果为空或仅包含空白字符，使用默认名称
        if pd.isna(column_name) or str(column_name).strip() == '':
            return f'column_{idx}'
        
        # 保留原始列名
        return str(column_name)