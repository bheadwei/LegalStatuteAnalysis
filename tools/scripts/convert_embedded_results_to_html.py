#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embedding 結果 HTML 轉換器
將 embedding 匹配結果轉換成結構化的 HTML 報告
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


class EmbeddedResultsHTMLGenerator:
    def __init__(self, input_dir: str, output_dir: str):
        """
        初始化 HTML 生成器

        Args:
            input_dir: embedding 結果檔案所在目錄
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

        格式：112190_1201_民法概要_mapped_embedded.json
        """
        import re

        # 移除副檔名和後綴
        name = filename.replace('_mapped_embedded.json', '').replace('_mapped_embedded', '')
        name = name.replace('.json', '')

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

    def collect_law_statistics(self, question_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """收集題目中所有匹配法條的統計資訊"""
        law_counts = {}  # 法條ID -> 出現次數
        law_details = {}  # 法條ID -> 法條詳細資訊

        for question in question_matches:
            for option in question.get('options', []):
                for article in option.get('matched_articles', [])[:3]:  # 只統計前3個最相關
                    law_id = article.get('id')
                    if law_id:
                        law_counts[law_id] = law_counts.get(law_id, 0) + 1
                        if law_id not in law_details:
                            law_details[law_id] = {
                                'law_name': article.get('law_name'),
                                'article_no': article.get('article_no_main'),
                                'category': article.get('category')
                            }

        # 排序：按出現次數排序
        sorted_laws = sorted(law_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            'total_laws': len(law_counts),
            'top_laws': [(law_id, count, law_details.get(law_id, {})) for law_id, count in sorted_laws[:10]],
            'law_counts': law_counts,
            'law_details': law_details
        }

    def generate_css(self) -> str:
        """生成CSS樣式"""
        return """
/* Embedding 結果報告樣式 */
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
    max-width: 1400px;
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
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
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
    margin-bottom: 20px;
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
    margin-bottom: 15px;
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

/* 匹配法條區域 */
.matched-articles {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 2px solid #ddd;
}

.matched-articles-title {
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 12px;
    font-size: 1.05em;
}

.article-item {
    background: white;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #e74c3c;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}

.article-item:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left-color: #c0392b;
}

.article-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.article-title {
    font-weight: 600;
    color: #e74c3c;
    font-size: 1.05em;
}

.similarity-badge {
    background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 0.9em;
    font-weight: 600;
}

.article-meta {
    display: flex;
    gap: 15px;
    margin-bottom: 10px;
    font-size: 0.95em;
    color: #666;
}

.article-meta-item {
    display: flex;
    align-items: center;
}

.article-meta-item::before {
    content: "•";
    margin-right: 5px;
    color: #3498db;
    font-weight: bold;
}

.article-content {
    background: #f8f9fa;
    padding: 12px;
    border-radius: 6px;
    font-size: 0.95em;
    line-height: 1.6;
    color: #555;
    max-height: 200px;
    overflow-y: auto;
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

/* PDF 下載按鈕 */
.pdf-button {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    font-size: 0.95em;
    border: none;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.pdf-button:hover {
    background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.pdf-button::before {
    content: "📄";
    font-size: 1.2em;
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

    .article-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
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

    /* 修復滾動條問題：列印時顯示完整內容 */
    .article-content {
        max-height: none !important;
        overflow: visible !important;
    }
}

/* 標籤頁樣式 */
.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid #e0e0e0;
}

.tab-button {
    background: none;
    border: none;
    padding: 12px 24px;
    font-size: 1.1em;
    font-weight: 600;
    color: #666;
    cursor: pointer;
    transition: all 0.3s ease;
    border-bottom: 3px solid transparent;
}

.tab-button:hover {
    color: #3498db;
}

.tab-button.active {
    color: #3498db;
    border-bottom-color: #3498db;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

/* 年份卡片 */
.year-section {
    margin-bottom: 25px;
}

.year-header {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 10px 10px 0 0;
    font-size: 1.3em;
    font-weight: 700;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.year-stats {
    font-size: 0.8em;
    opacity: 0.9;
}

.year-content {
    background: white;
    border: 2px solid #3498db;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 20px;
}

.subject-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 15px;
}

/* 法條卡片 */
.law-item {
    background: white;
    border: 2px solid #e0e0e0;
    border-left: 4px solid #e74c3c;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
}

.law-item:hover {
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transform: translateX(5px);
}

.law-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.law-title {
    font-size: 1.2em;
    font-weight: 700;
    color: #2c3e50;
}

.law-count-badge {
    background: #e74c3c;
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1em;
}

.related-exams {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e0e0e0;
}

.related-exams-title {
    font-weight: 600;
    color: #666;
    margin-bottom: 10px;
    font-size: 0.95em;
}

.exam-tag {
    display: inline-block;
    background: #f8f9fa;
    border: 1px solid #ddd;
    padding: 6px 12px;
    border-radius: 15px;
    margin: 5px 5px 5px 0;
    font-size: 0.9em;
    color: #555;
    text-decoration: none;
    transition: all 0.2s ease;
}

.exam-tag:hover {
    background: #3498db;
    color: white;
    border-color: #3498db;
}
"""

    def generate_index_page(self, json_files: List[Path]) -> str:
        """生成索引頁面（按年份和法條分類）"""
        # 收集所有文件的資訊
        years_data = {}  # year -> [{file_info, metadata, law_stats}, ...]
        all_laws = {}  # law_id -> {details, count, exam_files}
        law_articles_map = {}  # law_id -> {law_details, full_content, related_questions[]}

        for json_file in json_files:
            # 讀取 JSON 資料
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            question_matches = data.get('question_matches', [])

            # 解析檔名
            file_info = self.parse_filename(json_file.name)
            year = file_info['year']

            # 收集法條統計
            law_stats = self.collect_law_statistics(question_matches)

            # 按年份分類
            if year not in years_data:
                years_data[year] = []

            years_data[year].append({
                'file': json_file,
                'file_info': file_info,
                'metadata': metadata,
                'law_stats': law_stats
            })

            # 收集所有法條
            for law_id, count, details in law_stats['top_laws']:
                if law_id not in all_laws:
                    all_laws[law_id] = {
                        'details': details,
                        'total_count': 0,
                        'exam_files': []
                    }
                all_laws[law_id]['total_count'] += count
                all_laws[law_id]['exam_files'].append({
                    'file': json_file,
                    'file_info': file_info,
                    'count': count
                })

            # 收集法條與題目的對應關係（用於第三個分頁：按法條瀏覽題目）
            for question in question_matches:
                question_no = question.get('question_number')
                question_text = question.get('question_text', '')

                # 遍歷所有選項的匹配法條
                for option in question.get('options', []):
                    for article in option.get('matched_articles', [])[:3]:  # 只取前3個最相關的
                        law_id = article.get('id')
                        if law_id:
                            if law_id not in law_articles_map:
                                law_articles_map[law_id] = {
                                    'law_name': article.get('law_name'),
                                    'article_no_main': article.get('article_no_main'),
                                    'content': article.get('content'),
                                    'category': article.get('category'),
                                    'authority': article.get('authority'),
                                    'related_questions': []
                                }

                            # 避免重複加入同一題
                            existing_q = [q for q in law_articles_map[law_id]['related_questions']
                                         if q['question_no'] == question_no and q['exam_file'] == json_file.stem]
                            if not existing_q:
                                law_articles_map[law_id]['related_questions'].append({
                                    'question_no': question_no,
                                    'question_text': question_text,
                                    'file_info': file_info,
                                    'exam_file': json_file.stem,
                                    'similarity': article.get('similarity', 0)
                                })

        # 排序法條（按總出現次數）
        sorted_all_laws = sorted(all_laws.items(), key=lambda x: x[1]['total_count'], reverse=True)[:20]

        # 生成 HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embedding 結果報告 - 索引</title>
    <link rel="stylesheet" href="styles/main.css">
    <script>
        function switchTab(tabName) {{
            // 隱藏所有標籤內容
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => c.classList.remove('active'));

            // 移除所有按鈕的 active 狀態
            const buttons = document.querySelectorAll('.tab-button');
            buttons.forEach(b => b.classList.remove('active'));

            // 顯示選中的標籤
            document.getElementById(tabName + '-content').classList.add('active');
            document.getElementById(tabName + '-btn').classList.add('active');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>Embedding 結果報告</h1>
            <div class="subtitle">法條智能匹配分析</div>
        </div>

        <div class="metadata-card">
            <div class="tabs">
                <button id="year-btn" class="tab-button active" onclick="switchTab('year')">📅 按年份瀏覽</button>
                <button id="law-btn" class="tab-button" onclick="switchTab('law')">📚 按高頻法條瀏覽</button>
                <button id="article-btn" class="tab-button" onclick="switchTab('article')">📖 按法條瀏覽題目</button>
            </div>

            <!-- 按年份瀏覽 -->
            <div id="year-content" class="tab-content active">
"""

        # 生成按年份分類的內容
        for year in sorted(years_data.keys(), reverse=True):
            exams = years_data[year]
            total_questions = sum(e['metadata'].get('total_questions', 0) for e in exams)

            html += f"""
                <div class="year-section">
                    <div class="year-header">
                        <span>{year}</span>
                        <span class="year-stats">{len(exams)} 個科目 | {total_questions} 題</span>
                    </div>
                    <div class="year-content">
                        <div class="subject-grid">
"""

            for exam in exams:
                file_info = exam['file_info']
                metadata = exam['metadata']
                law_stats = exam['law_stats']
                html_filename = exam['file'].stem + '.html'

                html += f"""
                            <div class="metadata-item" style="padding: 20px; cursor: pointer;" onclick="window.location.href='{html_filename}'">
                                <div>
                                    <div style="font-size: 1.2em; font-weight: 600; color: #2c3e50; margin-bottom: 8px;">
                                        {file_info['subject']}
                                    </div>
                                    <div style="color: #666; font-size: 0.9em; margin-bottom: 8px;">
                                        題目：{metadata.get('total_questions', 0)} | 選項：{metadata.get('total_options_processed', 0)}
                                    </div>
                                    <div style="color: #999; font-size: 0.85em;">
                                        涉及 {law_stats['total_laws']} 個法條
                                    </div>
                                </div>
                                <div style="color: #3498db; font-size: 1.5em;">→</div>
                            </div>
"""

            html += """
                        </div>
                    </div>
                </div>
"""

        html += """
            </div>

            <!-- 按高頻法條瀏覽 -->
            <div id="law-content" class="tab-content">
                <p style="color: #666; margin-bottom: 20px;">以下是所有考試中最常被匹配的法條（前20名），點擊可查看相關考試科目</p>
"""

        # 生成法條統計
        for law_id, law_data in sorted_all_laws:
            details = law_data['details']
            total_count = law_data['total_count']
            exam_files = law_data['exam_files']

            html += f"""
                <div class="law-item">
                    <div class="law-header">
                        <div class="law-title">
                            {details.get('law_name', 'N/A')} 第 {details.get('article_no', 'N/A')} 條
                        </div>
                        <div class="law-count-badge">總計出現 {total_count} 次</div>
                    </div>
                    <div style="color: #666; font-size: 0.95em; margin-bottom: 10px;">
                        {details.get('category', 'N/A')} | 法條代碼：{law_id}
                    </div>
                    <div class="related-exams">
                        <div class="related-exams-title">📋 相關考試科目：</div>
"""

            for exam_file in exam_files:
                file_info = exam_file['file_info']
                count = exam_file['count']
                html_filename = exam_file['file'].stem + '.html'

                html += f"""
                        <a href="{html_filename}" class="exam-tag">
                            {file_info['display']} ({count}次)
                        </a>
"""

            html += """
                    </div>
                </div>
"""

        html += """
            </div>

            <!-- 按法條瀏覽題目 -->
            <div id="article-content" class="tab-content">
                <p style="color: #666; margin-bottom: 20px;">以下按法條分類，顯示每個法條及其相關考題。法條按相關題目數量排序，點擊題目標籤可跳轉至該題</p>
"""

        # 排序法條（按相關題目數量）
        sorted_law_articles = sorted(law_articles_map.items(),
                                     key=lambda x: len(x[1]['related_questions']),
                                     reverse=True)

        # 生成法條與題目的對應內容
        for law_id, law_data in sorted_law_articles:
            law_name = law_data['law_name']
            article_no = law_data['article_no_main']
            content = law_data['content']
            category = law_data['category']
            authority = law_data['authority']
            related_questions = law_data['related_questions']

            html += f"""
                <div class="law-item" style="margin-bottom: 30px;">
                    <div class="law-header">
                        <div class="law-title">
                            {law_name} 第 {article_no} 條
                        </div>
                        <div class="law-count-badge">相關 {len(related_questions)} 題</div>
                    </div>
                    <div style="color: #666; font-size: 0.95em; margin-bottom: 15px;">
                        {category} | {authority} | 法條代碼：{law_id}
                    </div>

                    <!-- 法條內容 -->
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #e74c3c;">
                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 10px;">📜 法條內容：</div>
                        <div style="line-height: 1.8; color: #555;">
                            {self.format_article_content(content)}
                        </div>
                    </div>

                    <!-- 相關題目 -->
                    <div class="related-exams">
                        <div class="related-exams-title">📝 相關題目：</div>
"""

            # 按考試科目分組題目
            exam_groups = {}
            for q in related_questions:
                exam_file = q['exam_file']
                if exam_file not in exam_groups:
                    exam_groups[exam_file] = {
                        'file_info': q['file_info'],
                        'questions': []
                    }
                exam_groups[exam_file]['questions'].append(q)

            # 生成每個考試科目的題目列表
            for exam_file, exam_group in exam_groups.items():
                file_info = exam_group['file_info']
                questions = exam_group['questions']

                html += f"""
                        <div style="margin-bottom: 15px;">
                            <div style="font-weight: 600; color: #2c3e50; margin-bottom: 8px;">
                                {file_info['display']}
                            </div>
"""

                for q in sorted(questions, key=lambda x: x['question_no']):
                    question_no = q['question_no']
                    question_text = q['question_text']
                    # 截斷過長的題目文字
                    if len(question_text) > 80:
                        question_text = question_text[:80] + '...'

                    html += f"""
                            <a href="{exam_file}.html#q{question_no}" class="exam-tag"
                               style="display: block; margin-bottom: 8px; padding: 10px 15px;"
                               title="{q['question_text']}">
                                第 {question_no} 題：{question_text}
                            </a>
"""

                html += """
                        </div>
"""

            html += """
                    </div>
                </div>
"""

        html += f"""
            </div>
        </div>

        <div class="metadata-card">
            <h3 style="color: #2c3e50;">ℹ️ 使用說明</h3>
            <ul style="line-height: 2; color: #555; margin-top: 10px; padding-left: 20px;">
                <li><strong>按年份瀏覽</strong>：依考試年份查看各科目的法條匹配結果</li>
                <li><strong>按高頻法條瀏覽</strong>：查看所有考試中最常出現的法條，快速定位重點法條</li>
                <li><strong>按法條瀏覽題目</strong>：依法條分類，查看每個法條及其相關考題，方便學習特定法條</li>
                <li>點擊任一科目、法條或題目標籤即可查看詳細的匹配結果</li>
            </ul>
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
        question_matches = data.get('question_matches', [])

        # 解析檔名獲取年份和科目
        file_info = self.parse_filename(json_file.name)

        # 檢查對應的 PDF 是否存在
        pdf_dir = self.output_dir.parent / "pdf_reports"
        pdf_file = pdf_dir / f"{json_file.stem}.pdf"
        has_pdf = pdf_file.exists()

        # 收集所有匹配的法條統計
        law_stats = self.collect_law_statistics(question_matches)

        # 生成 HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.get('source_file', json_file.name)} - Embedding 結果</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>{metadata.get('source_file', json_file.name)}</h1>
            <div class="subtitle">法條智能匹配結果</div>
        </div>

        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item">← 返回索引</a></li>
                {"<li><a href='../pdf_reports/" + json_file.stem + ".pdf' download class='pdf-button'>下載 PDF 檔案</a></li>" if has_pdf else "<li><button onclick='window.print()' class='pdf-button'>列印為 PDF</button></li>"}
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
                    <span class="metadata-value">{metadata.get('total_questions', 0)} 題</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">處理選項數</span>
                    <span class="metadata-value">{metadata.get('total_options_processed', 0)} 個</span>
                </div>
            </div>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">📚 高頻法條統計</h2>
            <p style="color: #666; margin-bottom: 15px;">以下是本次考試中最常被匹配的法條（前10名）</p>
            <div style="display: grid; gap: 10px;">
        """

        # 顯示前10個高頻法條
        for law_id, count, details in law_stats['top_laws']:
            html += f"""
                <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #e74c3c;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #2c3e50; margin-bottom: 5px;">
                                {details.get('law_name', 'N/A')} 第 {details.get('article_no', 'N/A')} 條
                            </div>
                            <div style="font-size: 0.9em; color: #666;">
                                {details.get('category', 'N/A')} | 法條代碼：{law_id}
                            </div>
                        </div>
                        <div style="background: #e74c3c; color: white; padding: 8px 15px; border-radius: 20px; font-weight: 600;">
                            出現 {count} 次
                        </div>
                    </div>
                </div>
        """

        html += """
            </div>
            <div style="margin-top: 15px; padding: 12px; background: #e8f4f8; border-radius: 8px; border-left: 4px solid #3498db;">
                <strong>💡 提示：</strong>高頻法條代表在本次考試中較常被考查，建議優先複習這些法條。
            </div>
        </div>
"""

        # 生成每個題目的 HTML
        for question in question_matches:
            html += self.generate_question_html(question, file_info)

        html += f"""
        <div style="text-align: center; color: #999; margin-top: 30px; padding: 20px;">
            生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html

    def format_article_content(self, content: str) -> str:
        """
        格式化法條內容，在編號後自動換行

        Args:
            content: 原始法條內容

        Returns:
            格式化後的 HTML 內容
        """
        import re

        if not content:
            return content

        # 處理數字編號（1、2、3 等）後面接空格的情況
        content = re.sub(r'(\d+)\s+', r'\1 ', content)

        # 在數字編號後插入換行（1 xxx、2 xxx、3 xxx）
        # 匹配：數字 + 空格 + 文字
        content = re.sub(r'(\d+\s+)(?=[^0-9])', r'<br>\1', content)

        # 在中文編號後插入換行（一、二、三、四、五、六、七、八、九、十）
        # 匹配：中文數字 + 頓號或句號 + 文字
        content = re.sub(r'([一二三四五六七八九十百千萬]+、)', r'<br>\1', content)

        # 移除開頭多餘的 <br>
        content = content.lstrip('<br>')

        return content

    def generate_question_html(self, question: Dict[str, Any], file_info: Dict[str, str]) -> str:
        """生成單個題目的 HTML"""
        question_no = question.get('question_number', 'N/A')
        html = f"""
        <div class="question-card" id="q{question_no}">
            <div class="question-header">
                <div class="question-number">第 {question_no} 題</div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 5px;">
                    <div style="font-size: 0.9em; opacity: 0.9;">{file_info['display']}</div>
                    <div class="correct-answer-badge">正確答案：{question.get('correct_answer', 'N/A')}</div>
                </div>
            </div>

            <div class="question-content">
                <div class="question-text">{question.get('question_text', '')}</div>

                <div class="options-section">
"""

        # 生成選項
        for option in question.get('options', []):
            is_correct = option.get('is_correct_answer', False)
            option_class = 'correct' if is_correct else ''

            html += f"""
                    <div class="option-card {option_class}">
                        <div class="option-header">
                            <div class="option-letter">{option.get('option_letter', '')}</div>
                            <div class="option-text">{option.get('option_text', '')}</div>
                        </div>
"""

            # 生成匹配的法條
            matched_articles = option.get('matched_articles', [])
            if matched_articles:
                html += """
                        <div class="matched-articles">
                            <div class="matched-articles-title">🎯 匹配法條（依相似度排序）</div>
"""

                for article in matched_articles[:5]:  # 只顯示前5個最相關的法條
                    similarity = article.get('similarity', 0)
                    similarity_percent = f"{similarity * 100:.2f}%"

                    html += f"""
                            <div class="article-item">
                                <div class="article-header">
                                    <div class="article-title">
                                        {article.get('law_name', 'N/A')} 第 {article.get('article_no_main', 'N/A')} 條
                                    </div>
                                    <div class="similarity-badge">相似度：{similarity_percent}</div>
                                </div>
                                <div class="article-meta">
                                    <div class="article-meta-item">{article.get('category', 'N/A')}</div>
                                    <div class="article-meta-item">{article.get('authority', 'N/A')}</div>
                                    <div class="article-meta-item">法條代碼：{article.get('id', 'N/A')}</div>
                                </div>
                                <div class="article-content">{self.format_article_content(article.get('content', 'N/A'))}</div>
                            </div>
"""

                html += """
                        </div>
"""

            html += """
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
        json_files = sorted(self.input_dir.glob("*.json"))

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
    input_dir = base_path / "output" / "embedded_results"
    output_dir = base_path / "output" / "html_reports"

    logger.info("開始 Embedding 結果 HTML 轉換...")
    logger.info(f"輸入目錄：{input_dir}")
    logger.info(f"輸出目錄：{output_dir}")

    try:
        generator = EmbeddedResultsHTMLGenerator(
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
