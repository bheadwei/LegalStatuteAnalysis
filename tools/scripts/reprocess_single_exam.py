"""
重新處理單一考卷的 LLM 解析
"""
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.parsing.llm_parser import parse_questions_with_llm, parse_answers_with_llm, merge_qa_json

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """重新處理民法概要"""
    load_dotenv()

    # 路徑設定
    question_md = Path('output/markdown/112190_1201_民法概要.md')
    answer_md = Path('output/markdown/112190_ANS1201_民法概要.md')
    output_json = Path('output/parsed_qa/112190_1201_民法概要.json')

    logger.info(f"重新處理: {question_md.name}")

    # 讀取 Markdown
    with open(question_md, 'r', encoding='utf-8') as f:
        question_content = f.read()

    with open(answer_md, 'r', encoding='utf-8') as f:
        answer_content = f.read()

    logger.info(f"Markdown 長度 - 題目: {len(question_content)} 字元")
    logger.info(f"Markdown 長度 - 答案: {len(answer_content)} 字元")

    # 使用 LLM 解析
    logger.info("開始 LLM 解析題目...")
    questions_result = parse_questions_with_llm(question_content)

    if not questions_result:
        logger.error("題目解析失敗")
        return False

    # 檢查題目數量
    mc_count = len(questions_result.get('multiple_choice_section', {}).get('questions', []))
    logger.info(f"解析到選擇題: {mc_count} 題")

    if mc_count < 25:
        logger.warning(f"⚠️ 選擇題數量不足 25 題，只有 {mc_count} 題")
        logger.warning("這可能是 LLM 解析問題，建議檢查 Markdown 內容")

    logger.info("開始 LLM 解析答案...")
    answers_result = parse_answers_with_llm(answer_content)

    if not answers_result:
        logger.error("答案解析失敗")
        return False

    # 合併結果
    logger.info("合併題目與答案...")
    final_json = merge_qa_json(questions_result, answers_result)

    # 儲存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_json, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 完成: {output_json}")

    # 最終檢查
    with open(output_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    final_mc_count = len(data.get('multiple_choice_section', {}).get('questions', []))
    logger.info(f"最終選擇題數量: {final_mc_count}")

    return final_mc_count >= 25


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
