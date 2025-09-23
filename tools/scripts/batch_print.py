#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量列印腳本 - 自動開啟所有列印頁面
"""

import webbrowser
import time
import os
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def open_print_pages():
    """開啟所有列印頁面"""
    
    # 檔案清單
    files = [
        "print_REA-ACT-5.html",
        "print_REA-ACT-29.html", 
        "print_REA-RULES-5.html",
        "print_REA-RULES-21.html",
        "print_REA-RULES-25.html",
        "print_REA-RULES-25-1.html",
        "print_CMCA-24.html",
        "print_CMCA-25.html",
        "print_FTA-11.html",
        "print_FTA-47.html",
        "print_CPA-3.html",
        "print_combined.html"
    ]
    
    base_path = "file:///home/bheadwei/LegalStatuteAnalysis_V2/output/print/"
    
    logger.info("開始開啟列印頁面...")
    
    for i, file in enumerate(files, 1):
        url = base_path + file
        logger.info(f"開啟頁面 {i}/{len(files)}: {file}")
        
        # 開啟瀏覽器
        webbrowser.open(url)
        
        # 等待頁面載入
        time.sleep(3)
    
    logger.info("所有列印頁面已開啟！")
    logger.info("請按照瀏覽器列印指南進行PDF生成。")

if __name__ == "__main__":
    open_print_pages()
