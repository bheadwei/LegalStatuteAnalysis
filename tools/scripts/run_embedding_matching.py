"""
執行 Embedding 法條匹配
讀取 QA mapped JSON，與法條資料庫進行 Embedding 匹配
"""

import json
import logging
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core_embedding.embedding_matcher import EmbeddingMatcher


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


def process_single_json(json_path: Path, laws_csv: Path, output_dir: Path, logger: logging.Logger):
    """處理單一 QA mapped JSON 檔案"""
    import os
    from dotenv import load_dotenv

    logger.info(f"處理: {json_path.name}")

    # 載入環境變數
    load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-large')

    # 載入 QA JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        qa_data = json.load(f)

    questions = qa_data['questions']
    logger.info(f"  載入 {len(questions)} 題")

    # 初始化 Embedding Matcher
    matcher = EmbeddingMatcher(openai_api_key=openai_api_key, embedding_model=embedding_model)

    # 載入法條資料
    if not matcher.load_law_articles(str(laws_csv)):
        raise RuntimeError("法條資料載入失敗")

    # 處理每題的每個選項
    results = {
        "metadata": {
            "source_file": json_path.name,
            "laws_csv": str(laws_csv),
            "total_questions": len(questions),
            "total_options_processed": 0
        },
        "question_matches": []
    }

    total_options = 0

    for q in questions:
        q_num = q['question_number']
        q_text = q['question_text']
        options = q.get('options', [])
        answer_letter = q.get('answer', '')
        answer_index = q.get('answer_index', -1)

        logger.info(f"  題 {q_num}: {q_text[:50]}... ({len(options)} 個選項)")

        # 為每個選項進行匹配
        option_matches = []

        for i, opt_text in enumerate(options):
            # 選項字母 A/B/C/D
            opt_letter = chr(ord('A') + i)

            # 進行 Embedding 匹配
            match_result = matcher.match_option(
                question_content=q_text,
                option_letter=opt_letter,
                option_content=opt_text,
                question_id=str(q_num),
                top_k=3  # 返回前3個最相關的法條
            )

            # 標記是否為正確答案
            is_correct_answer = (opt_letter == answer_letter)

            option_matches.append({
                "option_letter": opt_letter,
                "option_text": opt_text,
                "is_correct_answer": is_correct_answer,
                "matched_articles": match_result.matched_articles,
                "processing_time": match_result.processing_time
            })

            total_options += 1

        # 儲存該題的結果
        results['question_matches'].append({
            "question_number": q_num,
            "question_text": q_text,
            "correct_answer": answer_letter,
            "options": option_matches
        })

    results['metadata']['total_options_processed'] = total_options

    # 儲存結果
    output_file = output_dir / f"{json_path.stem}_embedded.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 完成: {output_file}")
    logger.info(f"   處理 {len(questions)} 題, {total_options} 個選項")


def main():
    """主程式"""
    logger = setup_logger()

    # 路徑設定
    qa_mapped_dir = Path('output/qa_mapped')
    laws_csv = Path('data/law_articles.csv')
    output_dir = Path('output/embedded_results')
    output_dir.mkdir(parents=True, exist_ok=True)

    # 檢查法條資料庫
    if not laws_csv.exists():
        logger.error(f"找不到法條資料庫: {laws_csv}")
        logger.error("請先執行: poetry run python3 tools/scripts/prepare_laws_csv.py")
        return

    # 取得所有 QA mapped JSON
    json_files = sorted(qa_mapped_dir.glob('*_mapped.json'))

    if not json_files:
        logger.error(f"找不到 QA mapped JSON 於: {qa_mapped_dir}")
        return

    logger.info(f"找到 {len(json_files)} 個 JSON 檔案")
    logger.info("=" * 60)

    # 處理每個 JSON
    for json_file in json_files:
        try:
            process_single_json(json_file, laws_csv, output_dir, logger)
            logger.info("")
        except Exception as e:
            logger.error(f"處理失敗 {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    logger.info("=" * 60)
    logger.info("✅ 所有檔案處理完成")


if __name__ == "__main__":
    main()
