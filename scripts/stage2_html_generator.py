#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二階段：版面設計與HTML生成
生成法條講義的HTML頁面，包含法條外框、題目排版和統計頁面
"""

import json
import os
from typing import Dict, List, Any
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HTMLGenerator:
    def __init__(self, base_path: str = "/home/bheadwei/LegalStatuteAnalysis_V2"):
        self.base_path = base_path
        self.results_path = os.path.join(base_path, "results")
        self.output_path = os.path.join(base_path, "output")
        
        # 確保輸出目錄存在
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(os.path.join(self.output_path, "styles"), exist_ok=True)
        os.makedirs(os.path.join(self.output_path, "assets"), exist_ok=True)
        
        # 載入整合資料
        self.integrated_data = self.load_integrated_data()
        self.statistics = self.load_statistics()
        
    def load_integrated_data(self) -> Dict[str, Any]:
        """載入第一階段整合的資料"""
        integrated_file = os.path.join(self.results_path, "integrated_data_stage1.json")
        logger.info(f"載入整合資料: {integrated_file}")
        
        with open(integrated_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_statistics(self) -> Dict[str, Any]:
        """載入統計資料"""
        stats_file = os.path.join(self.results_path, "statistics_stage1.json")
        logger.info(f"載入統計資料: {stats_file}")
        
        with open(stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_css(self) -> str:
        """生成CSS樣式"""
        css_content = """
/* 法條講義樣式 */
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
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* 頁面標題 */
.page-header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.page-header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
    font-weight: 700;
}

.page-header .subtitle {
    font-size: 1.2em;
    opacity: 0.9;
}

