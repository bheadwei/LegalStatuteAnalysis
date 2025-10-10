"""
題目答案 Mapping 腳本
處理「乙部分 單一選擇題」與答案表格的對應
使用 LLM 智能解析題目，避免漏題問題
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from src.pdf_converter.core import PDFToMarkdownConverter
from src.parsing.llm_parser import parse_questions_with_llm, parse_answers_with_llm

# 載入環境變數
load_dotenv()


def setup_logger() -> logging.Logger:
    """設置日誌"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def find_matching_answer_file(question_file: Path, answer_dir: Path) -> Path:
    """根據題目檔名找到對應的答案檔"""
    # 112190_1201_民法概要.pdf -> 112190_ANS1201_民法概要.pdf
    match = re.match(r'(\d+)_(\d+)_(.+)\.pdf', question_file.name)
    if not match:
        raise ValueError(f"無法解析題目檔名: {question_file.name}")

    year_code, subject_code, subject_name = match.groups()
    answer_filename = f'{year_code}_ANS{subject_code}_{subject_name}.pdf'
    answer_path = answer_dir / answer_filename

    if not answer_path.exists():
        raise FileNotFoundError(f"找不到對應答案檔: {answer_filename}")

    return answer_path


def extract_single_choice_section(markdown_content: str) -> Tuple[str, int]:
    """提取「乙、測驗題部分」內容

    Returns:
        (section_content, start_line): 測驗題內容和起始行號
    """
    lines = markdown_content.split('\n')

    # 找到「乙、測驗題部分」的位置
    section_start = None
    for i, line in enumerate(lines):
        if '測驗題' in line and ('乙' in line or '部分' in line):
            section_start = i
            break

    if section_start is None:
        raise ValueError("未找到「測驗題部分」")

    # 從該位置開始到文件結尾
    section_content = '\n'.join(lines[section_start:])
    return section_content, section_start


def parse_questions_with_llm_enhanced(markdown_content: str, logger: logging.Logger) -> List[Dict]:
    """使用 LLM 智能解析選擇題（參考原始範例邏輯）

    此函數使用 LLM 來解析題目，能夠：
    1. 智能分割連在一起的選項
    2. 處理各種格式異常
    3. 確保不會漏題

    Returns:
        [
            {
                "question_number": 1,
                "question_text": "題目內容",
                "options": {"A": "選項1", "B": "選項2", "C": "選項3", "D": "選項4"}
            },
            ...
        ]
    """
    logger.info("📝 使用 LLM 智能解析題目...")

    try:
        # 使用 LLM 解析整份題目文件
        parsed_result = parse_questions_with_llm(markdown_content)

        if not parsed_result:
            logger.error("❌ LLM 解析失敗")
            return []

        # 提取選擇題部分
        mc_section = parsed_result.multiple_choice_section

        questions = []
        for mc_q in mc_section:
            questions.append({
                "question_number": mc_q.question_number,
                "question_text": mc_q.content,
                "options": mc_q.options.dict()  # 轉換為 dict {"A": "...", "B": "...", ...}
            })

        logger.info(f"✅ LLM 成功解析 {len(questions)} 題選擇題")
        return questions

    except Exception as e:
        logger.error(f"❌ LLM 解析過程出錯: {e}", exc_info=True)
        return []


def parse_answers_from_table(markdown_content: str, logger: logging.Logger) -> Dict[int, str]:
    """從答案表格中提取答案

    Returns:
        {1: 'A', 2: 'C', 3: 'B', ...}
    """
    answers = {}

    # 找到所有表格
    table_pattern = r'<table>(.*?)</table>'
    tables = re.findall(table_pattern, markdown_content, re.DOTALL)

    for table in tables:
        # 解析表格中的「題號」和「答案」行
        # 提取「第N題」的模式
        question_nums = re.findall(r'第(\d+)題', table)
        # 提取答案（跳過「題號」和「答案」等關鍵字）
        answer_row = re.search(r'<tr><td[^>]*>答案</td>(.+?)</tr>', table)

        if question_nums and answer_row:
            answer_cells = re.findall(r'<td[^>]*>([A-D]?)</td>', answer_row.group(1))

            # 配對題號和答案
            for q_num_str, ans in zip(question_nums, answer_cells):
                if ans:  # 只記錄有答案的題目
                    q_num = int(q_num_str)
                    answers[q_num] = ans

    logger.info(f"解析到 {len(answers)} 個答案")
    return answers


