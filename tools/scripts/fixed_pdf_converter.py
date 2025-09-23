#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版 PDF 轉換器
支援中文字體的 Markdown 轉 PDF
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List
import logging
import requests

PROJECT_ROOT = Path(__file__).parent.parent

def install_required_packages():
    """安裝必要的套件"""
    packages = ['reportlab', 'markdown']
    
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            print(f"📦 安裝 {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def download_chinese_font():
    """下載中文字體檔案"""
    font_dir = PROJECT_ROOT / "fonts"
    font_dir.mkdir(exist_ok=True)
    
    font_file = font_dir / "NotoSansCJK-Regular.ttc"
    
    # 如果字體檔案已存在，直接返回路徑
    if font_file.exists():
        return str(font_file)
    
    # 使用系統中文字體
    system_fonts = [
        "C:/Windows/Fonts/simsun.ttc",  # 宋體
        "C:/Windows/Fonts/msyh.ttc",    # 微軟雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑體
        "C:/Windows/Fonts/kaiu.ttf",    # 標楷體
    ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            print(f"📝 使用系統字體: {font_path}")
            return font_path
    
    print("⚠️ 未找到合適的中文字體，將使用預設字體")
    return None

def convert_md_to_pdf_with_chinese():
    """支援中文的 Markdown 轉 PDF 轉換"""
    
    # 安裝必要套件
    install_required_packages()
    
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import black, blue, darkgreen
    import markdown
    import re
    
    # 設定目錄
    notes_dir = PROJECT_ROOT / "results" / "法條筆記"
    pdf_dir = PROJECT_ROOT / "results" / "法條筆記_PDF"
    pdf_dir.mkdir(exist_ok=True)
    
    # 註冊中文字體
    chinese_font_path = download_chinese_font()
    if chinese_font_path:
        try:
            pdfmetrics.registerFont(TTFont('ChineseFont', chinese_font_path))
            chinese_font_name = 'ChineseFont'
            print(f"✅ 成功註冊中文字體: {chinese_font_path}")
        except Exception as e:
            print(f"⚠️ 字體註冊失敗: {e}")
            chinese_font_name = 'Helvetica'
    else:
        chinese_font_name = 'Helvetica'
    
    # 取得 Markdown 檔案
    md_files = list(notes_dir.glob("*.md"))
    md_files.sort()
    
    print(f"📚 找到 {len(md_files)} 個 Markdown 檔案")
    print(f"📁 輸出目錄: {pdf_dir}")
    print(f"🔤 使用字體: {chinese_font_name}")
    
    # 設定樣式
    styles = getSampleStyleSheet()
    
    # 建立中文樣式
    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Title'],
        fontName=chinese_font_name,
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # 置中
        textColor=darkgreen
    )
    
    heading1_style = ParagraphStyle(
        'ChineseHeading1',
        parent=styles['Heading1'],
        fontName=chinese_font_name,
        fontSize=16,
        spaceAfter=12,
        textColor=blue
    )
    
    heading2_style = ParagraphStyle(
        'ChineseHeading2',
        parent=styles['Heading2'],
        fontName=chinese_font_name,
        fontSize=14,
        spaceAfter=10,
        textColor=blue
    )
    
    heading3_style = ParagraphStyle(
        'ChineseHeading3',
        fontName=chinese_font_name,
        fontSize=12,
        spaceAfter=8,
        textColor=darkgreen
    )
    
    normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName=chinese_font_name,
        fontSize=11,
        spaceAfter=6,
        leading=16
    )
    
    quote_style = ParagraphStyle(
        'ChineseQuote',
        parent=normal_style,
        fontName=chinese_font_name,
        fontSize=10,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=6,
        textColor=darkgreen
    )
    
    list_style = ParagraphStyle(
        'ChineseList',
        parent=normal_style,
        fontName=chinese_font_name,
        fontSize=10,
        leftIndent=20,
        spaceAfter=4
    )
    
    successful = 0
    
    for md_file in md_files:
        try:
            print(f"🔄 轉換: {md_file.name}")
            
            # 讀取 Markdown 內容
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 建立 PDF 文件
            pdf_file = pdf_dir / f"{md_file.stem}.pdf"
            doc = SimpleDocTemplate(
                str(pdf_file),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # 解析內容
            story = []
            lines = md_content.split('\n')
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if not line:
                    i += 1
                    continue
                
                # 處理不同類型的內容
                if line.startswith('# '):
                    # 主標題
                    title = line[2:].strip()
                    story.append(Paragraph(title, title_style))
                    story.append(Spacer(1, 12))
                    
                elif line.startswith('## '):
                    # 二級標題
                    heading = line[3:].strip()
                    story.append(Paragraph(heading, heading1_style))
                    story.append(Spacer(1, 8))
                    
                elif line.startswith('### '):
                    # 三級標題
                    heading = line[4:].strip()
                    story.append(Paragraph(heading, heading2_style))
                    story.append(Spacer(1, 6))
                    
                elif line.startswith('#### '):
                    # 四級標題
                    heading = line[5:].strip()
                    story.append(Paragraph(heading, heading3_style))
                    story.append(Spacer(1, 4))
                    
                elif line.startswith('> '):
                    # 引用內容
                    quote = line[2:].strip()
                    story.append(Paragraph(quote, quote_style))
                    
                elif line.startswith('- ') or line.startswith('* '):
                    # 列表項目
                    item = line[2:].strip()
                    # 處理嵌套列表
                    bullet = "•"
                    if line.startswith('  - ') or line.startswith('  * '):
                        bullet = "◦"
                        item = line[4:].strip()
                    elif line.startswith('    - ') or line.startswith('    * '):
                        bullet = "▪"
                        item = line[6:].strip()
                    
                    story.append(Paragraph(f"{bullet} {item}", list_style))
                    
                elif line.startswith('**') and line.endswith('**'):
                    # 粗體文字
                    bold_text = line[2:-2].strip()
                    story.append(Paragraph(f"<b>{bold_text}</b>", normal_style))
                    
                elif '---' in line or '===' in line:
                    # 分隔線
                    story.append(Spacer(1, 12))
                    
                elif line.startswith('```'):
                    # 程式碼區塊 - 跳過
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('```'):
                        i += 1
                    
                else:
                    # 一般文字
                    if line and len(line.strip()) > 0:
                        # 清理 Markdown 語法
                        clean_line = line
                        
                        # 處理粗體
                        clean_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_line)
                        
                        # 處理斜體
                        clean_line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_line)
                        
                        # 處理行內程式碼
                        clean_line = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', clean_line)
                        
                        # 移除其他 Markdown 符號
                        clean_line = clean_line.replace('`', '')
                        
                        if len(clean_line.strip()) > 0:
                            story.append(Paragraph(clean_line, normal_style))
                
                i += 1
            
            # 生成 PDF
            doc.build(story)
            
            print(f"✅ 完成: {pdf_file.name}")
            successful += 1
            
        except Exception as e:
            print(f"❌ 轉換失敗: {md_file.name} - {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n📊 轉換結果: {successful}/{len(md_files)} 成功")
    print(f"📁 PDF 檔案位置: {pdf_dir}")
    
    return successful > 0

def main():
    """主程式"""
    print("📚 修正版 PDF 轉換器（支援中文）")
    print("=" * 50)
    
    try:
        if convert_md_to_pdf_with_chinese():
            print("\n🎉 PDF 轉換完成！")
        else:
            print("\n❌ PDF 轉換失敗")
    
    except Exception as e:
        print(f"❌ 轉換過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

