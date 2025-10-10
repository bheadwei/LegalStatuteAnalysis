#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次生成 Embedding 結果 PDF 報告
支援 wkhtmltopdf 和 weasyprint 兩種轉換方式
"""

import subprocess
import logging
from pathlib import Path
from typing import List, Dict, Optional
import sys

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFReportGenerator:
    def __init__(self, html_dir: str, pdf_dir: str):
        """
        初始化 PDF 報告生成器

        Args:
            html_dir: HTML 報告所在目錄
            pdf_dir: PDF 輸出目錄
        """
        self.html_dir = Path(html_dir)
        self.pdf_dir = Path(pdf_dir)

        # 確保目錄存在
        self.pdf_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"HTML 目錄: {self.html_dir}")
        logger.info(f"PDF 目錄: {self.pdf_dir}")

    def check_dependencies(self) -> Dict[str, bool]:
        """檢查 PDF 生成工具是否可用"""
        tools = {}

        # 檢查 wkhtmltopdf
        try:
            result = subprocess.run(['wkhtmltopdf', '--version'],
                                    capture_output=True, text=True, timeout=10)
            tools['wkhtmltopdf'] = result.returncode == 0
            if tools['wkhtmltopdf']:
                logger.info("✅ wkhtmltopdf 可用")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            tools['wkhtmltopdf'] = False
            logger.warning("❌ wkhtmltopdf 不可用")

        # 檢查 weasyprint
        try:
            import weasyprint
            tools['weasyprint'] = True
            logger.info("✅ weasyprint 可用")
        except ImportError:
            tools['weasyprint'] = False
            logger.warning("❌ weasyprint 不可用")

        return tools

    def generate_pdf_with_wkhtmltopdf(self, html_file: Path, pdf_file: Path) -> bool:
        """
        使用 wkhtmltopdf 生成 PDF（參考 stage3_pdf_generator.py）

        Args:
            html_file: HTML 檔案路徑
            pdf_file: PDF 輸出路徑

        Returns:
            是否成功生成
        """
        try:
            # 使用經過測試的參數組合（與 stage3 一致）
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--margin-top', '15mm',
                '--margin-bottom', '15mm',
                '--margin-left', '15mm',
                '--margin-right', '15mm',
                '--encoding', 'UTF-8',
                '--enable-local-file-access',
                '--load-error-handling', 'ignore',
                '--javascript-delay', '1000',
                '--dpi', '300',
                str(html_file),
                str(pdf_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                logger.info(f"✅ PDF 已生成: {pdf_file.name}")
                return True
            else:
                logger.error(f"❌ PDF 生成失敗: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"❌ PDF 生成超時")
            return False
        except Exception as e:
            logger.error(f"❌ PDF 生成錯誤: {e}")
            return False

    def generate_pdf_with_weasyprint(self, html_file: Path, pdf_file: Path) -> bool:
        """
        使用 weasyprint 生成 PDF

        Args:
            html_file: HTML 檔案路徑
            pdf_file: PDF 輸出路徑

        Returns:
            是否成功生成
        """
        try:
            from weasyprint import HTML

            # 讀取 HTML 並生成 PDF
            html_doc = HTML(filename=str(html_file))
            html_doc.write_pdf(str(pdf_file))

            logger.info(f"✅ PDF 已生成: {pdf_file.name}")
            return True

        except Exception as e:
            logger.error(f"❌ PDF 生成錯誤: {e}")
            return False

    def generate_pdf(self, html_file: Path, tools: Dict[str, bool]) -> Optional[Path]:
        """
        生成 PDF（自動選擇可用工具）

        Args:
            html_file: HTML 檔案路徑
            tools: 可用工具字典

        Returns:
            生成的 PDF 檔案路徑，失敗則返回 None
        """
        pdf_file = self.pdf_dir / f"{html_file.stem}.pdf"

        # 優先使用 wkhtmltopdf
        if tools.get('wkhtmltopdf'):
            if self.generate_pdf_with_wkhtmltopdf(html_file, pdf_file):
                return pdf_file

        # 備用 weasyprint
        if tools.get('weasyprint'):
            if self.generate_pdf_with_weasyprint(html_file, pdf_file):
                return pdf_file

        logger.warning(f"⚠️ 無法生成 PDF: {html_file.name}")
        return None

    def batch_generate(self, exclude_index: bool = True) -> Dict[str, any]:
        """
        批次生成所有 HTML 的 PDF

        Args:
            exclude_index: 是否排除 index.html

        Returns:
            生成結果統計
        """
        # 找到所有 HTML 檔案
        html_files = sorted(self.html_dir.glob("*.html"))

        if exclude_index:
            html_files = [f for f in html_files if f.name != 'index.html']

        if not html_files:
            logger.warning(f"在 {self.html_dir} 中找不到 HTML 檔案")
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'files': []
            }

        logger.info(f"找到 {len(html_files)} 個 HTML 檔案")

        # 檢查依賴
        tools = self.check_dependencies()

        if not any(tools.values()):
            logger.error("❌ 未找到任何可用的 PDF 生成工具")
            logger.error("請安裝以下工具之一：")
            logger.error("  1. wkhtmltopdf: sudo apt-get install wkhtmltopdf")
            logger.error("  2. weasyprint: pip install weasyprint")
            return {
                'total': len(html_files),
                'success': 0,
                'failed': len(html_files),
                'files': []
            }

        # 批次生成 PDF
        generated_files = []
        failed_count = 0

        for html_file in html_files:
            pdf_file = self.generate_pdf(html_file, tools)
            if pdf_file:
                generated_files.append(pdf_file)
            else:
                failed_count += 1

        # 統計結果
        result = {
            'total': len(html_files),
            'success': len(generated_files),
            'failed': failed_count,
            'files': [str(f) for f in generated_files]
        }

        return result


def main():
    """主函數"""
    # 設定路徑
    base_path = Path("/home/bheadwei/LegalStatuteAnalysis")
    html_dir = base_path / "output" / "html_reports"
    pdf_dir = base_path / "output" / "pdf_reports"

    logger.info("=" * 60)
    logger.info("開始批次生成 PDF 報告")
    logger.info("=" * 60)

    try:
        generator = PDFReportGenerator(
            html_dir=str(html_dir),
            pdf_dir=str(pdf_dir)
        )

        # 批次生成 PDF
        result = generator.batch_generate(exclude_index=True)

        # 輸出結果
        logger.info("=" * 60)
        logger.info("PDF 生成完成")
        logger.info("=" * 60)
        logger.info(f"總檔案數: {result['total']}")
        logger.info(f"成功生成: {result['success']}")
        logger.info(f"失敗: {result['failed']}")
        logger.info(f"輸出目錄: {pdf_dir}")
        logger.info("=" * 60)

        if result['success'] > 0:
            logger.info("✅ PDF 生成成功！")
            logger.info("")
            logger.info("生成的檔案:")
            for file_path in result['files']:
                logger.info(f"  - {Path(file_path).name}")
        else:
            logger.error("❌ 沒有成功生成任何 PDF")
            logger.error("請檢查依賴是否正確安裝")

        return result['success'] > 0

    except Exception as e:
        logger.error(f"❌ PDF 生成失敗: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
