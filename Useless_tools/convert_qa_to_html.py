#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QA Mapped 結果 HTML 轉換器
將 qa_mapped 目錄中的考題 JSON 轉換成美觀的 HTML 報告
"""

import json
import os
from typing import Dict, List, Any
import logging
from datetime import datetime
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QAMappedHTMLGenerator:
    def __init__(self, input_dir: str, output_dir: str):
        """
        初始化 HTML 生成器

        Args:
            input_dir: qa_mapped JSON 檔案所在目錄
            output_dir: HTML 輸出目錄
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        # 確保輸出目錄存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "styles").mkdir(exist_ok=True)

        logger.info(f"輸入目錄: {self.input_dir}")
        logger.info(f"輸出目錄: {self.output_dir}")

    def parse_filename(self, filename: str) -> Dict[str, str]:
        """
        解析檔名，提取年份和科目資訊

        格式：112190_1201_民法概要_mapped.json
        """
        import re

        # 移除副檔名和後綴
        name = filename.replace('_mapped.json', '')

        # 提取年份（前3位數字）和科目
        match = re.match(r'(\d{3})(\d+)_(\d+)_(.+)', name)
        if match:
            year = match.group(1)  # 例如：112
            exam_code = match.group(2) + match.group(3)  # 例如：1901201
            subject = match.group(4)  # 例如：民法概要

            return {
                'year': f'{year}年',
                'exam_code': exam_code,
                'subject': subject,
                'display': f'{year}年 - {subject}'
            }

        return {
            'year': '未知',
            'exam_code': '',
            'subject': name,
            'display': name
        }

    def generate_css(self) -> str:
        """生成CSS樣式"""
        return """
/* 考題報告樣式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}

/* 頁面標題 */
.page-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 30px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 15px;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.page-header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-weight: 700;
}

.page-header .subtitle {
    font-size: 1.2em;
    opacity: 0.95;
}

/* 元資料卡片 */
.metadata-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 30px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metadata-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 15px;
}

.metadata-item {
    display: flex;
    justify-content: space-between;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #3498db;
}

.metadata-label {
    font-weight: 600;
    color: #555;
}

.metadata-value {
    color: #2c3e50;
    font-weight: 500;
}

/* 題目卡片 */
.question-card {
    background: white;
    border: 3px solid #2c3e50;
    border-radius: 15px;
    margin-bottom: 30px;
    padding: 0;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.question-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.question-header {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 20px 30px;
    border-radius: 12px 12px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.question-number {
    font-size: 1.5em;
    font-weight: 700;
}

.correct-answer-badge {
    background: #27ae60;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1.1em;
}

.no-answer-badge {
    background: #95a5a6;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1.1em;
}

.question-content {
    padding: 25px 30px;
}

.question-text {
    font-size: 1.2em;
    font-weight: 600;
    margin-bottom: 20px;
    color: #2c3e50;
    line-height: 1.8;
}

/* 選項區域 */
.options-section {
    margin-top: 20px;
}

.option-card {
    background: #f8f9fa;
    border: 2px solid #ddd;
    border-radius: 12px;
    margin-bottom: 15px;
    padding: 20px;
    transition: all 0.3s ease;
}

.option-card.correct {
    border-color: #27ae60;
    background: #d4edda;
}

.option-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.option-header {
    display: flex;
    align-items: flex-start;
}

.option-letter {
    background: #3498db;
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.2em;
    margin-right: 15px;
    flex-shrink: 0;
}

.option-card.correct .option-letter {
    background: #27ae60;
}

.option-text {
    flex: 1;
    font-size: 1.1em;
    line-height: 1.7;
    color: #2c3e50;
}

/* 導航 */
.navigation {
    background: white;
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.nav-list {
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
}

.nav-item {
    background: #3498db;
    color: white;
    padding: 10px 18px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    font-size: 0.95em;
}

.nav-item:hover {
    background: #2980b9;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

.nav-item.active {
    background: #e74c3c;
}

/* 索引頁面樣式 */
.exam-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

.exam-card {
    background: white;
    border: 2px solid #e0e0e0;
    border-left: 5px solid #3498db;
    border-radius: 12px;
    padding: 25px;
    transition: all 0.3s ease;
    cursor: pointer;
}

.exam-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    border-left-color: #e74c3c;
}

.exam-title {
    font-size: 1.3em;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 15px;
}

.exam-stats {
    display: flex;
    gap: 20px;
    margin-top: 12px;
}

.stat-badge {
    background: #f8f9fa;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.9em;
    color: #555;
}

/* 響應式設計 */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }

    .page-header {
        padding: 20px;
    }

    .page-header h1 {
        font-size: 1.8em;
    }

    .question-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .metadata-grid {
        grid-template-columns: 1fr;
    }

    .exam-grid {
        grid-template-columns: 1fr;
    }
}

/* 列印樣式 */
@media print {
    body {
        background: white;
        padding: 0;
    }

    .question-card {
        break-inside: avoid;
        box-shadow: none;
        border: 2px solid #2c3e50;
    }

    .navigation {
        display: none;
    }

    .page-header {
        background: #2c3e50;
    }
}
"""

    def generate_index_page(self, json_files: List[Path]) -> str:
        """生成索引頁面"""
        # 收集所有文件的資訊
        exams_data = []

        for json_file in json_files:
            # 讀取 JSON 資料
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            questions = data.get('questions', [])

            # 解析檔名
            file_info = self.parse_filename(json_file.name)

            # 計算統計資料
            answered_questions = sum(1 for q in questions if q.get('answer') is not None)

            exams_data.append({
                'file': json_file,
                'file_info': file_info,
                'total_questions': metadata.get('total_questions', len(questions)),
                'answered_questions': answered_questions,
                'parsing_method': metadata.get('parsing_method', 'N/A')
            })

        # 按年份和科目排序
        exams_data.sort(key=lambda x: (x['file_info']['year'], x['file_info']['subject']))

        # 生成 HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考題報告索引</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>📚 考題報告索引</h1>
            <div class="subtitle">不動產經紀人考試題目總覽</div>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">📊 總體統計</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">總科目數</span>
                    <span class="metadata-value">{len(exams_data)} 科</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">總題目數</span>
                    <span class="metadata-value">{sum(e['total_questions'] for e in exams_data)} 題</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">已有答案</span>
                    <span class="metadata-value">{sum(e['answered_questions'] for e in exams_data)} 題</span>
                </div>
            </div>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">📋 考試科目列表</h2>
            <div class="exam-grid">
