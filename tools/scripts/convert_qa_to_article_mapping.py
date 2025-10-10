#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考題對應法條 HTML 生成器
從 embedded_results 提取資料，生成以考題為中心的法條對應頁面
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QAArticleMappingGenerator:
    def __init__(self, input_dir: str, output_dir: str):
        """
        初始化考題-法條對應 HTML 生成器

        Args:
            input_dir: embedded_results 目錄
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
        """解析檔名，提取年份和科目資訊"""
        import re

        name = filename.replace('_mapped_embedded.json', '').replace('_mapped_embedded', '')
        name = name.replace('.json', '')

        match = re.match(r'(\d{3})(\d+)_(\d+)_(.+)', name)
        if match:
            year = match.group(1)
            exam_code = match.group(2) + match.group(3)
            subject = match.group(4)

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

    def collect_question_articles(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
        """收集一個題目所有選項相關的法條（去重）"""
        articles_dict = {}  # law_id -> article details

        for option in question.get('options', []):
            for article in option.get('matched_articles', [])[:3]:  # 前3個最相關
                law_id = article.get('id')
                if law_id and law_id not in articles_dict:
                    articles_dict[law_id] = {
                        'id': law_id,
                        'law_name': article.get('law_name'),
                        'article_no': article.get('article_no_main'),
                        'category': article.get('category'),
                        'authority': article.get('authority'),
                        'content': article.get('content'),
                        'similarity': article.get('similarity', 0)
                    }

        # 按相似度排序
        sorted_articles = sorted(articles_dict.values(), key=lambda x: x['similarity'], reverse=True)
        return sorted_articles

    def generate_css(self) -> str:
        """生成CSS樣式"""
        return """
/* 考題對應法條樣式 */
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
    font-size: 2.2em;
    margin-bottom: 10px;
    font-weight: 700;
}

