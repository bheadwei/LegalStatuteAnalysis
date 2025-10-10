#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法條準備腳本：將法條 PDF 轉換為 CSV

流程：
1. 掃描 data/laws/ 目錄中的所有 PDF
2. 使用 MinerU 轉換為 Markdown
3. 使用 law_articles_converter 轉換為 CSV
4. 合併所有法條到單一 CSV 檔案
"""

import argparse
import logging
import sys
import tempfile
from pathlib import Path

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.pdf_converter.core import PDFToMarkdownConverter
import pandas as pd

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_law_pdfs_to_csv(laws_dir: Path, output_csv: Path):
    """
    將法條目錄中的所有 PDF 轉換為單一 CSV

    Args:
        laws_dir: 法條 PDF 所在目錄
        output_csv: 輸出的 CSV 檔案路徑
    """
    logger.info(f"🚀 開始處理法條 PDF: {laws_dir}")

    # 找出所有 PDF
    pdf_files = list(laws_dir.glob("*.pdf"))
    logger.info(f"找到 {len(pdf_files)} 個法條 PDF 檔案")

    if not pdf_files:
        logger.error("未找到任何 PDF 檔案")
        return False

    # 初始化 PDF 轉換器
    converter = PDFToMarkdownConverter()

    # 準備 CSV 資料
    all_articles = []

    # 處理每個 PDF
    for idx, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"處理 [{idx}/{len(pdf_files)}]: {pdf_file.name}")

        try:
            # 使用臨時目錄
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_output = Path(temp_dir)

                # 轉換為 Markdown
                markdown_filename = temp_output / f"{pdf_file.stem}.md"
                content = converter.process_pdf(pdf_file, markdown_filename)
                # content 已經是字符串，不需要再讀取

                # 解析法條
                articles = parse_law_markdown(pdf_file.stem, content)
                all_articles.extend(articles)

                logger.info(f"  ✅ 解析出 {len(articles)} 條法條")

        except Exception as e:
            logger.error(f"  ❌ 處理失敗: {e}")
            continue

    # 轉換為 DataFrame 並儲存
    if all_articles:
        df = pd.DataFrame(all_articles)
        df.to_csv(output_csv, index=False, encoding='utf-8')
        logger.info(f"✅ 成功生成 CSV: {output_csv}")
        logger.info(f"   總計 {len(all_articles)} 條法條")
        return True
    else:
        logger.error("❌ 未能解析任何法條")
        return False


def parse_law_markdown(law_name: str, content: str) -> list:
    """
    簡單的法條 Markdown 解析器

    Args:
        law_name: 法規名稱（從檔名提取）
        content: Markdown 內容

    Returns:
        法條列表
    """
    import re

    articles = []

    # 簡單的模式：尋找 "第X條" 的格式
    pattern = r'第\s*(\d+)\s*條\s*(.+?)(?=第\s*\d+\s*條|$)'

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        article_no = int(match.group(1))
        article_content = match.group(2).strip()

        # 清理內容
        article_content = re.sub(r'\n+', ' ', article_content)
        article_content = article_content.strip()

        if article_content:  # 只保留非空內容
            articles.append({
                '法規代碼': generate_law_code(law_name),
                '法規名稱': law_name,
                '修正日期（民國）': '',
                '法規類別': '不動產法規',
                '主管機關': '內政部',
                '章節編號': 0,
                '章節標題': '',
                '條文主號': article_no,
                '條文次號': 0,
                '條文完整內容': article_content
            })

    return articles


def generate_law_code(law_name: str) -> str:
    """生成法規代碼"""
    # 簡單的映射
    code_map = {
        '不動產經紀業管理條例': 'REAA',
        '不動產經紀業管理條例施行細則': 'REAAR',
        '公寓大廈管理條例': 'CMBA',
        '公平交易法': 'FTLA',
        '消費者保護法': 'CPLA'
    }

    return code_map.get(law_name, 'UNKN')


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="將法條 PDF 轉換為 CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--laws_dir',
        type=Path,
        default=Path('data/laws'),
        help='法條 PDF 所在目錄（預設: data/laws）'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('data/law_articles.csv'),
        help='輸出 CSV 檔案路徑（預設: data/law_articles.csv）'
    )

    args = parser.parse_args()

    # 檢查輸入目錄
    if not args.laws_dir.exists():
        logger.error(f"法條目錄不存在: {args.laws_dir}")
        return 1

    # 確保輸出目錄存在
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # 執行轉換
    success = convert_law_pdfs_to_csv(args.laws_dir, args.output)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
