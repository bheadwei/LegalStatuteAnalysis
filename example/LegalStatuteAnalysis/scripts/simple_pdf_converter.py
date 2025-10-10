#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版 PDF 轉換器
使用 reportlab 將 Markdown 轉換為 PDF
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List
import logging

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

def convert_md_to_pdf_simple():
    """簡單的 Markdown 轉 PDF 轉換"""
    
    # 安裝必要套件
    install_required_packages()
    
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import markdown
    import re
    
    # 設定目錄
    notes_dir = PROJECT_ROOT / "results" / "法條筆記"
    pdf_dir = PROJECT_ROOT / "results" / "法條筆記_PDF"
    pdf_dir.mkdir(exist_ok=True)
    
    # 取得 Markdown 檔案
    md_files = list(notes_dir.glob("*.md"))
    md_files.sort()
    
    print(f"📚 找到 {len(md_files)} 個 Markdown 檔案")
    print(f"📁 輸出目錄: {pdf_dir}")
    
    # 設定樣式
    styles = getSampleStyleSheet()
    
    # 建立中文樣式
    title_style = ParagraphStyle(
        'ChineseTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceAfter=30,
        alignment=1  # 置中
    )
    
    heading1_style = ParagraphStyle(
        'ChineseHeading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        spaceAfter=12
    )
    
    heading2_style = ParagraphStyle(
        'ChineseHeading2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'ChineseNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        spaceAfter=6
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
            
            for line in lines:
                line = line.strip()
                if not line:
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
                    
                elif line.startswith('> '):
                    # 引用內容
                    quote = line[2:].strip()
                    story.append(Paragraph(f"<i>{quote}</i>", normal_style))
                    
                elif line.startswith('- '):
                    # 列表項目
                    item = line[2:].strip()
                    story.append(Paragraph(f"• {item}", normal_style))
                    
                elif line.startswith('**') and line.endswith('**'):
                    # 粗體文字
                    bold_text = line[2:-2].strip()
                    story.append(Paragraph(f"<b>{bold_text}</b>", normal_style))
                    
                elif '---' in line:
                    # 分隔線
                    story.append(Spacer(1, 12))
                    
                else:
                    # 一般文字
                    if line and not line.startswith('```'):
                        # 簡單清理一些 Markdown 語法
                        clean_line = line.replace('**', '')
                        clean_line = clean_line.replace('*', '')
                        clean_line = clean_line.replace('`', '')
                        
                        if len(clean_line.strip()) > 0:
                            story.append(Paragraph(clean_line, normal_style))
            
            # 生成 PDF
            doc.build(story)
            
            print(f"✅ 完成: {pdf_file.name}")
            successful += 1
            
        except Exception as e:
            print(f"❌ 轉換失敗: {md_file.name} - {e}")
    
    print(f"\n📊 轉換結果: {successful}/{len(md_files)} 成功")
    print(f"📁 PDF 檔案位置: {pdf_dir}")
    
    return successful > 0

def main():
    """主程式"""
    print("📚 簡化版 PDF 轉換器")
    print("=" * 50)
    
    try:
        if convert_md_to_pdf_simple():
            print("\n🎉 PDF 轉換完成！")
        else:
            print("\n❌ PDF 轉換失敗")
    
    except Exception as e:
        print(f"❌ 轉換過程中發生錯誤: {e}")

if __name__ == "__main__":
    main()
