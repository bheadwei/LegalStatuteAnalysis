#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理考卷和答案PDF文件
自动将考卷PDF和答案PDF配对，转换为Markdown，然后合并成JSON格式

使用方法:
    poetry run python scripts/batch_process_exams.py --data-dir data --output-dir results

功能:
    1. 自动识别data目录下的考卷和答案PDF对
    2. 使用PDF转换器将PDF转换为Markdown
    3. 使用LLM解析器解析考题和答案
    4. 合并成JSON格式并保存
"""

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Dict, List, Tuple
import re

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
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


def find_exam_pairs(data_dir: Path) -> List[Tuple[Path, Path, str]]:
    """
    查找data目录下的考卷和答案PDF对
    支援從 questions/ 和 answer/ 子目錄讀取

    返回: List of (question_pdf, answer_pdf, exam_name)
    """
    # 檢查是否有 questions 和 answer 子目錄
    questions_dir = data_dir / "questions"
    answers_dir = data_dir / "answer"

    # 如果子目錄存在，使用子目錄；否則使用根目錄
    if questions_dir.exists() and answers_dir.exists():
        logger.info(f"檢測到子目錄結構，使用 {questions_dir} 和 {answers_dir}")
        question_search_dir = questions_dir
        answer_search_dir = answers_dir
    else:
        logger.info(f"使用單一目錄: {data_dir}")
        question_search_dir = data_dir
        answer_search_dir = data_dir

    exam_pairs = []

    # 获取所有考题PDF
    pdf_files = list(question_search_dir.glob("*.pdf"))

    # 识别考卷PDF（不含ANS的）
    question_pdfs = [f for f in pdf_files if "ANS" not in f.name]

    for question_pdf in question_pdfs:
        # 从文件名提取考试代码，例如 "112190_1201_民法概要.pdf" -> "112190_1201"
        match = re.match(r"(\d+_\d+)_(.+)\.pdf$", question_pdf.name)
        if not match:
            logger.warning(f"无法解析文件名格式: {question_pdf.name}")
            continue

        exam_code = match.group(1)  # "112190_1201"
        exam_subject = match.group(2)  # "民法概要"

        # 查找对应的答案PDF
        answer_pdf = answer_search_dir / f"{exam_code.split('_')[0]}_ANS{exam_code.split('_')[1]}_{exam_subject}.pdf"

        if answer_pdf.exists():
            exam_pairs.append((question_pdf, answer_pdf, f"{exam_code}_{exam_subject}"))
        else:
            logger.warning(f"找不到对应的答案PDF: {answer_pdf.name}")

    return exam_pairs


def convert_pdf_to_markdown(pdf_path: Path, output_path: Path, use_gpu: bool = True) -> str:
    """
    将PDF转换为Markdown

    返回: Markdown内容
    """
    try:
        converter = PDFToMarkdownConverter(logger)
        markdown_content = converter.process_pdf(pdf_path, output_path, use_gpu=use_gpu)
        return markdown_content
    except Exception as e:
        logger.error(f"PDF转换失败 {pdf_path.name}: {e}")
        raise


def process_exam_pair(
    question_pdf: Path,
    answer_pdf: Path,
    exam_name: str,
    markdown_dir: Path,
    output_dir: Path,
    skip_pdf_conversion: bool = False,
    use_gpu: bool = True
) -> Dict:
    """
    处理一对考卷和答案

    返回: 处理结果字典
    """
    result = {
        "exam_name": exam_name,
        "question_pdf": str(question_pdf),
        "answer_pdf": str(answer_pdf),
        "status": "pending"
    }

    try:
        # 1. 设置Markdown文件路径
        question_md = markdown_dir / f"{question_pdf.stem}.md"
        answer_md = markdown_dir / f"{answer_pdf.stem}.md"

        # 2. 转换PDF到Markdown（如果需要）
        if skip_pdf_conversion and question_md.exists() and answer_md.exists():
            logger.info(f"跳过PDF转换，使用现有Markdown文件")
            question_content = question_md.read_text(encoding="utf-8")
            answer_content = answer_md.read_text(encoding="utf-8")
        else:
            logger.info(f"转换考卷PDF: {question_pdf.name}")
            question_content = convert_pdf_to_markdown(question_pdf, question_md, use_gpu)

            logger.info(f"转换答案PDF: {answer_pdf.name}")
            answer_content = convert_pdf_to_markdown(answer_pdf, answer_md, use_gpu)

        result["question_md"] = str(question_md)
        result["answer_md"] = str(answer_md)

        # 3. 使用LLM解析考题和答案
        logger.info(f"使用LLM解析考题: {exam_name}")
        questions_result = parse_questions_with_llm(question_content)
        if not questions_result:
            raise Exception("考题解析失败")

        logger.info(f"使用LLM解析答案: {exam_name}")
        answers_result = parse_answers_with_llm(answer_content)
        if not answers_result:
            raise Exception("答案解析失败")

        # 4. 合并考题和答案
        logger.info(f"合并考题和答案: {exam_name}")
        final_json = merge_qa_json(questions_result, answers_result)

        # 5. 保存JSON文件
        output_file = output_dir / f"{exam_name}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)

        result["output_json"] = str(output_file)
        result["status"] = "success"
        logger.info(f"成功处理: {exam_name} -> {output_file}")

    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
        logger.error(f"处理失败 {exam_name}: {e}")

    return result


def main():
    """主函数"""
    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="批量处理考卷和答案PDF，转换成JSON格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 处理所有PDF文件
    poetry run python scripts/batch_process_exams.py

    # 指定数据目录和输出目录
    poetry run python scripts/batch_process_exams.py --data-dir data --output-dir results/exams

    # 跳过PDF转换（如果已有Markdown文件）
    poetry run python scripts/batch_process_exams.py --skip-pdf-conversion
        """
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="包含PDF文件的目录 (默认: data)"
    )
    parser.add_argument(
        "--markdown-dir",
        type=Path,
        default=Path("results/markdown"),
        help="Markdown文件输出目录 (默认: results/markdown)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/exams"),
        help="JSON文件输出目录 (默认: results/exams)"
    )
    parser.add_argument(
        "--skip-pdf-conversion",
        action="store_true",
        help="跳过PDF转换步骤（如果Markdown文件已存在）"
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        default=True,
        help="使用GPU加速PDF转换（默认：启用）"
    )
    parser.add_argument(
        "--no-gpu",
        action="store_true",
        help="禁用GPU，使用CPU进行PDF转换"
    )

    args = parser.parse_args()

    # 确定是否使用GPU
    use_gpu = not args.no_gpu if hasattr(args, 'no_gpu') else args.use_gpu

    # 创建输出目录
    args.markdown_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    console.print("\n[bold cyan]📚 考卷答案批量处理工具[/bold cyan]")
    console.print("=" * 60)
    console.print(f"[yellow]⚙️  GPU加速:[/yellow] {'启用' if use_gpu else '禁用'}")

    # 1. 查找考卷答案对
    console.print(f"\n[yellow]🔍 扫描目录:[/yellow] {args.data_dir}")
    exam_pairs = find_exam_pairs(args.data_dir)

    if not exam_pairs:
        console.print("[red]❌ 未找到考卷和答案PDF对！[/red]")
        console.print("\n[yellow]提示：[/yellow]")
        console.print("  - 考卷文件格式: 112190_1201_民法概要.pdf")
        console.print("  - 答案文件格式: 112190_ANS1201_民法概要.pdf")
        return

    # 显示找到的文件对
    table = Table(title=f"找到 {len(exam_pairs)} 对考卷答案")
    table.add_column("序号", style="cyan", width=6)
    table.add_column("考试科目", style="green")
    table.add_column("考卷文件", style="yellow")
    table.add_column("答案文件", style="magenta")

    for idx, (q_pdf, a_pdf, exam_name) in enumerate(exam_pairs, 1):
        table.add_row(
            str(idx),
            exam_name.split('_', 2)[-1],  # 提取科目名
            q_pdf.name,
            a_pdf.name
        )

    console.print(table)

    # 2. 处理每一对考卷答案
    console.print(f"\n[yellow]🚀 开始批量处理...[/yellow]")
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]处理中...", total=len(exam_pairs))

        for question_pdf, answer_pdf, exam_name in exam_pairs:
            progress.update(task, description=f"[cyan]处理: {exam_name}")

            result = process_exam_pair(
                question_pdf,
                answer_pdf,
                exam_name,
                args.markdown_dir,
                args.output_dir,
                args.skip_pdf_conversion,
                use_gpu
            )
            results.append(result)

            progress.advance(task)

    # 3. 显示处理结果
    console.print("\n[bold green]✅ 批量处理完成！[/bold green]")
    console.print("=" * 60)

    success_count = len([r for r in results if r["status"] == "success"])
    failed_count = len([r for r in results if r["status"] == "failed"])

    # 统计表
    stats_table = Table(title="处理统计")
    stats_table.add_column("项目", style="cyan")
    stats_table.add_column("数量", style="magenta", justify="right")
    stats_table.add_row("总数", str(len(results)))
    stats_table.add_row("成功", f"[green]{success_count}[/green]")
    stats_table.add_row("失败", f"[red]{failed_count}[/red]")
    console.print(stats_table)

    # 详细结果表
    result_table = Table(title="详细结果")
    result_table.add_column("序号", style="cyan", width=6)
    result_table.add_column("考试科目", style="green")
    result_table.add_column("状态", style="yellow")
    result_table.add_column("输出文件", style="magenta")

    for idx, result in enumerate(results, 1):
        subject = result["exam_name"].split('_', 2)[-1]

        if result["status"] == "success":
            status_text = "[green]✓ 成功[/green]"
            output = Path(result["output_json"]).name
        else:
            status_text = f"[red]✗ 失败[/red]"
            output = result.get("error", "未知错误")[:40]

        result_table.add_row(str(idx), subject, status_text, output)

    console.print(result_table)

    # 保存处理报告
    report_file = args.output_dir / "processing_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "total": len(results),
            "success": success_count,
            "failed": failed_count,
            "results": results
        }, f, ensure_ascii=False, indent=2)

    console.print(f"\n[cyan]📄 处理报告已保存到:[/cyan] {report_file}")

    if success_count > 0:
        console.print(f"\n[green]✓ JSON文件已保存到:[/green] {args.output_dir}")
        console.print(f"[green]✓ Markdown文件已保存到:[/green] {args.markdown_dir}")


if __name__ == "__main__":
    main()
