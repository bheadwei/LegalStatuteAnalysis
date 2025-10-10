"""
PDF 轉 Markdown 命令列介面
"""

import click
import logging
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

from .core import PDFToMarkdownConverter, BatchConverter


console = Console()


def setup_logging(verbose: bool = False) -> logging.Logger:
    """設置日誌記錄"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='啟用詳細輸出')
@click.pass_context
def cli(ctx, verbose):
    """PDF 轉 Markdown 工具
    
    專門處理法規條文類型的 PDF 文件轉換
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['logger'] = setup_logging(verbose)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), help='輸出文件路徑')
@click.pass_context
def convert(ctx, input_file: Path, output: Path):
    """轉換單個 PDF 文件
    
    INPUT_FILE: 要轉換的 PDF 文件路徑
    """
    logger = ctx.obj['logger']
    
    try:
        # 設置輸出路徑
        if not output:
            output = input_file.parent / f"{input_file.stem}.md"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("轉換中...", total=None)
            
            converter = PDFToMarkdownConverter(logger)
            markdown_content = converter.process_pdf(input_file, output)
            
            progress.update(task, description="✓ 轉換完成")
        
        console.print(f"\n[green]✓ 轉換成功![/green]")
        console.print(f"輸入: {input_file}")
        console.print(f"輸出: {output}")
        console.print(f"內容長度: {len(markdown_content)} 字符")
        
        # 顯示結構統計
        if converter.sections:
            table = Table(title="文件結構統計")
            table.add_column("層級", style="cyan")
            table.add_column("數量", style="magenta")
            
            level_count = {}
            for section in converter.sections:
                level_name = ["文件標題", "章節", "條文", "項目", "子項目"][section.level]
                level_count[level_name] = level_count.get(level_name, 0) + 1
            
            for level_name, count in level_count.items():
                table.add_row(level_name, str(count))
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ 轉換失敗: {e}[/red]")
        if ctx.obj['verbose']:
            logger.exception("詳細錯誤信息")
        raise click.ClickException(str(e))


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), help='輸出目錄路徑')
@click.pass_context
def batch(ctx, input_dir: Path, output_dir: Path):
    """批量轉換目錄中的所有 PDF 文件
    
    INPUT_DIR: 包含 PDF 文件的目錄
    """
    logger = ctx.obj['logger']
    
    try:
        # 設置輸出目錄
        if not output_dir:
            output_dir = input_dir / "markdown_output"
        
        # 檢查 PDF 文件
        pdf_files = list(input_dir.glob('*.pdf'))
        if not pdf_files:
            console.print(f"[yellow]⚠ 在 {input_dir} 中未找到 PDF 文件[/yellow]")
            return
        
        console.print(f"找到 {len(pdf_files)} 個 PDF 文件")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("批量轉換中...", total=len(pdf_files))
            
            batch_converter = BatchConverter(logger)
            results = batch_converter.convert_directory(input_dir, output_dir)
            
            progress.update(task, completed=len(pdf_files), description="✓ 批量轉換完成")
        
        # 顯示結果統計
        successful = len([r for r in results.values() if not r.startswith('錯誤')])
        failed = len(results) - successful
        
        console.print(f"\n[green]✓ 批量轉換完成![/green]")
        console.print(f"總文件: {len(results)}")
        console.print(f"成功: {successful}")
        console.print(f"失敗: {failed}")
        console.print(f"輸出目錄: {output_dir}")
        
        # 顯示詳細結果
        if ctx.obj['verbose'] or failed > 0:
            table = Table(title="轉換結果詳情")
            table.add_column("原文件", style="cyan")
            table.add_column("結果", style="green")
            
            for input_file, result in results.items():
                file_name = Path(input_file).name
                if result.startswith('錯誤'):
                    table.add_row(file_name, f"[red]{result}[/red]")
                else:
                    output_name = Path(result).name
                    table.add_row(file_name, f"[green]✓ {output_name}[/green]")
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]✗ 批量轉換失敗: {e}[/red]")
        if ctx.obj['verbose']:
            logger.exception("詳細錯誤信息")
        raise click.ClickException(str(e))


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True, path_type=Path))
@click.option('--lines', '-n', type=int, default=20, help='顯示行數 (預設: 20)')
@click.pass_context
def preview(ctx, markdown_file: Path, lines: int):
    """預覽轉換後的 Markdown 文件
    
    MARKDOWN_FILE: Markdown 文件路徑
    """
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines_list = content.split('\n')
        preview_content = '\n'.join(lines_list[:lines])
        
        console.print(f"\n[cyan]預覽: {markdown_file}[/cyan]")
        console.print(f"[yellow]顯示前 {lines} 行 (總共 {len(lines_list)} 行)[/yellow]\n")
        
        # 使用 Rich 的 Markdown 渲染
        from rich.markdown import Markdown
        md = Markdown(preview_content)
        console.print(md)
        
        if len(lines_list) > lines:
            console.print(f"\n[dim]... 還有 {len(lines_list) - lines} 行[/dim]")
        
    except Exception as e:
        console.print(f"[red]✗ 預覽失敗: {e}[/red]")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
