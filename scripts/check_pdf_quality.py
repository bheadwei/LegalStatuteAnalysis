#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF品質檢查腳本 - 驗證PDF文字顯示是否正常
"""

import os
import subprocess
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_pdf_text_content(pdf_file):
    """檢查PDF是否包含可讀文字"""
    try:
        # 使用pdftotext提取文字內容
        result = subprocess.run(['pdftotext', pdf_file, '-'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            text_content = result.stdout.strip()
            if text_content:
                logger.info(f"✅ {os.path.basename(pdf_file)}: 包含文字內容 ({len(text_content)} 字元)")
                return True
            else:
                logger.warning(f"⚠️ {os.path.basename(pdf_file)}: 無文字內容")
                return False
        else:
            logger.error(f"❌ {os.path.basename(pdf_file)}: 無法讀取文字內容")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {os.path.basename(pdf_file)}: 讀取超時")
        return False
    except FileNotFoundError:
        logger.warning("pdftotext 工具未安裝，無法檢查文字內容")
        return None
    except Exception as e:
        logger.error(f"❌ {os.path.basename(pdf_file)}: 檢查錯誤 - {e}")
        return False

def check_pdf_file_size(pdf_file):
    """檢查PDF檔案大小"""
    try:
        file_size = os.path.getsize(pdf_file)
        size_mb = file_size / (1024 * 1024)
        
        if size_mb > 0.1:  # 大於100KB
            logger.info(f"✅ {os.path.basename(pdf_file)}: 檔案大小正常 ({size_mb:.2f} MB)")
            return True
        else:
            logger.warning(f"⚠️ {os.path.basename(pdf_file)}: 檔案大小過小 ({size_mb:.2f} MB)")
            return False
            
    except Exception as e:
        logger.error(f"❌ {os.path.basename(pdf_file)}: 無法檢查檔案大小 - {e}")
        return False

def check_pdf_structure(pdf_file):
    """檢查PDF檔案結構"""
    try:
        # 使用pdfinfo檢查PDF資訊
        result = subprocess.run(['pdfinfo', pdf_file], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            info = result.stdout
            logger.info(f"✅ {os.path.basename(pdf_file)}: PDF結構正常")
            
            # 提取頁數資訊
            for line in info.split('\n'):
                if 'Pages:' in line:
                    pages = line.split(':')[1].strip()
                    logger.info(f"   頁數: {pages}")
                    break
            return True
        else:
            logger.error(f"❌ {os.path.basename(pdf_file)}: PDF結構異常")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {os.path.basename(pdf_file)}: 檢查超時")
        return False
    except FileNotFoundError:
        logger.warning("pdfinfo 工具未安裝，無法檢查PDF結構")
        return None
    except Exception as e:
        logger.error(f"❌ {os.path.basename(pdf_file)}: 檢查錯誤 - {e}")
        return False

def main():
    """主函數"""
    logger.info("開始PDF品質檢查...")
    
    pdf_dir = "/home/bheadwei/LegalStatuteAnalysis_V2/output/print/pdfs"
    
    if not os.path.exists(pdf_dir):
        logger.error(f"PDF目錄不存在: {pdf_dir}")
        return
    
    # 獲取所有PDF檔案
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        logger.warning("未找到PDF檔案")
        return
    
    logger.info(f"找到 {len(pdf_files)} 個PDF檔案")
    
    # 檢查每個PDF檔案
    results = {
        'total': len(pdf_files),
        'text_ok': 0,
        'size_ok': 0,
        'structure_ok': 0,
        'all_ok': 0
    }
    
    for pdf_file in sorted(pdf_files):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        logger.info(f"\n檢查檔案: {pdf_file}")
        
        # 檢查文字內容
        text_ok = check_pdf_text_content(pdf_path)
        if text_ok is True:
            results['text_ok'] += 1
        
        # 檢查檔案大小
        size_ok = check_pdf_file_size(pdf_path)
        if size_ok:
            results['size_ok'] += 1
        
        # 檢查PDF結構
        structure_ok = check_pdf_structure(pdf_path)
        if structure_ok is True:
            results['structure_ok'] += 1
        
        # 檢查是否全部通過
        if text_ok is True and size_ok and structure_ok is True:
            results['all_ok'] += 1
    
    # 輸出檢查結果摘要
    logger.info("\n" + "="*50)
    logger.info("PDF品質檢查結果摘要:")
    logger.info(f"總檔案數: {results['total']}")
    logger.info(f"文字內容正常: {results['text_ok']}/{results['total']}")
    logger.info(f"檔案大小正常: {results['size_ok']}/{results['total']}")
    logger.info(f"PDF結構正常: {results['structure_ok']}/{results['total']}")
    logger.info(f"全部檢查通過: {results['all_ok']}/{results['total']}")
    
    if results['all_ok'] == results['total']:
        logger.info("🎉 所有PDF檔案品質檢查通過！")
    else:
        logger.warning("⚠️ 部分PDF檔案存在問題，請檢查上述詳細資訊")
    
    logger.info("="*50)

if __name__ == "__main__":
    main()
