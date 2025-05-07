#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chat-Excel API: 提供RESTful接口将Excel文件转换为SQL语句
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import tempfile
import os
from typing import Dict, List

from core.excel_parser import ExcelParser
from core.sql_generator import SQLGenerator

app = FastAPI()

# 配置静态文件和模板目录
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/convert")
async def convert_excel_to_sql(
    file: UploadFile = File(...),
    dialect: str = "mysql",
    sheet: str = Form(None),
    table_prefix: str = Form(None),
    header_row: int = Form(None),
    data_start_row: int = Form(None),
    valid_column_start: int = Form(None),
    valid_column_end: int = Form(None)
) -> Dict[str, List[str]]:
    """
    将上传的Excel文件转换为SQL语句
    
    参数:
        file: 上传的Excel文件
        dialect: SQL方言(mysql/sqlite/postgresql)
        sheet: 指定工作表名称(可选)
        table_prefix: 表名前缀(可选)
        header_row: 表头所在行索引，从0开始(可选，默认为0)
        data_start_row: 数据开始行索引，从1开始(可选，默认为1)
        valid_column_start: 有效列起始索引，从0开始(可选，默认为0)
        valid_column_end: 有效列结束索引(可选，默认为None表示所有列)
    
    返回:
        {"sql_statements": [SQL语句列表]}
    """
    # 设置默认值
    header_row = 0 if header_row is None else int(header_row)
    data_start_row = 1 if data_start_row is None else int(data_start_row)
    valid_column_start = 0 if valid_column_start is None else int(valid_column_start)
    
    print(f"Received request with parameters: dialect={dialect}, sheet={sheet}, table_prefix={table_prefix}, header_row={header_row}, data_start_row={data_start_row}, valid_column_start={valid_column_start}, valid_column_end={valid_column_end}")
    try:
        # 保存上传文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # 创建解析器和生成器
        parser = ExcelParser(tmp_path)
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
        
        # 删除临时文件
        os.unlink(tmp_path)
        
        return {"sql_statements": sql_statements}
        
    except Exception as e:
        # 确保删除临时文件
        print(f"转换Excel到SQL时出错: {e}")
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)