.page-header .subtitle {
    font-size: 1.1em;
    opacity: 0.95;
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

/* 題目卡片 */
.qa-card {
    background: white;
    border: 2px solid #3498db;
    border-radius: 15px;
    margin-bottom: 30px;
    padding: 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.qa-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.qa-header {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
    padding: 20px 30px;
    border-radius: 13px 13px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.qa-number {
    font-size: 1.4em;
    font-weight: 700;
}

.answer-badge {
    background: #27ae60;
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 1em;
}

.qa-content {
    padding: 25px 30px;
}

.qa-question {
    font-size: 1.15em;
    font-weight: 600;
    margin-bottom: 20px;
    color: #2c3e50;
    line-height: 1.8;
    padding-bottom: 15px;
    border-bottom: 2px solid #e0e0e0;
}

/* 選項列表 */
.options-list {
    margin-bottom: 25px;
}

.option-item {
    display: flex;
    margin-bottom: 10px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 3px solid #ddd;
}

.option-item.correct {
    background: #d4edda;
    border-left-color: #27ae60;
}

.option-label {
    font-weight: 700;
    color: #2c3e50;
    margin-right: 10px;
    min-width: 30px;
}

.option-text {
    flex: 1;
    color: #555;
}

/* 法條區域 */
.articles-section {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    border: 2px solid #e0e0e0;
}

.articles-title {
    font-size: 1.1em;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #ddd;
}

.article-box {
    background: white;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #e74c3c;
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 15px;
    transition: all 0.2s ease;
}

.article-box:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-left-color: #c0392b;
}

.article-box-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.article-name {
    font-weight: 700;
    color: #e74c3c;
    font-size: 1.05em;
}

.similarity-score {
    background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 0.85em;
    font-weight: 600;
}

.article-info {
    display: flex;
    gap: 20px;
    margin-bottom: 12px;
    font-size: 0.9em;
    color: #666;
}

.article-info-item::before {
    content: "•";
    margin-right: 5px;
    color: #3498db;
    font-weight: bold;
}

.article-text {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 6px;
    font-size: 0.95em;
    line-height: 1.7;
    color: #555;
    white-space: pre-wrap;
}

/* 列印樣式 */
@media print {
    body {
        background: white;
        padding: 0;
    }

    .qa-card {
        break-inside: avoid;
        box-shadow: none;
        border: 1px solid #3498db;
    }

    .navigation {
        display: none;
    }

    .page-header {
        background: #3498db;
    }
}

/* 響應式設計 */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }

    .page-header h1 {
        font-size: 1.6em;
    }

    .qa-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .article-box-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
    }
}
"""

    def load_original_qa_data(self, json_file: Path) -> Dict[str, Any]:
        """載入原始 qa_mapped JSON 資料以獲取選項內容"""
        # 從 embedded 檔名還原成原始 qa_mapped 檔名
        original_name = json_file.name.replace('_embedded.json', '.json')
        qa_mapped_dir = json_file.parent.parent / "qa_mapped"
        original_file = qa_mapped_dir / original_name

        if original_file.exists():
            with open(original_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def generate_html_for_json(self, json_file: Path) -> str:
        """為單個 JSON 檔案生成考題對應法條 HTML"""
        # 讀取 embedded JSON 資料
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 讀取原始 qa_mapped JSON 以獲取選項內容
        original_qa_data = self.load_original_qa_data(json_file)
        original_questions = {q['question_number']: q for q in original_qa_data.get('questions', [])}

        metadata = data.get('metadata', {})
        question_matches = data.get('question_matches', [])

        # 解析檔名
        file_info = self.parse_filename(json_file.name)

        # 生成 HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_info['display']} - 考題對應法條</title>
    <link rel="stylesheet" href="styles/qa_article_mapping.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>{file_info['display']}</h1>
            <div class="subtitle">考題對應法條完整對照表</div>
        </div>

        <div class="navigation">
            <ul class="nav-list">
                <li><a href="index.html" class="nav-item">← 返回索引</a></li>
                <li><a href="{json_file.stem}.html" class="nav-item">查看 Embedding 結果</a></li>
            </ul>
        </div>
"""

        # 生成每個題目的 HTML
        for question in question_matches:
            question_number = question.get('question_number', 'N/A')
            question_text = question.get('question_text', '')
            correct_answer = question.get('correct_answer')

            # 從原始 QA 資料獲取選項內容
            original_q = original_questions.get(question_number, {})
            original_options = original_q.get('options', {})

            # 處理答案徽章
            if correct_answer:
                answer_badge = f'<div class="answer-badge">正確答案：{correct_answer}</div>'
            else:
                answer_badge = '<div class="answer-badge" style="background: #95a5a6;">答案未提供</div>'

            # 收集此題所有相關法條
            articles = self.collect_question_articles(question)

            html += f"""
        <div class="qa-card">
            <div class="qa-header">
                <div class="qa-number">第 {question_number} 題</div>
                {answer_badge}
            </div>

            <div class="qa-content">
                <div class="qa-question">{question_text}</div>

                <div class="options-list">
"""

            # 顯示選項（從原始 QA 資料讀取）
            for option_letter in ['A', 'B', 'C', 'D']:
                option_text = original_options.get(option_letter, '')
                if not option_text:
                    continue

                is_correct = (option_letter == correct_answer)
                correct_class = 'correct' if is_correct else ''

                html += f"""
                    <div class="option-item {correct_class}">
                        <span class="option-label">{option_letter}.</span>
                        <span class="option-text">{option_text}</span>
                    </div>
"""

            html += """
                </div>

                <div class="articles-section">
                    <div class="articles-title">📚 相關法條</div>
"""

            # 顯示相關法條
            if articles:
                for article in articles:
                    similarity_percent = f"{article['similarity'] * 100:.2f}%"

                    html += f"""
                    <div class="article-box">
                        <div class="article-box-header">
                            <div class="article-name">
                                {article['law_name']} 第 {article['article_no']} 條
                            </div>
                            <div class="similarity-score">相似度：{similarity_percent}</div>
                        </div>
                        <div class="article-info">
                            <span class="article-info-item">{article['category']}</span>
                            <span class="article-info-item">{article['authority']}</span>
                            <span class="article-info-item">法條代碼：{article['id']}</span>
                        </div>
                        <div class="article-text">{article['content']}</div>
                    </div>
"""
            else:
                html += """
                    <p style="color: #999; padding: 20px; text-align: center;">此題無匹配法條</p>
"""

            html += """
                </div>
            </div>
        </div>
"""

        html += f"""
        <div style="text-align: center; color: #999; margin-top: 30px; padding: 20px;">
            生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        return html

    def generate_index_page(self, json_files: List[Path]) -> str:
        """生成索引頁面"""
        # 收集所有檔案的資訊
        files_info = []

        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            question_matches = data.get('question_matches', [])

            # 載入原始 QA 資料
            original_qa_data = self.load_original_qa_data(json_file)
            original_questions = original_qa_data.get('questions', [])

            # 統計有答案的題數
            answered_count = sum(1 for q in original_questions if q.get('answer') is not None)

            file_info = self.parse_filename(json_file.name)
            html_filename = f"{json_file.stem}_qa_mapping.html"

            files_info.append({
                'file_info': file_info,
                'html_filename': html_filename,
                'total_questions': len(question_matches),
                'answered_questions': answered_count
            })

        # 生成 HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>考題對應法條 - 索引頁面</title>
    <link rel="stylesheet" href="styles/qa_article_mapping.css">
    <style>
        .exam-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .exam-card {{
            background: white;
            border: 2px solid #e0e0e0;
            border-left: 5px solid #3498db;
            border-radius: 12px;
            padding: 25px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .exam-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            border-left-color: #e74c3c;
        }}
        .exam-title {{
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .exam-stats {{
            display: flex;
            gap: 15px;
            margin-top: 12px;
            flex-wrap: wrap;
        }}
        .stat-badge {{
            background: #f8f9fa;
            padding: 6px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            color: #555;
            border: 1px solid #ddd;
        }}
        .metadata-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .metadata-item {{
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .metadata-label {{
            font-weight: 600;
            color: #555;
        }}
        .metadata-value {{
            color: #2c3e50;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>📚 考題對應法條報告</h1>
            <div class="subtitle">不動產經紀人考試 - 智能法條匹配系統</div>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">📊 總體統計</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">總科目數</span>
                    <span class="metadata-value">{len(files_info)} 科</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">總題目數</span>
                    <span class="metadata-value">{sum(f['total_questions'] for f in files_info)} 題</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">有答案題數</span>
                    <span class="metadata-value">{sum(f['answered_questions'] for f in files_info)} 題</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">匹配方法</span>
                    <span class="metadata-value">Embedding 智能匹配</span>
                </div>
            </div>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">📋 考試科目列表</h2>
            <div class="exam-grid">
"""

        for file_info in files_info:
            info = file_info['file_info']
            html += f"""
                <div class="exam-card" onclick="window.location.href='{file_info['html_filename']}'">
                    <div class="exam-title">{info['display']}</div>
                    <div style="color: #666; font-size: 0.95em; margin-bottom: 10px;">
                        {info['subject']}
                    </div>
                    <div class="exam-stats">
                        <div class="stat-badge">📝 {file_info['total_questions']} 題</div>
                        <div class="stat-badge">✅ {file_info['answered_questions']} 題有答案</div>
                        <div class="stat-badge">🤖 AI 智能匹配</div>
                    </div>
                </div>
"""

        html += f"""
            </div>
        </div>

        <div class="metadata-card">
            <h3 style="color: #2c3e50;">ℹ️ 使用說明</h3>
            <ul style="line-height: 2; color: #555; margin-top: 10px; padding-left: 20px;">
                <li><strong>智能法條匹配</strong>：使用 OpenAI Embedding 技術自動匹配相關法條</li>
                <li><strong>相似度評分</strong>：每個法條都有相似度百分比，幫助判斷相關性</li>
                <li><strong>完整法條內容</strong>：顯示法條名稱、條號、類別、主管機關及完整內容</li>
                <li><strong>答案標示</strong>：正確答案以綠色標示，無答案題目會特別標註</li>
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

    def process_all_files(self):
        """處理所有 JSON 檔案"""
        # 找到所有 JSON 檔案
        json_files = sorted(self.input_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"在 {self.input_dir} 中找不到 JSON 檔案")
            return

        logger.info(f"找到 {len(json_files)} 個 JSON 檔案")

        # 生成 CSS
        css_file = self.output_dir / "styles" / "qa_article_mapping.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_css())
        logger.info(f"✅ CSS 已生成：{css_file}")

        # 生成每個 JSON 的 HTML
        generated_files = []
        for json_file in json_files:
            html_file = self.output_dir / f"{json_file.stem}_qa_mapping.html"
            html_content = self.generate_html_for_json(json_file)

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            generated_files.append(html_file)
            logger.info(f"✅ HTML 已生成：{html_file}")

        # 生成 index 頁面
        index_file = self.output_dir / "index.html"
        index_content = self.generate_index_page(json_files)

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)

        logger.info(f"✅ 索引頁面已生成：{index_file}")

        # 生成摘要
        logger.info("=" * 60)
        logger.info("考題對應法條 HTML 轉換完成摘要")
        logger.info("=" * 60)
        logger.info(f"處理檔案數：{len(json_files)}")
        logger.info(f"輸出目錄：{self.output_dir}")
        logger.info(f"索引頁面：{index_file}")
        logger.info("=" * 60)

        return generated_files


def main():
    """主函數"""
    # 設定路徑
    base_path = Path("/home/bheadwei/LegalStatuteAnalysis")
    input_dir = base_path / "output" / "embedded_results"
    output_dir = base_path / "output" / "qa_article_reports"

    logger.info("開始生成考題對應法條 HTML...")
    logger.info(f"輸入目錄：{input_dir}")
    logger.info(f"輸出目錄：{output_dir}")

    try:
        generator = QAArticleMappingGenerator(
            input_dir=str(input_dir),
            output_dir=str(output_dir)
        )
        generator.process_all_files()

        logger.info("✅ 考題對應法條 HTML 轉換成功完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 轉換失敗：{e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
