#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
處理單一考卷和答案PDF文件
將考卷PDF和答案PDF轉換為Markdown，然後合併成JSON格式

使用方法:
    poetry run python tools/scripts/process_single_exam.py \
        --question data/questions/110180_1102_不動產估價概要.pdf \
        --answer data/answer/110180_ANS1102_不動產估價概要.pdf \
        --output-dir output/parsed_qa

功能:
    1. 使用GPU加速的PDF轉換器將PDF轉換為Markdown
    2. 使用LLM解析器解析考題和答案
    3. 合併成JSON格式並保存
"""

import argparse
import json
import logging
from pathlib import Path
import sys
import re

# Add project root to sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from rich.console import Console
from rich import print as rprint

from src.pdf_converter.core import PDFToMarkdownConverter
from src.parsing.llm_parser import (
    parse_questions_with_llm,
    parse_answers_with_llm,
    merge_qa_json,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
console = Console()


def convert_pdf_to_markdown(pdf_path: Path, output_path: Path, use_gpu: bool = True) -> str:
    """
    將PDF轉換為Markdown

    Args:
        pdf_path: PDF文件路徑
        output_path: Markdown輸出路徑
        use_gpu: 是否使用GPU加速

    Returns:
        Markdown內容
    """
    try:
        converter = PDFToMarkdownConverter(logger)
        markdown_content = converter.process_pdf(pdf_path, output_path, use_gpu=use_gpu)
        return markdown_content
    except Exception as e:
        logger.error(f"PDF轉換失敗 {pdf_path.name}: {e}")
        raise


def process_exam(
    question_pdf: Path,
    answer_pdf: Path,
    markdown_dir: Path,
    output_dir: Path,
    use_gpu: bool = True
) -> bool:
    """
    處理單一考卷和答案

    Args:
        question_pdf: 考卷PDF路徑
        answer_pdf: 答案PDF路徑
        markdown_dir: Markdown輸出目錄
        output_dir: JSON輸出目錄
        use_gpu: 是否使用GPU加速

    Returns:
        處理是否成功
    """
    try:
        # 從文件名提取考試名稱
        match = re.match(r"(\d+_\d+)_(.+)\.pdf$", question_pdf.name)
        if not match:
            logger.error(f"無法解析文件名格式: {question_pdf.name}")
            return False

        exam_code = match.group(1)
        exam_subject = match.group(2)
        exam_name = f"{exam_code}_{exam_subject}"

        console.print(f"\n[bold cyan]處理考試:[/bold cyan] {exam_name}")
        console.print("=" * 60)

        # 1. 設置Markdown文件路徑
        question_md = markdown_dir / f"{question_pdf.stem}.md"
        answer_md = markdown_dir / f"{answer_pdf.stem}.md"

        # 2. 轉換PDF到Markdown
        console.print(f"[yellow]📄 轉換考卷PDF:[/yellow] {question_pdf.name}")
        question_content = convert_pdf_to_markdown(question_pdf, question_md, use_gpu)
        console.print(f"[green]✓ 考卷Markdown已保存:[/green] {question_md}")

        console.print(f"\n[yellow]📄 轉換答案PDF:[/yellow] {answer_pdf.name}")
        answer_content = convert_pdf_to_markdown(answer_pdf, answer_md, use_gpu)
        console.print(f"[green]✓ 答案Markdown已保存:[/green] {answer_md}")

        # 3. 使用LLM解析考題和答案
        console.print(f"\n[yellow]🤖 使用LLM解析考題...[/yellow]")
        questions_result = parse_questions_with_llm(question_content)
        if not questions_result:
            raise Exception("考題解析失敗")
        console.print(f"[green]✓ 考題解析完成[/green]")

        console.print(f"\n[yellow]🤖 使用LLM解析答案...[/yellow]")
        answers_result = parse_answers_with_llm(answer_content)
        if not answers_result:
            raise Exception("答案解析失敗")
        console.print(f"[green]✓ 答案解析完成[/green]")

        # 4. 合併考題和答案
        console.print(f"\n[yellow]🔗 合併考題和答案...[/yellow]")
        final_json = merge_qa_json(questions_result, answers_result)

        # 5. 保存JSON文件
        output_file = output_dir / f"{exam_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)

        console.print(f"[green]✓ JSON已保存:[/green] {output_file}")

        # 顯示統計信息
        mc_count = len(final_json.get('multiple_choice_section', {}).get('questions', []))
        console.print(f"\n[bold green]✅ 處理完成！[/bold green]")
        console.print(f"[cyan]選擇題數量:[/cyan] {mc_count}")

        return True

    except Exception as e:
        console.print(f"[red]❌ 處理失敗:[/red] {e}")
        logger.exception(e)
        return False


def main():
    """主函數"""
    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="處理單一考卷和答案PDF，轉換成JSON格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 處理單一考試
    poetry run python tools/scripts/process_single_exam.py \\
        --question data/questions/110180_1102_不動產估價概要.pdf \\
        --answer data/answer/110180_ANS1102_不動產估價概要.pdf

    # 指定輸出目錄
    poetry run python tools/scripts/process_single_exam.py \\
        --question data/questions/110180_1102_不動產估價概要.pdf \\
        --answer data/answer/110180_ANS1102_不動產估價概要.pdf \\
        --output-dir output/parsed_qa
        """
    )
    parser.add_argument(
        "--question",
        type=Path,
        required=True,
        help="考卷PDF文件路徑"
    )
    parser.add_argument(
        "--answer",
        type=Path,
        required=True,
        help="答案PDF文件路徑"
    )
    parser.add_argument(
        "--markdown-dir",
        type=Path,
        default=Path("output/markdown"),
        help="Markdown文件輸出目錄 (默認: output/markdown)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/parsed_qa"),
        help="JSON文件輸出目錄 (默認: output/parsed_qa)"
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="禁用GPU，使用CPU進行PDF轉換"
    )

    args = parser.parse_args()

    # 檢查文件是否存在
    if not args.question.exists():
        console.print(f"[red]❌ 考卷文件不存在:[/red] {args.question}")
        return 1

    if not args.answer.exists():
        console.print(f"[red]❌ 答案文件不存在:[/red] {args.answer}")
        return 1

    # 創建輸出目錄
    args.markdown_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # 確定是否使用GPU
    use_gpu = not args.no_gpu

    console.print("\n[bold cyan]📚 單一考卷處理工具[/bold cyan]")
    console.print("=" * 60)
    console.print(f"[yellow]⚙️  GPU加速:[/yellow] {'啟用' if use_gpu else '禁用'}")
    console.print(f"[yellow]📂 Markdown目錄:[/yellow] {args.markdown_dir}")
    console.print(f"[yellow]📂 JSON輸出目錄:[/yellow] {args.output_dir}")

    # 處理考試
    success = process_exam(
        args.question,
        args.answer,
        args.markdown_dir,
        args.output_dir,
        use_gpu
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
