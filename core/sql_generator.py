#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL生成模块

负责将解析后的Excel数据转换为SQL建表语句和数据插入语句。
"""

import re
import pandas as pd
from datetime import datetime

class SQLGenerator:
    """SQL生成器
    
    用于生成SQL建表语句和数据插入语句。
    """
    
    def __init__(self, dialect='mysql', table_prefix=None):
        """初始化SQL生成器
        
        Args:
            dialect (str): SQL方言，支持'mysql', 'sqlite', 'postgresql'
            table_prefix (str, optional): 表名前缀
        """
        self.dialect = dialect.lower()
        self.table_prefix = table_prefix or ''
        
        # 不同方言的类型映射
        self.type_mappings = {
            'mysql': {
                'TINYINT': 'TINYINT',
                'SMALLINT': 'SMALLINT',
                'INT': 'INT',
                'BIGINT': 'BIGINT',
                'DECIMAL': 'DECIMAL',
                'VARCHAR': 'VARCHAR',
                'TEXT': 'TEXT',
                'DATE': 'DATE',
                'DATETIME': 'DATETIME',
                'BOOLEAN': 'BOOLEAN'
            },
            'sqlite': {
                'TINYINT': 'INTEGER',
                'SMALLINT': 'INTEGER',
                'INT': 'INTEGER',
                'BIGINT': 'INTEGER',
                'DECIMAL': 'REAL',
                'VARCHAR': 'TEXT',
                'TEXT': 'TEXT',
                'DATE': 'TEXT',
                'DATETIME': 'TEXT',
                'BOOLEAN': 'INTEGER'
            },
            'postgresql': {
                'TINYINT': 'SMALLINT',
                'SMALLINT': 'SMALLINT',
                'INT': 'INTEGER',
                'BIGINT': 'BIGINT',
                'DECIMAL': 'NUMERIC',
                'VARCHAR': 'VARCHAR',
                'TEXT': 'TEXT',
                'DATE': 'DATE',
                'DATETIME': 'TIMESTAMP',
                'BOOLEAN': 'BOOLEAN'
            }
        }
    
    def generate_create_table(self, table_name, sheet_data):
        """生成建表SQL语句
        
        Args:
            table_name (str): 表名
            sheet_data (dict): 工作表数据，包含headers和types
            
        Returns:
            str: 建表SQL语句
        """
        headers = sheet_data['headers']
        types = sheet_data['types']
        
        # 使用原始工作表名作为表名
        safe_table_name = table_name
        # 清理表名，使其符合SQL规范
        safe_table_name = self._sanitize_identifier(safe_table_name)
        
        # 确保表前缀不会覆盖原始表名
        if self.table_prefix:
            prefixed_table_name = f"{self.table_prefix}_{safe_table_name}"
        else:
            prefixed_table_name = safe_table_name
        
        # 生成列定义
        columns = []
        for header in headers:
            sql_type = self._map_type(types[header])
            # 直接使用原始列名，不进行额外处理
            columns.append(f"    {self._quote_identifier(header)} {sql_type}")
        
        # 生成建表语句
        if self.dialect == 'mysql':
            create_sql = f"CREATE TABLE IF NOT EXISTS {self._quote_identifier(prefixed_table_name)} (\n"
            create_sql += ",\n".join(columns)
            create_sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
        elif self.dialect == 'sqlite':
            create_sql = f"CREATE TABLE IF NOT EXISTS {self._quote_identifier(prefixed_table_name)} (\n"
            create_sql += ",\n".join(columns)
            create_sql += "\n);"
        elif self.dialect == 'postgresql':
            create_sql = f"CREATE TABLE IF NOT EXISTS {self._quote_identifier(prefixed_table_name)} (\n"
            create_sql += ",\n".join(columns)
            create_sql += "\n);"
        
        return create_sql
    
    def generate_insert_data(self, table_name, sheet_data):
        """生成数据插入SQL语句
        
        Args:
            table_name (str): 表名
            sheet_data (dict): 工作表数据，包含headers和data
            
        Returns:
            str: 数据插入SQL语句
        """
        headers = sheet_data['headers']
        data = sheet_data['data']
        types = sheet_data['types']
        
        # 使用原始工作表名作为表名
        safe_table_name = table_name
        # 清理表名，使其符合SQL规范
        safe_table_name = self._sanitize_identifier(safe_table_name)
        
        # 确保表前缀不会覆盖原始表名
        if self.table_prefix:
            prefixed_table_name = f"{self.table_prefix}_{safe_table_name}"
        else:
            prefixed_table_name = safe_table_name
        
        # 生成列名部分
        # 直接使用原始列名，不进行额外处理
        columns_str = ", ".join([self._quote_identifier(h) for h in headers])
        
        # 生成插入语句
        if not data:
            return f"-- 没有数据需要插入到表 {prefixed_table_name}"
        
        insert_statements = []
        
        # 根据方言生成不同的插入语句
        if self.dialect == 'mysql':
            insert_sql = f"INSERT INTO {self._quote_identifier(prefixed_table_name)} ({columns_str}) VALUES\n"
            
            values = []
            for row in data:
                row_values = []
                for header in headers:
                    value = row.get(header)
                    sql_type = types[header]
                    formatted_value = self._format_value(value, sql_type)
                    row_values.append(formatted_value)
                
                values.append(f"({', '.join(row_values)})")
            
            # 分批插入，每500行一批
            batch_size = 500
            for i in range(0, len(values), batch_size):
                batch = values[i:i+batch_size]
                insert_statements.append(insert_sql + ",\n".join(batch) + ";")
        
        elif self.dialect in ['sqlite', 'postgresql']:
            # SQLite和PostgreSQL每行一个INSERT语句
            for row in data:
                row_values = []
                for header in headers:
                    value = row.get(header)
                    sql_type = types[header]
                    formatted_value = self._format_value(value, sql_type)
                    row_values.append(formatted_value)
                
                values_str = ", ".join(row_values)
                insert_statements.append(f"INSERT INTO {self._quote_identifier(prefixed_table_name)} ({columns_str}) VALUES ({values_str});")
        
        return "\n".join(insert_statements)
    
    def _map_type(self, excel_type):
        """将Excel解析的类型映射到对应方言的SQL类型
        
        Args:
            excel_type (str): Excel解析的类型
            
        Returns:
            str: 对应方言的SQL类型
        """
        # 提取基本类型和参数
        match = re.match(r'([A-Z]+)(?:\(([^)]+)\))?', excel_type)
        if not match:
            return 'TEXT'  # 默认类型
        
        base_type = match.group(1)
        params = match.group(2)
        
        # 获取当前方言的类型映射
        dialect_mapping = self.type_mappings.get(self.dialect, self.type_mappings['mysql'])
        
        # 映射基本类型
        sql_type = dialect_mapping.get(base_type, 'TEXT')
        
        # 添加参数（如果有）
        if params and sql_type in ['VARCHAR', 'DECIMAL', 'NUMERIC']:
            return f"{sql_type}({params})"
        
        return sql_type
    
    def _sanitize_identifier(self, identifier):
        """清理标识符，使其符合SQL规范
        
        Args:
            identifier (str): 原始标识符
            
        Returns:
            str: 清理后的标识符
        """
        if not identifier:
            return 'column'
            
        # 仅替换SQL中的特殊字符为下划线
        clean_id = re.sub(r'[\\\"\'\`\;\,\=\*\%\<\>\|\?\!\@\#\$\^\&\*\(\)\+\[\]\{\}]', '_', str(identifier))
        
        # 确保不以数字开头
        if clean_id and clean_id[0].isdigit():
            clean_id = 'f_' + clean_id
            
        return clean_id
    
    def _quote_identifier(self, identifier):
        """根据SQL方言对标识符进行引用
        
        Args:
            identifier (str): 标识符
            
        Returns:
            str: 引用后的标识符
        """
        if self.dialect == 'mysql':
            return f"`{identifier}`"
        elif self.dialect == 'postgresql':
            return f'"{identifier}"'
        else:  # sqlite
            return f'"{identifier}"'
    
    def _format_value(self, value, sql_type):
        """格式化值，使其符合SQL语法
        
        Args:
            value: 原始值
            sql_type (str): SQL类型
            
        Returns:
            str: 格式化后的值
        """
        if value is None:
            return 'NULL'
        
        # 根据SQL类型格式化值
        if 'INT' in sql_type or sql_type == 'BOOLEAN':
            # 布尔值转换为0/1
            if isinstance(value, bool) or (hasattr(value, 'dtype') and pd.api.types.is_bool_dtype(value.dtype)):
                # 安全地处理pandas Series和numpy array
                if hasattr(value, 'item'):
                    try:
                        return '1' if value.item() else '0'
                    except (ValueError, TypeError):
                        return '0'
                else:
                    return '1' if value else '0'
            # 确保是整数
            try:
                return str(int(value))
            except (ValueError, TypeError):
                return '0'
        
        elif 'DECIMAL' in sql_type or sql_type == 'REAL' or sql_type == 'NUMERIC':
            # 确保是浮点数
            try:
                return str(float(value))
            except (ValueError, TypeError):
                return '0.0'
        
        elif sql_type in ['DATE', 'DATETIME', 'TIMESTAMP']:
            # 日期时间格式化
            if isinstance(value, datetime):
                if sql_type == 'DATE':
                    return f"'{value.strftime('%Y-%m-%d')}'"
                else:
                    return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
            else:
                return "'0000-00-00'"
        
        else:  # VARCHAR, TEXT等字符串类型
            # 转义单引号并用单引号包围
            if isinstance(value, str):
                escaped_value = value.replace("'", "''")
                return f"'{escaped_value}'"
            else:
                return f"'{str(value)}'"