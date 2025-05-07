#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试脚本：验证Chat-Excel工具的基本功能

这个脚本测试Excel解析器和SQL生成器的基本功能。
"""

import unittest
import pandas as pd
import tempfile
import os
from pathlib import Path

from core.excel_parser import ExcelParser
from core.sql_generator import SQLGenerator

class TestChatExcel(unittest.TestCase):
    """测试Chat-Excel工具的基本功能"""
    
    def setUp(self):
        """创建临时测试文件"""
        # 创建临时目录
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # 创建测试Excel文件
        self.excel_file = self.temp_path / "test_data.xlsx"
        
        # 测试数据
        test_data = {
            "整数列": [1, 2, 3, 4, 5],
            "浮点列": [1.1, 2.2, 3.3, 4.4, 5.5],
            "文本列": ["a", "b", "c", "d", "e"],
            "日期列": pd.date_range(start="2020-01-01", periods=5, freq="D"),
            "布尔列": [True, False, True, False, True]
        }
        
        # 创建DataFrame并保存为Excel
        df = pd.DataFrame(test_data)
        df.to_excel(self.excel_file, sheet_name="测试", index=False)
    
    def tearDown(self):
        """清理临时文件"""
        self.temp_dir.cleanup()
    
    def test_excel_parser(self):
        """测试Excel解析器"""
        parser = ExcelParser(self.excel_file)
        
        # 测试获取工作表名称
        sheet_names = parser.get_sheet_names()
        self.assertIn("测试", sheet_names)
        
        # 测试解析工作表
        sheet_data = parser.parse_sheet("测试")
        
        # 验证解析结果
        self.assertIn('headers', sheet_data)
        self.assertIn('types', sheet_data)
        self.assertIn('data', sheet_data)
        
        # 验证列名清理
        self.assertIn('整数列', sheet_data['headers'])
        
        # 验证类型推断
        self.assertIn('整数列', sheet_data['types'])
        self.assertTrue('INT' in sheet_data['types']['整数列'])
        
        # 验证数据
        self.assertEqual(len(sheet_data['data']), 5)
    
    def test_sql_generator_mysql(self):
        """测试MySQL SQL生成器"""
        parser = ExcelParser(self.excel_file)
        sheet_data = parser.parse_sheet("测试")
        
        generator = SQLGenerator(dialect='mysql')
        
        # 测试生成建表语句
        create_sql = generator.generate_create_table("test_table", sheet_data)
        
        # 验证SQL语句
        self.assertIn("CREATE TABLE", create_sql)
        self.assertIn("`test_table`", create_sql)
        self.assertIn("ENGINE=InnoDB", create_sql)
        
        # 测试生成插入语句
        insert_sql = generator.generate_insert_data("test_table", sheet_data)
        
        # 验证SQL语句
        self.assertIn("INSERT INTO", insert_sql)
        self.assertIn("`test_table`", insert_sql)
    
    def test_sql_generator_sqlite(self):
        """测试SQLite SQL生成器"""
        parser = ExcelParser(self.excel_file)
        sheet_data = parser.parse_sheet("测试")
        
        generator = SQLGenerator(dialect='sqlite')
        
        # 测试生成建表语句
        create_sql = generator.generate_create_table("test_table", sheet_data)
        
        # 验证SQL语句
        self.assertIn("CREATE TABLE", create_sql)
        self.assertIn('"test_table"', create_sql)
        self.assertNotIn("ENGINE=InnoDB", create_sql)  # SQLite不使用ENGINE
        # 验证标准列名格式
        self.assertTrue(all(re.match(r'^[a-z0-9_]+$', h) for h in sheet_data['headers']))
        # 验证数据行数正确性 
        self.assertEqual(len(sheet_data['data']), 5)  # 匹配测试数据实际行数

if __name__ == "__main__":
    unittest.main()