def merge_questions_and_answers(questions: List[Dict], answers: Dict[int, str]) -> List[Dict]:
    """合併題目和答案

    Returns:
        [
            {
                "question_number": 1,
                "question_text": "...",
                "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
                "answer": "A",
                "answer_index": 0
            },
            ...
        ]
    """
    merged = []

    for q in questions:
        q_num = q['question_number']
        answer_letter = answers.get(q_num, None)

        if answer_letter:
            # 計算答案索引 (A=0, B=1, C=2, D=3)
            answer_index = ord(answer_letter) - ord('A')

            merged.append({
                "question_number": q_num,
                "question_text": q['question_text'],
                "options": q['options'],  # 已經是 dict 格式 {"A": "...", "B": "...", ...}
                "answer": answer_letter,
                "answer_index": answer_index
            })

    return merged


def process_qa_pair(question_pdf: Path, answer_pdf: Path, output_json: Path, logger: logging.Logger):
    """處理單組題目答案對（使用 LLM 智能解析）"""
    logger.info(f"處理: {question_pdf.name}")

    # 1. 轉換 PDF 為 Markdown
    converter = PDFToMarkdownConverter(logger)

    logger.info("轉換題目 PDF...")
    q_markdown = converter.process_pdf(question_pdf)

    logger.info("轉換答案 PDF...")
    a_markdown = converter.process_pdf(answer_pdf)

    # 2. 使用 LLM 智能解析題目（不需要手動提取測驗題部分，LLM 會自動識別）
    logger.info("使用 LLM 解析題目...")
    questions = parse_questions_with_llm_enhanced(q_markdown, logger)

    if not questions:
        logger.error("❌ 題目解析失敗，中止處理")
        return

    # 3. 解析答案
    logger.info("解析答案...")
    answers = parse_answers_from_table(a_markdown, logger)

    # 4. 合併
    logger.info("合併題目與答案...")
    qa_merged = merge_questions_and_answers(questions, answers)

    # 5. 儲存 JSON
    output_data = {
        "metadata": {
            "question_file": question_pdf.name,
            "answer_file": answer_pdf.name,
            "total_questions": len(qa_merged),
            "parsing_method": "LLM (GPT-4o-mini)"  # 記錄使用的解析方法
        },
        "questions": qa_merged
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 儲存完成: {output_json}")
    logger.info(f"   共處理 {len(qa_merged)} 題（使用 LLM 智能解析）")


def main():
    """主程式"""
    logger = setup_logger()

    # 資料夾路徑
    questions_dir = Path('data/questions')
    answer_dir = Path('data/answer')
    output_dir = Path('output/qa_mapped')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 取得所有題目檔案
    question_files = sorted(questions_dir.glob('*.pdf'))

    if not question_files:
        logger.error(f"未找到題目檔案於: {questions_dir}")
        return

    logger.info(f"找到 {len(question_files)} 個題目檔案")

    # 處理每組題目答案
    for q_file in question_files:
        try:
            # 找到對應答案檔
            a_file = find_matching_answer_file(q_file, answer_dir)

            # 產生輸出檔名
            output_json = output_dir / f"{q_file.stem}_mapped.json"

            # 處理
            process_qa_pair(q_file, a_file, output_json, logger)

        except Exception as e:
            logger.error(f"處理失敗 {q_file.name}: {e}")
            continue

    logger.info("=" * 60)
    logger.info("✅ 所有檔案處理完成")


if __name__ == "__main__":
    main()
