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
}
"""

    def generate_index_page(self, json_files: List[Path]) -> str:
        """生成索引頁面"""
        html = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embedding 結果報告 - 索引</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>Embedding 結果報告</h1>
            <div class="subtitle">法條智能匹配分析</div>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">📊 報告清單</h2>
            <div style="display: grid; gap: 15px;">
"""

        for json_file in json_files:
            # 讀取元資料
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('metadata', {})
            source_file = metadata.get('source_file', json_file.name)
            total_questions = metadata.get('total_questions', 0)
            total_options = metadata.get('total_options_processed', 0)

            html_filename = json_file.stem + '.html'

            html += f"""
                <div class="metadata-item" style="padding: 20px; cursor: pointer;" onclick="window.location.href='{html_filename}'">
                    <div>
                        <div style="font-size: 1.2em; font-weight: 600; color: #2c3e50; margin-bottom: 8px;">
                            {source_file}
                        </div>
                        <div style="color: #666; font-size: 0.95em;">
                            題目數：{total_questions} | 選項數：{total_options}
                        </div>
                    </div>
                    <div style="color: #3498db; font-size: 1.5em;">→</div>
                </div>
"""

        html += f"""
            </div>
        </div>

        <div class="metadata-card">
            <h3 style="color: #2c3e50;">ℹ️ 說明</h3>
            <p style="line-height: 1.8; color: #555; margin-top: 10px;">
                本報告展示了法條 Embedding 匹配結果，每個題目的選項都會顯示最相關的法條及相似度分數。
                相似度分數越高，表示該法條與選項的語義相關性越強。
            </p>
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
            </ul>
        </div>

        <div class="metadata-card">
            <h2 style="color: #2c3e50; margin-bottom: 15px;">📋 基本資訊</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <span class="metadata-label">來源檔案</span>
                    <span class="metadata-value">{metadata.get('source_file', 'N/A')}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">法條資料</span>
                    <span class="metadata-value">{metadata.get('laws_csv', 'N/A')}</span>
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
"""

        # 生成每個題目的 HTML
        for question in question_matches:
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
        html = f"""
        <div class="question-card">
            <div class="question-header">
                <div class="question-number">第 {question.get('question_number', 'N/A')} 題</div>
                <div class="correct-answer-badge">正確答案：{question.get('correct_answer', 'N/A')}</div>
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
                                <div class="article-content">{article.get('content', 'N/A')[:300]}...</div>
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
