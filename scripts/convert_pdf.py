#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Markdown 轉換工具的專用執行入口。

這個腳本提供了一個方便的方式來調用 PDF 轉換功能。
使用方法:
python convert_pdf.py [OPTIONS] INPUT_PATH OUTPUT_PATH
例如:
python convert_pdf.py data/my_document.pdf results/my_document.md
"""

import sys
from pathlib import Path

# 將專案根目錄添加到 sys.path 以確保 src 模組可以被找到
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.pdf_converter.cli import cli

if __name__ == "__main__":
    print("--> 啟動 PDF -> Markdown 轉換工具...")
    cli()
