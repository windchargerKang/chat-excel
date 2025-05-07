#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chat-excel",
    version="0.1.0",
    author="Chat-Excel Team",
    author_email="example@example.com",
    description="将Excel文件转换为SQL库表的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/chat-excel",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "python-dotenv>=0.19.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "chat-excel=chat_excel:main",
        ],
    },
)