/* 法條外框樣式 */
.law-article {
    background: white;
    border: 3px solid #2c3e50;
    border-radius: 15px;
    margin-bottom: 30px;
    padding: 25px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.law-article:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.law-header {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 15px 20px;
    margin: -25px -25px 20px -25px;
    border-radius: 12px 12px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.law-title {
    font-size: 1.4em;
    font-weight: 700;
}

.law-meta {
    font-size: 0.9em;
    opacity: 0.9;
}

.law-content {
    font-size: 1.1em;
    line-height: 1.8;
    text-align: justify;
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #3498db;
}

.law-item {
    margin-bottom: 12px;
    padding-left: 8px;
    line-height: 1.7;
    text-indent: -1em;
    padding-left: 1em;
}

.law-paragraph {
    margin-bottom: 8px;
    line-height: 1.7;
}

/* 題目區域 */
.questions-section {
    margin-top: 25px;
    padding-top: 20px;
    border-top: 2px solid #ecf0f1;
}

.questions-title {
    font-size: 1.3em;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
}

.questions-title::before {
    content: "📝";
    margin-right: 10px;
    font-size: 1.2em;
}

.question-item {
    background: #fff;
    border: 2px solid #e74c3c;
    border-radius: 10px;
    margin-bottom: 15px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.question-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.question-number {
    background: #e74c3c;
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1.1em;
}

.question-points {
    background: #f39c12;
    color: white;
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 0.9em;
    font-weight: 500;
}

.question-content {
    font-size: 1.1em;
    line-height: 1.7;
    margin-bottom: 15px;
    font-weight: 500;
}

.options-list {
    list-style: none;
}

.option-item {
    display: flex;
    align-items: flex-start;
    margin-bottom: 10px;
    padding: 12px;
    border-radius: 8px;
    transition: background-color 0.2s ease;
}

.option-item:hover {
    background-color: #f8f9fa;
}

.option-key {
    background: #3498db;
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    margin-right: 15px;
    flex-shrink: 0;
}

.option-content {
    flex: 1;
    line-height: 1.6;
}

.option-law-ref {
    font-size: 0.9em;
    color: #7f8c8d;
    font-style: italic;
    margin-top: 5px;
}

.correct-answer {
    background: #d4edda;
    border-color: #28a745;
}

.correct-answer .option-key {
    background: #28a745;
}

/* 統計頁面樣式 */
.statistics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #3498db;
}

.stat-card h3 {
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 1.3em;
    display: flex;
    align-items: center;
}

.stat-card h3::before {
    content: "📊";
    margin-right: 10px;
}

.stat-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #ecf0f1;
}

.stat-item:last-child {
    border-bottom: none;
}

.stat-label {
    font-weight: 500;
    color: #555;
}

.stat-value {
    font-weight: 600;
    color: #2c3e50;
    background: #ecf0f1;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 0.9em;
}

/* 導航樣式 */
.navigation {
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-list {
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.nav-item {
    background: #3498db;
    color: white;
    padding: 8px 15px;
    border-radius: 20px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.3s ease;
}

.nav-item:hover {
    background: #2980b9;
    color: white;
    text-decoration: none;
}

.nav-item.active {
    background: #e74c3c;
}

/* 分頁樣式 */
.pagination {
    text-align: center;
    margin-top: 30px;
}

.page-info {
    background: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 響應式設計 */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .page-header h1 {
        font-size: 2em;
    }
    
    .law-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .question-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .statistics-grid {
        grid-template-columns: 1fr;
    }
    
    .nav-list {
        justify-content: center;
    }
}

/* 列印樣式 */
@media print {
    body {
        background: white;
    }
    
    .law-article {
        break-inside: avoid;
        box-shadow: none;
        border: 2px solid #2c3e50;
    }
    
    .question-item {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #e74c3c;
    }
    
    .navigation {
        display: none;
    }
    
    .page-header {
        background: #2c3e50;
        color: white;
    }
}
"""
        return css_content
    
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

    def generate_law_page(self, law_id: str, law_data: Dict[str, Any]) -> str:
        """生成單個法條頁面"""
        questions = self.integrated_data['law_question_mapping'].get(law_id, [])
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{law_data['law_name']} 第{law_data['article_no_main']}條</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>{law_data['law_name']}</h1>
            <div class="subtitle">第 {law_data['article_no_main']} 條</div>
        </div>
        
        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item">首頁</a></li>
                <li><a href="statistics.html" class="nav-item">統計</a></li>
                <li><a href="laws.html" class="nav-item">法條列表</a></li>
            </ul>
        </div>
        
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
            
            {self.generate_questions_section(questions) if questions else '<div class="questions-section"><div class="questions-title">本條文暫無相關考題</div></div>'}
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_questions_section(self, questions: List[Dict[str, Any]]) -> str:
        """生成題目區域HTML"""
        if not questions:
            return ""
        
        # 將題目按question_id分組，避免重複顯示
        unique_questions = {}
        for question in questions:
            question_id = question['question_id']
            if question_id not in unique_questions:
                unique_questions[question_id] = question
        
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
    
    def generate_laws_index_page(self) -> str:
        """生成法條列表頁面"""
        laws_with_questions = []
        laws_without_questions = []
        
        for law_id, law_data in self.integrated_data['laws'].items():
            if law_id in self.integrated_data['law_question_mapping']:
                laws_with_questions.append((law_id, law_data))
            else:
                laws_without_questions.append((law_id, law_data))
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>法條列表 - 不動產經紀相關法規講義</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>法條列表</h1>
            <div class="subtitle">不動產經紀相關法規講義</div>
        </div>
        
        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item">首頁</a></li>
                <li><a href="statistics.html" class="nav-item">統計</a></li>
                <li><a href="laws.html" class="nav-item active">法條列表</a></li>
            </ul>
        </div>
        
        <div class="statistics-grid">
            <div class="stat-card">
                <h3>有考題的法條</h3>
                <div class="stat-item">
                    <span class="stat-label">總數</span>
                    <span class="stat-value">{len(laws_with_questions)} 條</span>
                </div>
            </div>
            <div class="stat-card">
                <h3>無考題的法條</h3>
                <div class="stat-item">
                    <span class="stat-label">總數</span>
                    <span class="stat-value">{len(laws_without_questions)} 條</span>
                </div>
            </div>
        </div>
        
        <div class="law-article">
            <div class="law-header">
                <div class="law-title">有考題的法條 ({len(laws_with_questions)} 條)</div>
            </div>
            
            <div class="law-content">
        """
        
        # 按法規分組
        laws_by_category = {}
        for law_id, law_data in laws_with_questions:
            category = law_data['category']
            if category not in laws_by_category:
                laws_by_category[category] = []
            laws_by_category[category].append((law_id, law_data))
        
        for category, laws in laws_by_category.items():
            html += f'<h4 style="color: #2c3e50; margin: 20px 0 10px 0; border-bottom: 2px solid #3498db; padding-bottom: 5px;">{category}</h4>'
            html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; margin-bottom: 20px;">'
            
            for law_id, law_data in laws:
                # 計算唯一題目數量，避免重複計算
                questions = self.integrated_data['law_question_mapping'][law_id]
                unique_questions = {}
                for question in questions:
                    question_id = question['question_id']
                    if question_id not in unique_questions:
                        unique_questions[question_id] = question
                question_count = len(unique_questions)
                
                html += f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #e74c3c;">
                    <a href="law_{law_id}.html" style="text-decoration: none; color: #2c3e50;">
                        <div style="font-weight: 600; margin-bottom: 5px;">
                            {law_data['law_name']} 第 {law_data['article_no_main']} 條
                        </div>
                        <div style="font-size: 0.9em; color: #7f8c8d;">
                            {question_count} 題 | {law_data['authority']}
                        </div>
                    </a>
                </div>
                """
            
            html += '</div>'
        
        html += """
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_statistics_page(self) -> str:
        """生成統計頁面"""
        stats = self.statistics
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>統計資料 - 不動產經紀相關法規講義</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>統計資料</h1>
            <div class="subtitle">不動產經紀相關法規講義</div>
        </div>
        
        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item">首頁</a></li>
                <li><a href="statistics.html" class="nav-item active">統計</a></li>
                <li><a href="laws.html" class="nav-item">法條列表</a></li>
            </ul>
        </div>
        
        <div class="statistics-grid">
            <div class="stat-card">
                <h3>法條統計</h3>
                <div class="stat-item">
                    <span class="stat-label">總法條數</span>
                    <span class="stat-value">{stats['law_statistics']['total_laws']} 條</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">有考題的法條</span>
                    <span class="stat-value">{stats['law_statistics']['laws_with_questions']} 條</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">無考題的法條</span>
                    <span class="stat-value">{stats['law_statistics']['laws_without_questions']} 條</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">考題覆蓋率</span>
                    <span class="stat-value">{stats['law_statistics']['laws_with_questions']/stats['law_statistics']['total_laws']*100:.1f}%</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>題目統計</h3>
                <div class="stat-item">
                    <span class="stat-label">總題目數</span>
                    <span class="stat-value">{stats['question_statistics']['total_questions']} 題</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">總選項數</span>
                    <span class="stat-value">{stats['question_statistics']['total_options']} 個</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">正確答案</span>
                    <span class="stat-value">{stats['question_statistics']['correct_options']} 個</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">平均選項數</span>
                    <span class="stat-value">{stats['question_statistics']['average_options_per_question']:.1f} 個/題</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>對應關係統計</h3>
                <div class="stat-item">
                    <span class="stat-label">題目-法條對應</span>
                    <span class="stat-value">{stats['mapping_statistics']['question_law_mappings']} 個</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">法條-題目對應</span>
                    <span class="stat-value">{stats['mapping_statistics']['law_question_mappings']} 個</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">平均法條/題目</span>
                    <span class="stat-value">{stats['mapping_statistics']['average_laws_per_question']:.1f} 條</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">平均題目/法條</span>
                    <span class="stat-value">{stats['mapping_statistics']['average_questions_per_law']:.1f} 題</span>
                </div>
            </div>
        </div>
        
        <div class="statistics-grid">
            <div class="stat-card">
                <h3>法規類別分布</h3>
        """
        
        for category, count in stats['law_statistics']['categories'].items():
            percentage = count / stats['law_statistics']['total_laws'] * 100
            html += f"""
                <div class="stat-item">
                    <span class="stat-label">{category}</span>
                    <span class="stat-value">{count} 條 ({percentage:.1f}%)</span>
                </div>
            """
        
        html += """
            </div>
            
            <div class="stat-card">
                <h3>主管機關分布</h3>
        """
        
        for authority, count in stats['law_statistics']['authorities'].items():
            percentage = count / stats['law_statistics']['total_laws'] * 100
            html += f"""
                <div class="stat-item">
                    <span class="stat-label">{authority}</span>
                    <span class="stat-value">{count} 條 ({percentage:.1f}%)</span>
                </div>
            """
        
        html += """
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_index_page(self) -> str:
        """生成首頁"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>不動產經紀相關法規講義</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>不動產經紀相關法規講義</h1>
            <div class="subtitle">113年專門職業及技術人員高等考試建築師、32類科技師（含第二次食品技師）、大地工程技師考試分階段考試暨普通考試不動產經紀人、記帳士考試試題</div>
        </div>
        
        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item active">首頁</a></li>
                <li><a href="statistics.html" class="nav-item">統計</a></li>
                <li><a href="laws.html" class="nav-item">法條列表</a></li>
            </ul>
        </div>
        
        <div class="statistics-grid">
            <div class="stat-card">
                <h3>考試資訊</h3>
                <div class="stat-item">
                    <span class="stat-label">科目名稱</span>
                    <span class="stat-value">不動產經紀相關法規概要</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">考試時間</span>
                    <span class="stat-value">1 小時 30 分</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">題目總數</span>
                    <span class="stat-value">{self.integrated_data['metadata']['total_questions']} 題</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">法條總數</span>
                    <span class="stat-value">{self.integrated_data['metadata']['total_laws']} 條</span>
                </div>
            </div>
            
            <div class="stat-card">
                <h3>重點法條</h3>
                <div class="stat-item">
                    <span class="stat-label">有考題的法條</span>
                    <span class="stat-value">{self.statistics['law_statistics']['laws_with_questions']} 條</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">考題覆蓋率</span>
                    <span class="stat-value">{self.statistics['law_statistics']['laws_with_questions']/self.statistics['law_statistics']['total_laws']*100:.1f}%</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">平均題目/法條</span>
                    <span class="stat-value">{self.statistics['mapping_statistics']['average_questions_per_law']:.1f} 題</span>
                </div>
            </div>
        </div>
        
        <div class="law-article">
            <div class="law-header">
                <div class="law-title">使用說明</div>
            </div>
            
            <div class="law-content">
                <h4>📚 講義特色</h4>
                <ul style="margin: 15px 0; padding-left: 20px;">
                    <li>以法條為中心，逐條列出並用外框框住</li>
                    <li>每條法條下方列出相關的考題和選項</li>
                    <li>正確答案以綠色標示，錯誤答案以紅色標示</li>
                    <li>提供詳細的統計資料和分析</li>
                </ul>
                
                <h4>🎯 學習建議</h4>
                <ul style="margin: 15px 0; padding-left: 20px;">
                    <li>重點複習有考題的 {self.statistics['law_statistics']['laws_with_questions']} 條法條</li>
                    <li>理解每條法條的核心概念和應用</li>
                    <li>熟悉題目類型和解題技巧</li>
                    <li>定期檢視統計資料掌握學習進度</li>
                </ul>
                
                <h4>📖 瀏覽方式</h4>
                <ul style="margin: 15px 0; padding-left: 20px;">
                    <li><strong>法條列表</strong>：查看所有法條，重點關注有考題的法條</li>
                    <li><strong>統計資料</strong>：了解法條分布和考題統計</li>
                    <li><strong>個別法條</strong>：點擊法條名稱查看詳細內容和相關考題</li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def generate_all_pages(self) -> None:
        """生成所有頁面"""
        logger.info("開始生成HTML頁面...")
        
        # 生成CSS
        css_file = os.path.join(self.output_path, "styles", "main.css")
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_css())
        logger.info(f"CSS樣式已生成: {css_file}")
        
        # 生成首頁
        index_file = os.path.join(self.output_path, "index.html")
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_index_page())
        logger.info(f"首頁已生成: {index_file}")
        
        # 生成統計頁面
        stats_file = os.path.join(self.output_path, "statistics.html")
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_statistics_page())
        logger.info(f"統計頁面已生成: {stats_file}")
        
        # 生成法條列表頁面
        laws_file = os.path.join(self.output_path, "laws.html")
        with open(laws_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_laws_index_page())
        logger.info(f"法條列表頁面已生成: {laws_file}")
        
        # 生成個別法條頁面
        law_pages_count = 0
        for law_id, law_data in self.integrated_data['laws'].items():
            if law_id in self.integrated_data['law_question_mapping']:
                law_file = os.path.join(self.output_path, f"law_{law_id}.html")
                with open(law_file, 'w', encoding='utf-8') as f:
                    f.write(self.generate_law_page(law_id, law_data))
                law_pages_count += 1
        
        logger.info(f"已生成 {law_pages_count} 個法條頁面")
        
        # 生成README
        readme_content = f"""
# 不動產經紀相關法規講義

## 檔案說明

- `index.html` - 首頁
- `statistics.html` - 統計資料頁面
- `laws.html` - 法條列表頁面
- `law_*.html` - 個別法條頁面
- `styles/main.css` - 主要樣式檔案

## 統計摘要

- 總題目數: {self.integrated_data['metadata']['total_questions']} 題
- 總法條數: {self.integrated_data['metadata']['total_laws']} 條
- 有考題的法條數: {self.statistics['law_statistics']['laws_with_questions']} 條
- 考題覆蓋率: {self.statistics['law_statistics']['laws_with_questions']/self.statistics['law_statistics']['total_laws']*100:.1f}%

## 生成時間

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        readme_file = os.path.join(self.output_path, "README.md")
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        logger.info(f"README已生成: {readme_file}")

def main():
    """主函數"""
    logger.info("開始第二階段HTML生成...")
    
    try:
        # 初始化生成器
        generator = HTMLGenerator()
        
        # 生成所有頁面
        generator.generate_all_pages()
        
        # 輸出摘要
        logger.info("=" * 50)
        logger.info("第二階段HTML生成完成摘要:")
        logger.info(f"輸出目錄: {generator.output_path}")
        logger.info(f"總題目數: {generator.integrated_data['metadata']['total_questions']}")
        logger.info(f"總法條數: {generator.integrated_data['metadata']['total_laws']}")
        logger.info(f"有考題的法條數: {generator.statistics['law_statistics']['laws_with_questions']}")
        logger.info(f"生成的法條頁面數: {len(generator.integrated_data['law_question_mapping'])}")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"第二階段HTML生成失敗: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
