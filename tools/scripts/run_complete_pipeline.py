#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的法條對應系統處理流程

流程：
1. PDF → Markdown (MinerU)
2. Markdown → JSON (LLM Parser)
3. 法條 PDF → CSV (如需要)
4. JSON + 法條CSV → Embedding 匹配
5. 匹配結果 → HTML 報告
6. HTML → PDF 報告

使用方式：
    python tools/scripts/run_complete_pipeline.py \
        --exam_pdf data/pdfs/113年不動產經紀法規(經)-A黃振國老師.pdf \
        --laws_csv data/laws_processed/law_articles.csv \
        --output_dir output
"""

import argparse
import json
import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.pdf_converter.core import PDFToMarkdownConverter
from src.parsing.llm_parser import (
    parse_questions_with_llm,
    parse_answers_with_llm,
    merge_qa_json,
)
from src.core_embedding.embedding_matcher import EmbeddingMatcher

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegalStatuteAnalysisPipeline:
    """法條對應系統完整處理流程"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 子目錄
        self.markdown_dir = output_dir / "markdown"
        self.json_dir = output_dir / "json"
        self.results_dir = output_dir / "results"

        for d in [self.markdown_dir, self.json_dir, self.results_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # 載入環境變數
        load_dotenv()

        # 檢查 API Key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("請設定 OPENAI_API_KEY 環境變數")

        logger.info(f"輸出目錄: {self.output_dir}")

    def step1_pdf_to_markdown(self, pdf_path: Path) -> tuple[Path, Path]:
        """步驟1: PDF 轉換為 Markdown"""
        logger.info("=" * 60)
        logger.info("步驟 1: PDF → Markdown (使用 MinerU)")
        logger.info("=" * 60)

        converter = PDFToMarkdownConverter()

        # 生成 markdown 檔名
        markdown_filename = self.markdown_dir / f"{pdf_path.stem}.md"

        # 轉換 PDF
        content = converter.process_pdf(pdf_path, markdown_filename)

        logger.info(f"✅ Markdown 已生成: {markdown_filename}")

        # 假設答案也在同一個Markdown中，或者需要分離
        # 這裡我們先返回同一個檔案作為題目和答案
        return markdown_filename, markdown_filename

    def step2_markdown_to_json(self, questions_md: Path, answers_md: Path) -> Path:
        """步驟2: Markdown 解析為 JSON"""
        logger.info("=" * 60)
        logger.info("步驟 2: Markdown → JSON (LLM 解析)")
        logger.info("=" * 60)

        # 讀取內容
        q_content = questions_md.read_text(encoding='utf-8')

        # 處理答案：如果題號前有答案字母，需要提取
        # 這裡先使用簡單的方式：假設答案在題目的markdown中
        a_content = self._extract_answers_from_markdown(q_content)

        # LLM 解析
        logger.info("解析題目...")
        questions_result = parse_questions_with_llm(q_content)
        if not questions_result:
            raise RuntimeError("題目解析失敗")

        logger.info("解析答案...")
        answers_result = parse_answers_with_llm(a_content)
        if not answers_result:
            raise RuntimeError("答案解析失敗")

        # 合併
        final_json = merge_qa_json(questions_result, answers_result)

        # 儲存
        output_file = self.json_dir / f"{questions_md.stem}_parsed.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ JSON 已生成: {output_file}")
        return output_file

    def _extract_answers_from_markdown(self, markdown_content: str) -> str:
        """從markdown中提取答案

        根據用戶說明：答案在題號前面（例如：A 1. 題目內容...）
        """
        import re

        # 尋找格式如 "A 1." 或 "B 2." 的模式
        pattern = r'^([A-D])\s+(\d+)[\.\、]'

        answers = {}
        for line in markdown_content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                answer_letter = match.group(1)
                question_number = match.group(2)
                answers[question_number] = answer_letter

        # 轉換為LLM Parser期望的格式
        if answers:
            answer_text = "答案：\n"
            for q_num, ans_letter in sorted(answers.items(), key=lambda x: int(x[0])):
                answer_text += f"{q_num}. {ans_letter}\n"
            return answer_text
        else:
            logger.warning("未能從markdown中提取答案，將嘗試LLM自動識別")
            return "答案：（需要從題目中識別）"

    def step3_embedding_matching(self, questions_json: Path, laws_csv: Path) -> Path:
        """步驟3: Embedding 匹配"""
        logger.info("=" * 60)
        logger.info("步驟 3: Embedding 匹配")
        logger.info("=" * 60)

        # 初始化匹配器
        matcher = EmbeddingMatcher(
            openai_api_key=self.api_key,
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        )

        # 載入法條
        logger.info(f"載入法條資料: {laws_csv}")
        if not matcher.load_law_articles(str(laws_csv)):
            raise RuntimeError("法條載入失敗")

        # 處理考題
        logger.info(f"處理考題: {questions_json}")
        results = matcher.process_exam_questions(
            str(questions_json),
            output_file=None
        )

        # 儲存結果
        output_file = self.results_dir / f"{questions_json.stem}_matches.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ 匹配結果已生成: {output_file}")
        return output_file

    def step4_generate_html_report(self, matches_json: Path, questions_json: Path) -> Path:
        """步驟4: 生成 HTML 報告"""
        logger.info("=" * 60)
        logger.info("步驟 4: 生成 HTML 報告")
        logger.info("=" * 60)

        # 這裡需要實作HTML生成邏輯
        # 可以使用stage2_html_generator.py的邏輯
        logger.warning("HTML報告生成功能尚未實作")
        return None

    def run(self, exam_pdf: Path, laws_csv: Path):
        """運行完整流程"""
        logger.info("🚀 開始法條對應系統完整流程")
        logger.info(f"考題PDF: {exam_pdf}")
        logger.info(f"法條CSV: {laws_csv}")

        try:
            # 步驟1: PDF → Markdown
            questions_md, answers_md = self.step1_pdf_to_markdown(exam_pdf)

            # 步驟2: Markdown → JSON
            questions_json = self.step2_markdown_to_json(questions_md, answers_md)

            # 步驟3: Embedding 匹配
            matches_json = self.step3_embedding_matching(questions_json, laws_csv)

            # 步驟4: 生成報告
            # html_report = self.step4_generate_html_report(matches_json, questions_json)

            logger.info("=" * 60)
            logger.info("✅ 完整流程執行成功！")
            logger.info("=" * 60)
            logger.info(f"輸出檔案：")
            logger.info(f"  - Markdown: {questions_md}")
            logger.info(f"  - JSON: {questions_json}")
            logger.info(f"  - 匹配結果: {matches_json}")

            return True

        except Exception as e:
            logger.error(f"❌ 流程執行失敗: {e}", exc_info=True)
            return False


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="法條對應系統完整處理流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python tools/scripts/run_complete_pipeline.py \\
      --exam_pdf data/pdfs/113年不動產經紀法規(經)-A黃振國老師.pdf \\
      --laws_csv data/laws_processed/law_articles.csv \\
      --output_dir output
        """
    )

    parser.add_argument(
        '--exam_pdf',
        type=Path,
        required=True,
        help='考題PDF檔案路徑'
    )

    parser.add_argument(
        '--laws_csv',
        type=Path,
        required=True,
        help='法條CSV檔案路徑'
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=Path('output'),
        help='輸出目錄（預設: output）'
    )

    args = parser.parse_args()

    # 檢查輸入檔案
    if not args.exam_pdf.exists():
        logger.error(f"考題PDF不存在: {args.exam_pdf}")
        return 1

    if not args.laws_csv.exists():
        logger.error(f"法條CSV不存在: {args.laws_csv}")
        return 1

    # 執行流程
    pipeline = LegalStatuteAnalysisPipeline(args.output_dir)
    success = pipeline.run(args.exam_pdf, args.laws_csv)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
