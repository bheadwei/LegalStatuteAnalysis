"""
將 parsed_qa 格式轉換為 embedding 匹配所需的格式
"""

import json
import logging
from pathlib import Path

def setup_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def convert_qa_format(input_file: Path, output_file: Path, logger: logging.Logger):
    """將 QA JSON 格式轉換為 embedding 匹配格式"""

    logger.info(f"轉換: {input_file.name}")

    # 讀取原始 JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 提取選擇題部分
    mc_questions = data.get('multiple_choice_section', {}).get('questions', [])

    if not mc_questions:
        logger.warning(f"  未找到選擇題，跳過")
        return False

    # 轉換格式
    converted = {
        "metadata": {
            "source_file": input_file.name,
            "exam_title": data.get('exam_metadata', {}).get('exam_title', ''),
            "course_name": data.get('exam_metadata', {}).get('course_name', '')
        },
        "questions": []
    }

    for q in mc_questions:
        # 將 options 從字典轉為陣列
        options_dict = q.get('options', {})
        options_array = []

        # 按 A, B, C, D 順序排列
        for letter in ['A', 'B', 'C', 'D']:
            if letter in options_dict:
                options_array.append(options_dict[letter])

        # 取得正確答案
        correct_answer = q.get('correct_answer', '')
        answer_index = ord(correct_answer) - ord('A') if correct_answer else -1

        converted['questions'].append({
            "question_number": q.get('question_number', 0),
            "question_text": q.get('content', ''),
            "options": options_array,
            "answer": correct_answer,
            "answer_index": answer_index
        })

    # 儲存轉換後的 JSON
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted, f, ensure_ascii=False, indent=2)

    logger.info(f"  ✅ 完成: {len(converted['questions'])} 題 → {output_file.name}")
    return True


def main():
    logger = setup_logger()

    # 路徑設定
    input_dir = Path('output/parsed_qa')
    output_dir = Path('output/qa_mapped')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 取得所有 JSON 檔案（排除 processing_report.json）
    json_files = [f for f in input_dir.glob('*.json') if 'processing_report' not in f.name]

    if not json_files:
        logger.error(f"找不到 JSON 檔案於: {input_dir}")
        return

    logger.info(f"找到 {len(json_files)} 個 JSON 檔案")
    logger.info("=" * 60)

    success_count = 0

    for json_file in sorted(json_files):
        try:
            # 輸出檔名加上 _mapped 後綴
            output_file = output_dir / f"{json_file.stem}_mapped.json"

            if convert_qa_format(json_file, output_file, logger):
                success_count += 1

        except Exception as e:
            logger.error(f"轉換失敗 {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    logger.info("=" * 60)
    logger.info(f"✅ 完成: {success_count}/{len(json_files)} 個檔案成功轉換")


if __name__ == "__main__":
    main()
