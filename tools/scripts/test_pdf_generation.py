#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF生成測試腳本 - 解決中文字體顯示問題
"""

import os
import subprocess
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_html():
    """創建測試用的HTML檔案"""
    test_html = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>中文字體測試</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');
        
        body {
            font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', 'Source Han Sans TC', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14pt;
            line-height: 1.6;
            color: #000;
            margin: 20px;
            background: white;
        }
        
        .test-section {
            margin-bottom: 30px;
            padding: 20px;
            border: 2px solid #2c3e50;
            border-radius: 8px;
        }
        
        .test-title {
            font-size: 18pt;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .test-content {
            font-size: 12pt;
            line-height: 1.5;
        }
        
        @media print {
            @page {
                size: A4;
                margin: 15mm;
            }
            body {
                font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', 'Source Han Sans TC', 'Helvetica Neue', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #000;
                margin: 0;
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="test-section">
        <div class="test-title">不動產經紀業管理條例 第 29 條</div>
        <div class="test-content">
            經紀業違反本條例者，依下列規定處罰之：<br>
            一、違反第七條第六項、第十一條、第十七條、第十九條第一項、第二十一條第一項、第二項或第二十二條第一項規定，由直轄市、縣（市）主管機關處新臺幣六萬元以上三十萬元以下罰鍰。<br>
            二、違反第二十四條之一第二項規定，未依限申報登錄資訊或申報登錄價格、交易面積資訊不實由直轄市、縣（市）主管機關按戶（棟）處新臺幣三萬元以上十五萬元以下罰鍰，並令其限期改正；屆期未改正者，按次處罰。
        </div>
    </div>
    
    <div class="test-section">
        <div class="test-title">相關考題</div>
        <div class="test-content">
            <strong>第 1 題</strong><br>
            不動產說明書係不動產交易過程中極為重要之資訊揭露文件，下列關於不動產說明書之敘述，何者與不動產經紀業管理條例之規定不符？<br><br>
            A. 不動產之買賣如委由經紀業代銷者，不動產說明書應由經紀業指派經紀人簽章<br>
            B. 經紀人員在執行業務過程中，應以不動產說明書向與委託人交易之相對人解說<br>
            C. 經紀人員於提供解說後，應將不動產說明書交由委託人簽章<br>
            D. 雙方當事人簽訂買賣契約書後，不動產說明書視為買賣契約書之一部分
        </div>
    </div>
</body>
</html>"""
    
    test_file = "/home/bheadwei/LegalStatuteAnalysis_V2/output/print/test_font.html"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    return test_file

def test_wkhtmltopdf_methods():
    """測試不同的wkhtmltopdf參數組合"""
    test_html = create_test_html()
    base_path = "/home/bheadwei/LegalStatuteAnalysis_V2/output/print/pdfs"
    
    # 測試方法1：基本參數
    test_method_1(test_html, base_path)
    
    # 測試方法2：增強字體支援
    test_method_2(test_html, base_path)
    
    # 測試方法3：使用系統字體
    test_method_3(test_html, base_path)