"""

        for exam in exams_data:
            file_info = exam['file_info']
            html_filename = exam['file'].stem + '.html'

            html += f"""
                <div class="exam-card" onclick="window.location.href='{html_filename}'">
                    <div class="exam-title">{file_info['display']}</div>
                    <div style="color: #666; font-size: 0.95em; margin-bottom: 10px;">
                        {file_info['subject']}
                    </div>
                    <div class="exam-stats">
                        <div class="stat-badge">📝 {exam['total_questions']} 題</div>
                        <div class="stat-badge">✅ {exam['answered_questions']} 題有答案</div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.85em; color: #999;">
                        解析方式：{exam['parsing_method']}
                    </div>
                </div>
"""

        html += f"""
            </div>
        </div>

        <div style="text-align: center; color: #999; margin-top: 30px; padding: 20px;">
            生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html

    def generate_html_for_json(self, json_file: Path) -> str:
        """為單個 JSON 檔案生成 HTML"""
        # 讀取 JSON 資料
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metadata = data.get('metadata', {})
        questions = data.get('questions', [])

        # 解析檔名獲取年份和科目
        file_info = self.parse_filename(json_file.name)

        # 計算統計資料
        answered_questions = sum(1 for q in questions if q.get('answer') is not None)

        # 生成 HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_info['display']} - 考題報告</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>{file_info['display']}</h1>
            <div class="subtitle">{file_info['subject']}</div>
        </div>

        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item">← 返回索引</a></li>
                <li><button onclick="window.print()" class="nav-item">🖨️ 列印</button></li>
            </ul>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">📋 基本資訊</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">考試年份</span>
                    <span class="metadata-value">{file_info['year']}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">考試科目</span>
                    <span class="metadata-value">{file_info['subject']}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">題目總數</span>
                    <span class="metadata-value">{metadata.get('total_questions', len(questions))} 題</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">已有答案</span>
                    <span class="metadata-value">{answered_questions} 題</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">題目檔案</span>
                    <span class="metadata-value">{metadata.get('question_file', 'N/A')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">答案檔案</span>
                    <span class="metadata-value">{metadata.get('answer_file', 'N/A')}</span>
                </div>
            </div>
        </div>
"""

        # 生成每個題目的 HTML
        for question in questions:
            html += self.generate_question_html(question)

        html += f"""
        <div style="text-align: center; color: #999; margin-top: 30px; padding: 20px;">
            生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html

    def generate_question_html(self, question: Dict[str, Any]) -> str:
        """生成單個題目的 HTML"""
        question_number = question.get('question_number', 'N/A')
        question_text = question.get('question_text', '')
        options = question.get('options', {})
        correct_answer = question.get('answer')

        # 生成答案標籤
        if correct_answer:
            answer_badge = f'<div class="correct-answer-badge">正確答案：{correct_answer}</div>'
        else:
            answer_badge = '<div class="no-answer-badge">答案未提供</div>'

        html = f"""
        <div class="question-card">
            <div class="question-header">
                <div class="question-number">第 {question_number} 題</div>
                {answer_badge}
            </div>

            <div class="question-content">
                <div class="question-text">{question_text}</div>

                <div class="options-section">
"""

        # 生成選項
        for option_letter in ['A', 'B', 'C', 'D']:
            option_text = options.get(option_letter, '')
            if not option_text:
                continue

            is_correct = option_letter == correct_answer
            option_class = 'correct' if is_correct else ''

            html += f"""
                    <div class="option-card {option_class}">
                        <div class="option-header">
                            <div class="option-letter">{option_letter}</div>
                            <div class="option-text">{option_text}</div>
                        </div>
                    </div>
"""

        html += """
                </div>
            </div>
        </div>
"""
        return html

    def process_all_files(self):
        """處理所有 JSON 檔案"""
        # 找到所有 JSON 檔案
        json_files = sorted(self.input_dir.glob("*_mapped.json"))

        if not json_files:
            logger.warning(f"在 {self.input_dir} 中找不到 JSON 檔案")
            return

        logger.info(f"找到 {len(json_files)} 個 JSON 檔案")

        # 生成 CSS
        css_file = self.output_dir / "styles" / "main.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_css())
        logger.info(f"✅ CSS 已生成：{css_file}")

        # 生成每個 JSON 的 HTML
        for json_file in json_files:
            html_file = self.output_dir / f"{json_file.stem}.html"
            html_content = self.generate_html_for_json(json_file)

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"✅ HTML 已生成：{html_file}")

        # 生成索引頁面
        index_file = self.output_dir / "index.html"
        index_content = self.generate_index_page(json_files)

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        logger.info(f"✅ 索引頁面已生成：{index_file}")

        # 生成摘要
        logger.info("=" * 60)
        logger.info("HTML 轉換完成摘要")
        logger.info("=" * 60)
        logger.info(f"處理檔案數：{len(json_files)}")
        logger.info(f"輸出目錄：{self.output_dir}")
        logger.info(f"索引頁面：{index_file}")
        logger.info("=" * 60)


def main():
    """主函數"""
    # 設定路徑
    base_path = Path("/home/bheadwei/LegalStatuteAnalysis")
    input_dir = base_path / "output" / "qa_mapped"
    output_dir = base_path / "output" / "html_qa_reports"

    logger.info("開始 QA Mapped 結果 HTML 轉換...")
    logger.info(f"輸入目錄：{input_dir}")
    logger.info(f"輸出目錄：{output_dir}")

    try:
        generator = QAMappedHTMLGenerator(
            input_dir=str(input_dir),
            output_dir=str(output_dir)
        )
        generator.process_all_files()

        logger.info("✅ HTML 轉換成功完成！")
        return True

    except Exception as e:
        logger.error(f"❌ HTML 轉換失敗：{e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
