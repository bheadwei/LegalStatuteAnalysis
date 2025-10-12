#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新處理民法概要 - 完整流程
從 PDF → Markdown → LLM 解析 → JSON
"""

import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pdf_converter.core import PDFToMarkdownConverter
from src.parsing.llm_parser import parse_questions_with_llm, parse_answers_with_llm, merge_qa_json

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """重新處理民法概要"""
    load_dotenv()

    # 路徑設定
    question_pdf = Path('data/questions/112190_1201_民法概要.pdf')
    answer_pdf = Path('data/answer/112190_ANS1201_民法概要.pdf')

    markdown_dir = Path('output/markdown')
    output_dir = Path('output/parsed_qa')

    question_md = markdown_dir / f"{question_pdf.stem}.md"
    answer_md = markdown_dir / f"{answer_pdf.stem}.md"
    output_json = output_dir / "112190_1201_民法概要.json"

    logger.info("=" * 60)
    logger.info("開始重新處理：112190_1201_民法概要")
    logger.info("=" * 60)

    # Step 1: PDF → Markdown
    logger.info("Step 1/4: 轉換題目 PDF → Markdown")
    converter = PDFToMarkdownConverter(logger)
    question_content = converter.process_pdf(question_pdf, question_md, use_gpu=True)
    logger.info(f"  ✅ 題目 Markdown: {len(question_content)} 字元")

    logger.info("Step 2/4: 轉換答案 PDF → Markdown")
    answer_content = converter.process_pdf(answer_pdf, answer_md, use_gpu=True)
    logger.info(f"  ✅ 答案 Markdown: {len(answer_content)} 字元")

    # Step 2: LLM 解析
    logger.info("Step 3/4: LLM 解析題目")
    questions_result = parse_questions_with_llm(question_content)

    if not questions_result:
        logger.error("❌ 題目解析失敗")
        return False

    # 檢查題數
    mc_questions = questions_result.multiple_choice_section.questions if questions_result.multiple_choice_section else []
    mc_count = len(mc_questions)
    logger.info(f"  ✅ 解析到選擇題: {mc_count} 題")

    if mc_count < 20:
        logger.warning(f"  ⚠️ 題數異常：只有 {mc_count} 題（預期 25 題）")

    logger.info("Step 4/4: LLM 解析答案")
    answers_result = parse_answers_with_llm(answer_content)

    if not answers_result:
        logger.error("❌ 答案解析失敗")
        return False

    # 檢查答案數
    answer_count = len(answers_result.answers) if answers_result.answers else 0
    logger.info(f"  ✅ 解析到答案: {answer_count} 個")

    # Step 3: 合併
    logger.info("Step 5/5: 合併題目與答案")
    final_json = merge_qa_json(questions_result, answers_result)

    # 儲存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    logger.info(f"  ✅ JSON 已儲存: {output_json}")

    # 最終驗證
    with open(output_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    final_mc_count = len(data.get('multiple_choice_section', {}).get('questions', []))

    logger.info("=" * 60)
    logger.info("處理完成摘要")
    logger.info("=" * 60)
    logger.info(f"選擇題數量: {final_mc_count}")
    logger.info(f"申論題數量: {len(data.get('essay_section', {}).get('questions', []))}")
    logger.info(f"答案數量: {len([v for v in data.get('answer_key', {}).get('answers', {}).values() if v])}")

    if final_mc_count >= 20:
        logger.info("✅ 處理成功")
        return True
    else:
        logger.warning(f"⚠️ 選擇題數量不足: {final_mc_count}/25")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