def test_method_1(html_file, output_path):
    """測試方法1：基本參數"""
    logger.info("測試方法1：基本參數")
    
    pdf_file = os.path.join(output_path, "test_method1.pdf")
    cmd = [
        'wkhtmltopdf',
        '--page-size', 'A4',
        '--margin-top', '15mm',
        '--margin-bottom', '15mm',
        '--margin-left', '15mm',
        '--margin-right', '15mm',
        '--encoding', 'UTF-8',
        '--print-media-type',
        html_file,
        pdf_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            logger.info(f"方法1成功: {pdf_file}")
        else:
            logger.error(f"方法1失敗: {result.stderr}")
    except Exception as e:
        logger.error(f"方法1錯誤: {e}")

def test_method_2(html_file, output_path):
    """測試方法2：增強字體支援"""
    logger.info("測試方法2：增強字體支援")
    
    pdf_file = os.path.join(output_path, "test_method2.pdf")
    cmd = [
        'wkhtmltopdf',
        '--page-size', 'A4',
        '--margin-top', '15mm',
        '--margin-bottom', '15mm',
        '--margin-left', '15mm',
        '--margin-right', '15mm',
        '--encoding', 'UTF-8',
        '--print-media-type',
        '--enable-local-file-access',
        '--load-error-handling', 'ignore',
        '--javascript-delay', '2000',
        '--dpi', '300',
        '--enable-font-subsetting',
        '--disable-smart-shrinking',
        html_file,
        pdf_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            logger.info(f"方法2成功: {pdf_file}")
        else:
            logger.error(f"方法2失敗: {result.stderr}")
    except Exception as e:
        logger.error(f"方法2錯誤: {e}")

def test_method_3(html_file, output_path):
    """測試方法3：使用系統字體"""
    logger.info("測試方法3：使用系統字體")
    
    # 創建使用系統字體的HTML
    system_font_html = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系統字體測試</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
            font-size: 14pt;
            line-height: 1.6;
            color: #000;
            margin: 20px;
            background: white;
        }
        
        .test-section {
            margin-bottom: 30px;
            padding: 20px;
            border: 2px solid #2c3e50;
            border-radius: 8px;
        }
        
        .test-title {
            font-size: 18pt;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .test-content {
            font-size: 12pt;
            line-height: 1.5;
        }
        
        @media print {
            @page {
                size: A4;
                margin: 15mm;
            }
            body {
                font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #000;
                margin: 0;
                padding: 0;
            }
        }
    </style>
</head>
<body>
    <div class="test-section">
        <div class="test-title">不動產經紀業管理條例 第 29 條</div>
        <div class="test-content">
            經紀業違反本條例者，依下列規定處罰之：<br>
            一、違反第七條第六項、第十一條、第十七條、第十九條第一項、第二十一條第一項、第二項或第二十二條第一項規定，由直轄市、縣（市）主管機關處新臺幣六萬元以上三十萬元以下罰鍰。<br>
            二、違反第二十四條之一第二項規定，未依限申報登錄資訊或申報登錄價格、交易面積資訊不實由直轄市、縣（市）主管機關按戶（棟）處新臺幣三萬元以上十五萬元以下罰鍰，並令其限期改正；屆期未改正者，按次處罰。
        </div>
    </div>
    
    <div class="test-section">
        <div class="test-title">相關考題</div>
        <div class="test-content">
            <strong>第 1 題</strong><br>
            不動產說明書係不動產交易過程中極為重要之資訊揭露文件，下列關於不動產說明書之敘述，何者與不動產經紀業管理條例之規定不符？<br><br>
            A. 不動產之買賣如委由經紀業代銷者，不動產說明書應由經紀業指派經紀人簽章<br>
            B. 經紀人員在執行業務過程中，應以不動產說明書向與委託人交易之相對人解說<br>
            C. 經紀人員於提供解說後，應將不動產說明書交由委託人簽章<br>
            D. 雙方當事人簽訂買賣契約書後，不動產說明書視為買賣契約書之一部分
        </div>
    </div>
</body>
</html>"""
    
    system_html_file = "/home/bheadwei/LegalStatuteAnalysis_V2/output/print/test_system_font.html"
    with open(system_html_file, 'w', encoding='utf-8') as f:
        f.write(system_font_html)
    
    pdf_file = os.path.join(output_path, "test_method3.pdf")
    cmd = [
        'wkhtmltopdf',
        '--page-size', 'A4',
        '--margin-top', '15mm',
        '--margin-bottom', '15mm',
        '--margin-left', '15mm',
        '--margin-right', '15mm',
        '--encoding', 'UTF-8',
        '--print-media-type',
        '--enable-local-file-access',
        '--load-error-handling', 'ignore',
        '--javascript-delay', '1000',
        '--dpi', '300',
        '--disable-smart-shrinking',
        system_html_file,
        pdf_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            logger.info(f"方法3成功: {pdf_file}")
        else:
            logger.error(f"方法3失敗: {result.stderr}")
    except Exception as e:
        logger.error(f"方法3錯誤: {e}")

def main():
    """主函數"""
    logger.info("開始PDF字體測試...")
    
    # 確保輸出目錄存在
    os.makedirs("/home/bheadwei/LegalStatuteAnalysis_V2/output/print/pdfs", exist_ok=True)
    
    # 測試不同的方法
    test_wkhtmltopdf_methods()
    
    logger.info("PDF字體測試完成！")
    logger.info("請檢查生成的PDF檔案，找出最佳的字體顯示方法。")

if __name__ == "__main__":
    main()
