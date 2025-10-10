"""
PDF 轉 Markdown 核心模組
基於 MinerU 高品質 PDF 轉換工具
專門處理法規條文類型的 PDF 文件
"""

import re
import logging
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DocumentSection:
    """文件章節結構"""
    level: int
    title: str
    content: str
    start_page: int
    end_page: Optional[int] = None


class PDFToMarkdownConverter:
    """PDF 轉 Markdown 轉換器 - 基於 MinerU"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or self._setup_logger()
        self.sections: List[DocumentSection] = []
        self._check_mineru_installation()
        
    def _setup_logger(self) -> logging.Logger:
        """設置日誌"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def _check_mineru_installation(self):
        """檢查 MinerU 是否正確安裝"""
        try:
            result = subprocess.run(['mineru', '--help'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                self.logger.info("MinerU 已正確安裝並可用")
            else:
                self.logger.warning("MinerU 命令返回非零退出碼")
        except subprocess.TimeoutExpired:
            self.logger.warning("MinerU 檢查超時，但可能仍可正常工作")
        except FileNotFoundError:
            self.logger.error("MinerU 命令未找到")
            raise RuntimeError("請先安裝 MinerU: pip install -U 'mineru[core]'")
    
    def _run_mineru(self, pdf_path: Path, output_dir: Path, use_gpu: bool = True) -> Path:
        """運行 MinerU 進行 PDF 轉換

        Args:
            pdf_path: PDF 檔案路徑
            output_dir: 輸出目錄
            use_gpu: 是否使用 GPU 加速（預設為 True）
        """
        self.logger.info(f"使用 MinerU 處理 PDF: {pdf_path}")
        if use_gpu:
            self.logger.info("GPU 加速已啟用 (CUDA)")

        try:
            # 確保輸出目錄存在
            output_dir.mkdir(parents=True, exist_ok=True)

            # 構建 MinerU 命令 - 使用絕對路徑
            abs_pdf_path = pdf_path.resolve()
            abs_output_dir = output_dir.resolve()
            cmd = ['mineru', '-p', str(abs_pdf_path), '-o', str(abs_output_dir)]

            # 添加 GPU 設定
            if use_gpu:
                cmd.extend(['-d', 'cuda'])
            
            # 運行 MinerU
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300,  # 5分鐘超時
                cwd=output_dir.parent
            )
            
            if result.returncode != 0:
                self.logger.error(f"MinerU 運行失敗: {result.stderr}")
                raise RuntimeError(f"MinerU 轉換失敗: {result.stderr}")
            
            # MinerU 會在輸出目錄下創建子目錄結構：{pdf_stem}/auto/
            pdf_stem = pdf_path.stem
            mineru_output_dir = output_dir / pdf_stem / "auto"
            
            # 查找生成的 markdown 文件
            markdown_files = list(mineru_output_dir.glob("*.md"))
            if not markdown_files:
                # 備用：在整個輸出目錄中搜索
                markdown_files = list(output_dir.rglob("*.md"))
            
            if not markdown_files:
                raise RuntimeError(f"MinerU 未生成 Markdown 文件，預期位置: {mineru_output_dir}")
            
            # 返回第一個 markdown 文件
            markdown_file = markdown_files[0]
            self.logger.info(f"MinerU 轉換完成: {markdown_file}")
            return markdown_file
            
        except subprocess.TimeoutExpired:
            self.logger.error("MinerU 運行超時")
            raise RuntimeError("MinerU 轉換超時，請檢查文件大小或系統資源")
        except Exception as e:
            self.logger.error(f"MinerU 運行異常: {e}")
            raise
    
    def _post_process_markdown(self, markdown_content: str) -> str:
        """後處理 MinerU 生成的 Markdown 內容"""
        self.logger.info("開始後處理 Markdown 內容...")
        
        # 基本清理
        # 移除多餘的空行
        markdown_content = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown_content)
        
        # 修正標題格式（確保標題前後有適當的空行）
        markdown_content = re.sub(r'\n(#{1,6}\s+[^\n]+)\n', r'\n\n\1\n\n', markdown_content)
        
        # 移除頁眉頁腳的常見模式
        markdown_content = re.sub(r'頁次：\d+', '', markdown_content)
        markdown_content = re.sub(r'第\s*\d+\s*頁', '', markdown_content)
        
        return markdown_content.strip()
    
    def _analyze_markdown_structure(self, markdown_content: str) -> List[DocumentSection]:
        """分析 Markdown 內容結構（用於統計）"""
        self.logger.info("分析 Markdown 結構...")
        sections = []
        
        lines = markdown_content.split('\n')
        current_page = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 識別 Markdown 標題
            if line.startswith('#'):
                # 計算標題級別
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # 提取標題內容
                title = line[level:].strip()
                
                if title:
                    sections.append(DocumentSection(
                        level=level - 1,  # 轉換為 0-based
                        title=title,
                        content='',
                        start_page=current_page
                    ))
        
        self.logger.info(f"識別出 {len(sections)} 個結構元素")
        self.sections = sections
        return sections
    
    def process_pdf(self, pdf_path: Path, output_path: Optional[Path] = None) -> str:
        """處理單個 PDF 文件 - 使用 MinerU"""
        try:
            # 創建臨時目錄用於 MinerU 輸出
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 使用 MinerU 轉換 PDF
                mineru_output = self._run_mineru(pdf_path, temp_path)
                
                # 讀取 MinerU 生成的 Markdown
                with open(mineru_output, 'r', encoding='utf-8') as f:
                    raw_markdown = f.read()
                
                # 後處理 Markdown 內容
                markdown_content = self._post_process_markdown(raw_markdown)
                
                # 分析結構（用於統計）
                self._analyze_markdown_structure(markdown_content)
                
                # 保存文件
                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    self.logger.info(f"Markdown 文件已保存至: {output_path}")
                
                return markdown_content
            
        except Exception as e:
            self.logger.error(f"處理 PDF 失敗: {e}")
            raise
    
    # 保留舊方法以維持介面兼容性
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict]:
        """提取文字內容（兼容方法）"""
        self.logger.warning("extract_text_from_pdf 已棄用，請使用 process_pdf")
        # 返回空列表以維持兼容性
        return []
    
    def identify_legal_structure(self, pages_content: List[Dict]) -> List[DocumentSection]:
        """識別法規條文結構（兼容方法）"""
        self.logger.warning("identify_legal_structure 已棄用，結構分析已整合到 process_pdf")
        return self.sections
    
    def convert_to_markdown(self, sections: List[DocumentSection]) -> str:
        """轉換為 Markdown（兼容方法）"""
        self.logger.warning("convert_to_markdown 已棄用，轉換已整合到 process_pdf")
        return ""


class BatchConverter:
    """批量轉換器"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.converter = PDFToMarkdownConverter(logger)
        self.logger = logger or self.converter.logger
    
    def convert_directory(self, input_dir: Path, output_dir: Path) -> Dict[str, str]:
        """轉換目錄中的所有 PDF"""
        self.logger.info(f"開始批量轉換: {input_dir} -> {output_dir}")
        
        pdf_files = list(input_dir.glob('*.pdf'))
        if not pdf_files:
            self.logger.warning("未找到 PDF 文件")
            return {}
        
        results = {}
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for pdf_file in pdf_files:
            try:
                output_file = output_dir / f"{pdf_file.stem}.md"
                markdown_content = self.converter.process_pdf(pdf_file, output_file)
                results[str(pdf_file)] = str(output_file)
                self.logger.info(f"✓ {pdf_file.name} -> {output_file.name}")
                
            except Exception as e:
                self.logger.error(f"✗ {pdf_file.name} 轉換失敗: {e}")
                results[str(pdf_file)] = f"錯誤: {e}"
        
        self.logger.info(f"批量轉換完成，成功: {len([r for r in results.values() if not r.startswith('錯誤')])} / {len(pdf_files)}")
        return results
