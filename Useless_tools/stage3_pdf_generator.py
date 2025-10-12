#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第三階段：PDF生成器
生成法條講義的PDF檔案，包含個別PDF和合併PDF
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Any
import logging
from datetime import datetime
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, base_path: str = "/home/bheadwei/LegalStatuteAnalysis_V2"):
        self.base_path = base_path
        self.output_path = os.path.join(base_path, "output")
        self.print_path = os.path.join(self.output_path, "print")
        self.pdf_path = os.path.join(self.print_path, "pdfs")
        
        # 確保目錄存在
        os.makedirs(self.print_path, exist_ok=True)
        os.makedirs(self.pdf_path, exist_ok=True)
        
        # 載入整合資料
        self.integrated_data = self.load_integrated_data()
        self.statistics = self.load_statistics()
        
    def load_integrated_data(self) -> Dict[str, Any]:
        """載入第一階段整合的資料"""
        integrated_file = os.path.join(self.base_path, "results", "integrated_data_stage1.json")
        logger.info(f"載入整合資料: {integrated_file}")
        
        with open(integrated_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_statistics(self) -> Dict[str, Any]:
        """載入統計資料"""
        stats_file = os.path.join(self.base_path, "results", "statistics_stage1.json")
        logger.info(f"載入統計資料: {stats_file}")
        
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_print_css(self) -> str:
        """生成列印專用CSS"""
        css_file = os.path.join(self.output_path, "styles", "print.css")
        logger.info(f"列印CSS已存在: {css_file}")
        return css_file
    
    def format_law_content(self, content: str) -> str:
        """格式化法條內容，保持結構化格式"""
        if not content:
            return ""
        
        # 先處理換行符問題，將被意外分割的句子重新連接
        content = content.replace('連選得連任\n一次', '連選得連任一次')
        
        # 將內容按行分割
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 處理包含多個編號項目的行（如一、...二、...）
            if '。二、' in line or '。三、' in line or '。四、' in line or '。五、' in line:
                # 分割包含多個編號項目的行
                parts = []
                current_part = ""
                
                # 使用正則表達式分割
                import re
                # 找到所有編號項目的位置
                matches = list(re.finditer(r'[一二三四五六七八九十]、', line))
                
                if matches:
                    for i, match in enumerate(matches):
                        start = match.start()
                        if i == 0:
                            # 第一個項目，包含前面的內容
                            current_part = line[:start] + match.group()
                        else:
                            # 後續項目，先保存前一個項目
                            if current_part:
                                parts.append(current_part)
                            current_part = match.group()
                        
                        # 找到下一個項目的開始位置或行尾
                        if i + 1 < len(matches):
                            next_start = matches[i + 1].start()
                            current_part += line[start + len(match.group()):next_start]
                        else:
                            # 最後一個項目
                            current_part += line[start + len(match.group()):]
                    
                    # 添加最後一個項目
                    if current_part:
                        parts.append(current_part)
                    
                    # 格式化每個部分
                    for part in parts:
                        part = part.strip()
                        if part:
                            if any(part.startswith(f'{num}、') for num in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']):
                                formatted_lines.append(f'<div class="law-item">{part}</div>')
                            else:
                                formatted_lines.append(f'<div class="law-paragraph">{part}</div>')
                else:
                    # 如果沒有找到編號項目，按普通段落處理
                    formatted_lines.append(f'<div class="law-paragraph">{line}</div>')
            else:
                # 檢查是否為編號項目（一、二、三、四、五、六、七、八、九、十）
                if any(line.startswith(f'{num}、') for num in ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十']):
                    # 為編號項目添加適當的HTML結構
                    formatted_lines.append(f'<div class="law-item">{line}</div>')
                else:
                    # 普通段落
                    formatted_lines.append(f'<div class="law-paragraph">{line}</div>')
        
        return '\n'.join(formatted_lines)

    def generate_print_law_page(self, law_id: str, law_data: Dict[str, Any]) -> str:
        """生成列印專用的法條頁面"""
        questions = self.integrated_data['law_question_mapping'].get(law_id, [])
        
        # 將題目按question_id分組，避免重複顯示
        unique_questions = {}
        for question in questions:
            question_id = question['question_id']
            if question_id not in unique_questions:
                unique_questions[question_id] = question
        
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{law_data['law_name']} 第{law_data['article_no_main']}條 - 列印版</title>
    <link rel="stylesheet" href="../styles/print.css">
    <style>
        /* 內嵌樣式確保列印效果 */
        @media print {{
            @page {{
                size: A4;
                margin: 15mm;
            }}
            body {{
                font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #000;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                text-rendering: optimizeLegibility;
            }}
        }}
        
        /* 確保字體載入 */
        body {{
            font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="law-article">
            <div class="law-header">
                <div class="law-title">
                    {law_data['law_name']} 第 {law_data['article_no_main']} 條
                </div>
                <div class="law-meta">
                    {law_data['chapter_title']} | {law_data['authority']}
                </div>
            </div>
            
            <div class="law-content">
                {self.format_law_content(law_data['content'])}
            </div>
            
            {self.generate_questions_section(unique_questions) if unique_questions else '<div class="questions-section"><div class="questions-title">本條文暫無相關考題</div></div>'}
        </div>
    </div>
</body>
</html>"""
        return html
    
    def generate_questions_section(self, unique_questions: Dict[str, Any]) -> str:
        """生成題目區域HTML"""
        if not unique_questions:
            return ""
        
        html = '<div class="questions-section">'
        html += f'<div class="questions-title">相關考題 ({len(unique_questions)} 題)</div>'
        
        # 只遍歷唯一的題目
        for question in unique_questions.values():
            html += self.generate_question_html(question)
        
        html += '</div>'
        return html
    
    def generate_question_html(self, question: Dict[str, Any]) -> str:
        """生成單個題目HTML"""
        # 獲取完整題目資料
        question_data = None
        for q in self.integrated_data['questions']:
            if q['question_number'] == question['question_number']:
                question_data = q
                break
        
        if not question_data:
            return ""
        
        html = f"""
        <div class="question-item">
            <div class="question-header">
                <div class="question-number">第 {question['question_number']} 題</div>
                <div class="question-points">{question_data['points']} 分</div>
            </div>
            
            <div class="question-content">
                {question['question_content']}
            </div>
            
            <ul class="options-list">
        """
        
        # 生成選項
        for option_key, option_data in question_data['options'].items():
            is_correct = option_key == question_data['correct_answer']
            option_class = "correct-answer" if is_correct else ""
            law_ref = option_data[1] if len(option_data) > 1 else ""
            
            html += f"""
                <li class="option-item {option_class}">
                    <div class="option-key">{option_key}</div>
                    <div class="option-content">
                        {option_data[0]}
                        {f'<div class="option-law-ref">引用法條: {law_ref}</div>' if law_ref else ''}
                    </div>
                </li>
            """
        
        html += """
            </ul>
        </div>
        """
        
        return html
    
    def generate_combined_page(self) -> str:
        """生成合併所有法條的頁面"""
        laws_with_questions = []
        for law_id, law_data in self.integrated_data['laws'].items():
            if law_id in self.integrated_data['law_question_mapping']:
                laws_with_questions.append((law_id, law_data))
        
        # 按法規類別排序
        laws_by_category = {}
        for law_id, law_data in laws_with_questions:
            category = law_data['category']
            if category not in laws_by_category:
                laws_by_category[category] = []
            laws_by_category[category].append((law_id, law_data))
        
        html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>不動產經紀相關法規講義 - 完整版</title>
    <link rel="stylesheet" href="../styles/print.css">
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 15mm;
            }}
            body {{
                font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #000;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="law-article">
            <div class="law-header">
                <div class="law-title">不動產經紀相關法規講義</div>
                <div class="law-meta">113年專門職業及技術人員高等考試建築師、32類科技師（含第二次食品技師）、大地工程技師考試分階段考試暨普通考試不動產經紀人、記帳士考試試題</div>
            </div>
            
            <div class="law-content">
                <h3>考試資訊</h3>
                <ul>
                    <li>科目名稱：不動產經紀相關法規概要</li>
                    <li>考試時間：1 小時 30 分</li>
                    <li>題目總數：{self.integrated_data['metadata']['total_questions']} 題</li>
                    <li>法條總數：{self.integrated_data['metadata']['total_laws']} 條</li>
                    <li>有考題的法條數：{self.statistics['law_statistics']['laws_with_questions']} 條</li>
                </ul>
                
                <h3>法條統計</h3>
                <ul>
                    <li>不動產經紀：{self.statistics['law_statistics']['categories']['不動產經紀']} 條</li>
                    <li>住宅管理：{self.statistics['law_statistics']['categories']['住宅管理']} 條</li>
                    <li>競爭法：{self.statistics['law_statistics']['categories']['競爭法']} 條</li>
                    <li>消費者權益：{self.statistics['law_statistics']['categories']['消費者權益']} 條</li>
                </ul>
            </div>
        </div>
        """
        
        # 生成各類別的法條
        for category, laws in laws_by_category.items():
            html += f'<div class="law-article"><div class="law-header"><div class="law-title">{category}</div></div></div>'
            
            for law_id, law_data in laws:
                questions = self.integrated_data['law_question_mapping'].get(law_id, [])
                unique_questions = {}
                for question in questions:
                    question_id = question['question_id']
                    if question_id not in unique_questions:
                        unique_questions[question_id] = question
                
                html += f"""
                <div class="law-article">
                    <div class="law-header">
                        <div class="law-title">
                            {law_data['law_name']} 第 {law_data['article_no_main']} 條
                        </div>
                        <div class="law-meta">
                            {law_data['chapter_title']} | {law_data['authority']}
                        </div>
                    </div>
                    
                    <div class="law-content">
                        {self.format_law_content(law_data['content'])}
                    </div>
                    
                    {self.generate_questions_section(unique_questions) if unique_questions else '<div class="questions-section"><div class="questions-title">本條文暫無相關考題</div></div>'}
                </div>
                """
        
        html += """
    </div>
</body>
</html>"""
        return html
    
    def generate_print_pages(self) -> List[str]:
        """生成所有列印專用頁面"""
        logger.info("開始生成列印專用頁面...")
        
        generated_files = []
        
        # 生成個別法條頁面
        for law_id, law_data in self.integrated_data['laws'].items():
            if law_id in self.integrated_data['law_question_mapping']:
                print_html = self.generate_print_law_page(law_id, law_data)
                print_file = os.path.join(self.print_path, f"print_{law_id}.html")
                
                with open(print_file, 'w', encoding='utf-8') as f:
                    f.write(print_html)
                
                generated_files.append(print_file)
                logger.info(f"生成列印頁面: {print_file}")
        
        # 生成合併頁面
        combined_html = self.generate_combined_page()
        combined_file = os.path.join(self.print_path, "print_combined.html")
        
        with open(combined_file, 'w', encoding='utf-8') as f:
            f.write(combined_html)
        
        generated_files.append(combined_file)
        logger.info(f"生成合併頁面: {combined_file}")
        
        return generated_files
    
    def check_dependencies(self) -> bool:
        """檢查PDF生成所需的依賴"""
        logger.info("檢查PDF生成依賴...")
        
        # 檢查wkhtmltopdf
        try:
            result = subprocess.run(['wkhtmltopdf', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("wkhtmltopdf 已安裝")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # 檢查weasyprint
        try:
            import weasyprint
            logger.info("weasyprint 已安裝")
            return True
        except ImportError:
            pass
        
        # 檢查playwright
        try:
            import playwright
            logger.info("playwright 已安裝")
            return True
        except ImportError:
            pass
        
        logger.warning("未找到PDF生成工具，將使用瀏覽器列印方式")
        return False
    
    def generate_pdf_with_wkhtmltopdf(self, html_file: str, pdf_file: str) -> bool:
        """使用wkhtmltopdf生成PDF"""
        try:
            # 使用經過測試的參數組合
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '15mm',
                '--margin-bottom', '15mm',
                '--margin-left', '15mm',
                '--margin-right', '15mm',
                '--encoding', 'UTF-8',
                '--enable-local-file-access',
                '--load-error-handling', 'ignore',
                '--javascript-delay', '1000',
                '--dpi', '300',
                html_file,
                pdf_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"PDF生成成功: {pdf_file}")
                return True
            else:
                logger.error(f"PDF生成失敗: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("PDF生成超時")
            return False
        except Exception as e:
            logger.error(f"PDF生成錯誤: {e}")
            return False
    
    def generate_pdf_with_weasyprint(self, html_file: str, pdf_file: str) -> bool:
        """使用weasyprint生成PDF"""
        try:
            from weasyprint import HTML, CSS
            
            html_doc = HTML(filename=html_file)
            css_doc = CSS(filename=os.path.join(self.output_path, "styles", "print.css"))
            
            html_doc.write_pdf(pdf_file, stylesheets=[css_doc])
            logger.info(f"PDF生成成功: {pdf_file}")
            return True
            
        except Exception as e:
            logger.error(f"PDF生成錯誤: {e}")
            return False
    
    def generate_individual_pdfs(self) -> List[str]:
        """生成個別法條PDF"""
        logger.info("開始生成個別法條PDF...")
        
        generated_pdfs = []
        
        for law_id, law_data in self.integrated_data['laws'].items():
            if law_id in self.integrated_data['law_question_mapping']:
                html_file = os.path.join(self.print_path, f"print_{law_id}.html")
                pdf_file = os.path.join(self.pdf_path, f"{law_id}.pdf")
                
                # 嘗試不同的PDF生成方法
                success = False
                
                if self.generate_pdf_with_wkhtmltopdf(html_file, pdf_file):
                    success = True
                elif self.generate_pdf_with_weasyprint(html_file, pdf_file):
                    success = True
                
                if success:
                    generated_pdfs.append(pdf_file)
                else:
                    logger.warning(f"無法生成PDF: {pdf_file}")
        
        return generated_pdfs
    
    def generate_combined_pdf(self) -> str:
        """生成合併PDF"""
        logger.info("開始生成合併PDF...")
        
        html_file = os.path.join(self.print_path, "print_combined.html")
        pdf_file = os.path.join(self.pdf_path, "complete.pdf")
        
        # 嘗試不同的PDF生成方法
        success = False
        
        if self.generate_pdf_with_wkhtmltopdf(html_file, pdf_file):
            success = True
        elif self.generate_pdf_with_weasyprint(html_file, pdf_file):
            success = True
        
        if success:
            logger.info(f"合併PDF生成成功: {pdf_file}")
            return pdf_file
        else:
            logger.warning(f"無法生成合併PDF: {pdf_file}")
            return ""
    
    def generate_all_pdfs(self) -> Dict[str, Any]:
        """生成所有PDF檔案"""
        logger.info("開始第三階段PDF生成...")
        
        # 生成列印頁面
        print_pages = self.generate_print_pages()
        
        # 檢查依賴
        has_dependencies = self.check_dependencies()
        
        result = {
            'print_pages': print_pages,
            'individual_pdfs': [],
            'combined_pdf': '',
            'has_dependencies': has_dependencies
        }
        
        if has_dependencies:
            # 生成個別PDF
            individual_pdfs = self.generate_individual_pdfs()
            result['individual_pdfs'] = individual_pdfs
            
            # 生成合併PDF
            combined_pdf = self.generate_combined_pdf()
            result['combined_pdf'] = combined_pdf
        else:
            logger.info("請手動使用瀏覽器列印功能生成PDF")
            logger.info(f"列印頁面位置: {self.print_path}")
        
        return result
    
    def create_manual_print_guide(self) -> str:
        """創建手動列印指南"""
        guide_content = f"""# 法條講義PDF生成指南

## 自動生成（推薦）

如果已安裝PDF生成工具，請執行：
```bash
python scripts/stage3_pdf_generator.py
```

## 手動列印

### 個別法條PDF
1. 開啟瀏覽器
2. 開啟以下檔案：
"""
        
        for law_id, law_data in self.integrated_data['laws'].items():
            if law_id in self.integrated_data['law_question_mapping']:
                guide_content += f"   - `print/print_{law_id}.html` - {law_data['law_name']} 第{law_data['article_no_main']}條\n"
        
        guide_content += f"""
3. 使用瀏覽器列印功能（Ctrl+P）
4. 選擇「另存為PDF」
5. 設定頁面大小為A4，邊距為15mm
6. 儲存為對應的PDF檔案

### 合併PDF
1. 開啟 `print/print_combined.html`
2. 使用瀏覽器列印功能
3. 選擇「另存為PDF」
4. 儲存為 `complete.pdf`

## 檔案位置
- 列印頁面：`{self.print_path}/`
- PDF檔案：`{self.pdf_path}/`

## 列印設定建議
- 頁面大小：A4
- 邊距：上下左右各15mm
- 縮放：100%
- 背景圖形：開啟（確保顏色正確顯示）

生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        guide_file = os.path.join(self.print_path, "PRINT_GUIDE.md")
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        return guide_file

def main():
    """主函數"""
    logger.info("開始第三階段PDF生成...")
    
    try:
        # 初始化生成器
        generator = PDFGenerator()
        
        # 生成所有PDF
        result = generator.generate_all_pdfs()
        
        # 創建手動列印指南
        guide_file = generator.create_manual_print_guide()
        
        # 輸出摘要
        logger.info("=" * 50)
        logger.info("第三階段PDF生成完成摘要:")
        logger.info(f"列印頁面目錄: {generator.print_path}")
        logger.info(f"PDF目錄: {generator.pdf_path}")
        logger.info(f"生成列印頁面數: {len(result['print_pages'])}")
        logger.info(f"生成個別PDF數: {len(result['individual_pdfs'])}")
        logger.info(f"合併PDF: {'已生成' if result['combined_pdf'] else '未生成'}")
        logger.info(f"依賴檢查: {'通過' if result['has_dependencies'] else '未通過'}")
        logger.info(f"手動列印指南: {guide_file}")
        logger.info("=" * 50)
        
        if not result['has_dependencies']:
            logger.info("請參考手動列印指南使用瀏覽器列印功能")
        
        return True
        
    except Exception as e:
        logger.error(f"第三階段PDF生成失敗: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

