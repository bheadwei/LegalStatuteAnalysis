# PDF 轉 Markdown 模組

基於 [MinerU](https://github.com/opendatalab/MinerU) 高品質 PDF 轉換工具，專門處理法規條文類型的 PDF 文件轉換，能夠自動識別文件結構並轉換為結構化的 Markdown 格式。

## 功能特色

- 🚀 **MinerU 驅動**: 基於頂級開源 PDF 轉換工具 MinerU（42k+ stars）
- 🔍 **智能版面分析**: 使用 AI 模型進行精確的版面檢測和文字識別
- 📄 **高品質轉換**: 保持原文件的邏輯結構、表格和格式
- ⚡ **批量處理**: 支援目錄中多個 PDF 文件的批量轉換
- 🎯 **OCR 支援**: 支援掃描版 PDF 和圖片文字識別
- 🔧 **程式化介面**: 提供完整的 Python API
- 🖥️ **命令列工具**: 便捷的 CLI 操作介面

## 系統要求

根據 [MinerU 官方文檔](https://github.com/opendatalab/MinerU#local-deployment)：

| 項目 | 要求 |
|------|------|
| 操作系統 | Linux / Windows / macOS |
| 記憶體 | 最少 16GB+，建議 32GB+ |
| 硬碟空間 | 20GB+，建議 SSD |
| Python 版本 | 3.10-3.13 |
| GPU（可選） | Turing 架構及以上，6GB+ VRAM |

## 安裝依賴

```bash
pip install -r requirements.txt
```

### 依賴套件

- `mineru[core]`: 高品質 PDF 轉換核心
- `rich`: 美化命令列輸出
- `click`: 命令列介面框架

## 使用方法

### 命令列工具

#### 查看幫助
```bash
python main.py --help
```

#### 轉換單個文件
```bash
python main.py convert data/不動產經紀業管理條例.pdf
```

#### 指定輸出路徑
```bash
python main.py convert data/不動產經紀業管理條例.pdf -o output/converted.md
```

#### 批量轉換目錄
```bash
python main.py batch data/ -o output/markdown/
```

#### 預覽轉換結果
```bash
python main.py preview output/不動產經紀業管理條例.md
```

### Python API

#### 基本使用

```python
from pdf_to_markdown import PDFToMarkdownConverter
from pathlib import Path

# 初始化轉換器
converter = PDFToMarkdownConverter()

# 轉換單個文件
input_file = Path("data/法規文件.pdf")
output_file = Path("output/法規文件.md")
markdown_content = converter.process_pdf(input_file, output_file)

print(f"轉換完成，生成 {len(markdown_content)} 字符")
```

#### 批量轉換

```python
from pdf_to_markdown import BatchConverter
from pathlib import Path

# 初始化批量轉換器
batch_converter = BatchConverter()

# 轉換目錄中的所有 PDF
input_dir = Path("data")
output_dir = Path("output/markdown")
results = batch_converter.convert_directory(input_dir, output_dir)

for pdf_file, result in results.items():
    print(f"{pdf_file} -> {result}")
```

#### 分步處理

```python
from pdf_to_markdown import PDFToMarkdownConverter

converter = PDFToMarkdownConverter()

# 1. 提取 PDF 文字
pages_content = converter.extract_text_from_pdf(pdf_path)

# 2. 識別文件結構
sections = converter.identify_legal_structure(pages_content)

# 3. 轉換為 Markdown
markdown_content = converter.convert_to_markdown(sections)
```

## 文件結構識別

模組能夠自動識別以下法規文件結構：

### 支援的結構層級

1. **文件標題** (`# 標題`)
   - 條例、法律、規則、辦法、細則等

2. **章節** (`## 第X章`)
   - 第一章、第二章等章節劃分

3. **條文** (`### 第X條`)
   - 法規的基本條文單位

4. **項目** (`#### 項目`)
   - 條文下的具體項目

5. **子項目** (`##### 子項目`)
   - 項目下的細分內容

### 識別模式

- **章節**: `第[數字/中文數字]章 標題`
- **條文**: `第[數字/中文數字]條 內容`
- **項目**: `[數字/中文數字]. 內容`
- **子項目**: `([數字/中文數字]) 內容`

## 轉換範例

### 輸入 PDF 內容
```
不動產經紀業管理條例

第一章 總則

第一條 為健全不動產經紀業之經營及管理...

第二條 本條例所稱主管機關...

第二章 經紀業之設立

第三條 經營不動產經紀業...
```

### 輸出 Markdown
```markdown
# 不動產經紀業管理條例

## 第一章 總則

### 第一條

為健全不動產經紀業之經營及管理...

### 第二條

本條例所稱主管機關...

## 第二章 經紀業之設立

### 第三條

經營不動產經紀業...
```

## 目錄結構

```
VibeCoding_Workflow_Templates/
├── pdf_to_markdown/
│   ├── __init__.py          # 模組初始化
│   ├── core.py              # 核心轉換邏輯
│   └── cli.py               # 命令列介面
├── data/                    # 測試 PDF 文件
├── output/                  # 輸出目錄
├── main.py                  # 主程式入口
├── example.py               # 使用範例
├── requirements.txt         # 依賴套件
└── README.md               # 說明文件
```

## 運行範例

```bash
# 運行完整範例
python example.py
```

這會演示：
- 單文件轉換
- 批量轉換
- 程式化使用

## 日誌記錄

模組提供詳細的日誌記錄功能：

```python
import logging

# 啟用詳細日誌
logging.basicConfig(level=logging.DEBUG)

converter = PDFToMarkdownConverter()
# 轉換過程會輸出詳細日誌
```

## 錯誤處理

模組具備完善的錯誤處理機制：

- PDF 讀取錯誤
- 文字編碼問題
- 文件結構識別異常
- 文件寫入錯誤

## 性能考量

- 支援大型 PDF 文件處理
- 記憶體使用優化
- 批量處理效率提升

## 自訂擴展

### 自訂結構識別模式

```python
class CustomConverter(PDFToMarkdownConverter):
    def identify_legal_structure(self, pages_content):
        # 自訂結構識別邏輯
        pass
```

### 自訂 Markdown 格式

```python
def custom_format_content(self, content):
    # 自訂內容格式化
    return formatted_content
```

## 限制說明

根據 [MinerU 官方說明](https://github.com/opendatalab/MinerU#known-issues)：

- 極其複雜版面下可能出現閱讀順序錯誤
- 對垂直文字的支援有限
- 某些罕見語言的 OCR 識別可能不準確
- 部分公式在 Markdown 中可能渲染不正確
- 漫畫書、美術畫冊等特殊文件類型解析效果有限

## 技術細節

### PDF 處理
- 基於 [MinerU](https://github.com/opendatalab/MinerU) 進行高品質 PDF 解析
- 使用 AI 模型進行版面分析和文字識別
- 支援複雜表格、公式和圖片處理
- 內建 OCR 引擎，支援掃描版 PDF

### 結構識別
- MinerU 內建智能版面分析
- 自動識別標題、段落、表格、列表
- 支援多欄位版面和複雜結構
- AI 驅動的閱讀順序判斷

### Markdown 生成
- 標準 Markdown 格式輸出
- 保持原文件邏輯結構和格式
- 支援表格、公式和多級標題
- 智能後處理和格式優化

## 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個工具。

## 授權條款

本專案採用 MIT 授權條款。
