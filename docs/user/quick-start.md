# 快速入門指南 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **適用對象**：初次使用者
> **預計時間**：10-15 分鐘

---

## 🎯 關於本系統

LegalStatuteAnalysis_V1 是基於 LLM（大型語言模型）的智能分析工具，專門用於分析考試題目與相關法規條文的對應關係。系統能夠自動識別題目內容並智能匹配相關法條，生成詳細的對應分析報告。

**核心功能：**
- 🤖 **LLM 驅動**：支援 OpenAI、Claude、Gemini 多種 LLM 提供者
- 🔍 **智能分析**：使用 AI 模型進行精確的題目與法條對應分析
- 📊 **結構化輸出**：生成詳細的對應報告和統計分析
- ⚡ **批量處理**：支援大量考試題目的批量分析
- 🖥️ **命令列工具**：便捷的 CLI 操作介面

---

## 📋 系統要求

### 必要條件

| 項目 | 要求 |
|------|------|
| 操作系統 | Linux / Windows / macOS |
| Python 版本 | 3.12-3.13 |
| 記憶體 | 建議 4GB+ |
| 硬碟空間 | 至少 500MB |

### 可選條件

| 功能 | 要求 |
|------|------|
| **LLM 分析** | OpenAI 或 Claude API 金鑰（可選，支援模擬模式） |
| **PDF 處理** | MinerU（需要 16GB+ 記憶體） |
| **GPU 加速** | PyTorch + Transformers |

---

## ⚙️ 安裝步驟

### 1. 克隆專案

```bash
git clone git@github.com:bheadwei/LegalStatuteAnalysis.git
cd LegalStatuteAnalysis_V1
```

### 2. 建立虛擬環境

```bash
# Linux/WSL/macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 安裝依賴

**使用 Poetry（推薦）：**
```bash
# 安裝 Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 安裝基本依賴
poetry install

# 安裝可選功能
poetry install --extras pdf    # PDF 處理功能
poetry install --extras gpu    # GPU 支援
poetry install --extras all    # 所有功能
```

**使用 pip：**
```bash
pip install -r requirements.txt
```

### 4. 環境變數設定

建立 `.env` 文件：

```bash
# 複製範例檔案
cp src/main/resources/config/.env.example .env

# 編輯配置
nano .env
```

**配置內容：**
```env
# OpenAI API（如果使用）
OPENAI_API_KEY=your_openai_api_key_here

# Claude API（如果使用）
ANTHROPIC_API_KEY=your_claude_api_key_here

# Gemini API（如果使用）
GEMINI_API_KEY=your_gemini_api_key_here

# LLM 提供者選擇
LLM_PROVIDER=simulation  # simulation | openai | claude | gemini
```

---

## 🚀 第一次使用

### 驗證安裝

測試系統是否正確安裝：

```bash
# 使用模擬模式（無需 API 金鑰）
python tools/scripts/run_core_embedding.py --provider simulation --limit 1

# 預期輸出
🎯 法條考題智能對應系統 - 資料模型版本
============================================================
📋 載入系統配置: src/main/resources/config/law_config.json
✅ 系統配置載入完成 (版本: 3.0)
🛠️ 初始化對應服務...
✅ 成功載入 269 條法規條文
🔍 建立法條搜尋索引，共 269 條法規
🤖 開始分析 (LLM: simulation)
✅ 分析完成！
```

如果看到上述輸出，恭喜！系統安裝成功。

### 基本使用流程

#### 1. 快速體驗（模擬模式）

```bash
# 分析前 5 道題目
python tools/scripts/run_core_embedding.py --provider simulation --limit 5
```

#### 2. 使用真實 LLM

**OpenAI GPT：**
```bash
python tools/scripts/run_core_embedding.py --provider openai --limit 10
```

**Claude：**
```bash
python tools/scripts/run_core_with_gemini.py --provider claude --limit 10
```

**Gemini：**
```bash
python tools/scripts/run_core_with_gemini.py --provider gemini --limit 10
```

#### 3. 完整分析

```bash
# 分析所有題目（可能需要較長時間）
python tools/scripts/run_core_embedding.py --provider openai
```

---

## 📊 查看結果

### 分析報告位置

分析完成後，結果文件位於：

```
results/
├── mapping_report_model_based.json    # 主要分析報告
├── detailed_analysis.json             # 詳細分析結果
├── statistics_summary.json            # 統計摘要
└── analysis_log.txt                   # 分析日誌
```

### 快速檢視結果

**檢視分析統計：**
```bash
python -c "
import json
with open('results/mapping_report_model_based.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
metadata = data['metadata']
print(f'總題目數: {metadata[\"total_questions\"]}')
print(f'成功分析: {metadata.get(\"successful_analyses\", \"N/A\")}')
print(f'平均信心度: {metadata[\"average_confidence\"]:.3f}')
print(f'成功率: {metadata[\"success_rate\"]:.1%}')
print(f'使用 LLM: {metadata[\"llm_provider\"]} ({metadata[\"model\"]})')
"
```

**範例輸出：**
```
總題目數: 27
成功分析: 20
平均信心度: 0.756
成功率: 74.1%
使用 LLM: openai (gpt-4o-mini)
```

---

## 🔧 常用指令

### 主要分析指令

```bash
# 基本分析（推薦新手）
python tools/scripts/run_core_embedding.py --provider simulation --limit 5

# 使用不同 LLM 提供者
python tools/scripts/run_core_embedding.py --provider openai --limit 20
python tools/scripts/run_core_with_gemini.py --provider claude --limit 20
python tools/scripts/run_core_with_gemini.py --provider gemini --limit 20

# 完整批量分析
python tools/scripts/run_core_embedding.py --provider openai

# 指定配置檔案
python tools/scripts/run_core_embedding.py --config custom_config.json
```

### 輔助工具指令

```bash
# 檢查分析品質
python tools/scripts/check_analysis_quality.py

# 格式化分析結果
python tools/scripts/format_embedding_results.py

# 產生完整報告
python tools/scripts/generate_complete_law_notes.py

# 批量列印報告
python tools/scripts/batch_print.py
```

### PDF 處理指令（可選）

```bash
# 轉換 PDF 文件為 Markdown
python tools/scripts/convert_pdf.py

# 檢查 PDF 轉換品質
python tools/scripts/check_pdf_quality.py

# 簡易 PDF 轉換
python tools/scripts/simple_pdf_converter.py
```

---

## ⚠️ 故障排除

### 常見問題及解決方案

#### 1. 模組導入錯誤

**錯誤訊息：**
```
ModuleNotFoundError: No module named 'src'
```

**解決方案：**
```bash
# 確保在專案根目錄執行指令
pwd  # 應該顯示 .../LegalStatuteAnalysis_V1

# 如果不在根目錄，切換到正確位置
cd /path/to/LegalStatuteAnalysis_V1
```

#### 2. API 金鑰錯誤

**錯誤訊息：**
```
OpenAI API 金鑰未設置
Authentication failed
```

**解決方案：**
```bash
# 方法 1：設定環境變數
export OPENAI_API_KEY="your_api_key"

# 方法 2：使用 .env 文件
echo "OPENAI_API_KEY=your_api_key" >> .env

# 方法 3：使用模擬模式測試
python tools/scripts/run_core_embedding.py --provider simulation
```

#### 3. 依賴套件問題

**錯誤訊息：**
```
ImportError: No module named 'openai'
```

**解決方案：**
```bash
# 重新安裝依賴
pip install -r requirements.txt

# 或使用 Poetry
poetry install
```

#### 4. 配置檔案找不到

**錯誤訊息：**
```
FileNotFoundError: 找不到配置檔案
```

**解決方案：**
```bash
# 檢查配置檔案是否存在
ls src/main/resources/config/law_config.json

# 如果不存在，檢查檔案是否在正確位置
find . -name "law_config.json"
```

#### 5. 記憶體不足

**錯誤訊息：**
```
MemoryError: Unable to allocate array
```

**解決方案：**
```bash
# 限制處理數量
python tools/scripts/run_core_embedding.py --limit 10

# 或分批處理
for i in {0..2}; do
    python tools/scripts/run_core_embedding.py --offset $((i*10)) --limit 10
done
```

---

## 🎓 進階使用

### 自訂配置

**編輯系統配置：**
```bash
nano src/main/resources/config/law_config.json
```

**主要配置項目：**
- `llm_config` - LLM 提供者設定
- `law_definitions` - 法條定義
- `exam_sets` - 考試資料集

### Python API 使用

**基本 API 範例：**
```python
import asyncio
from src.main.python.models import SystemConfig
from src.main.python.core import EmbeddingMatcher

async def analyze_custom_question():
    # 載入配置
    config = SystemConfig.load_from_file(
        "src/main/resources/config/law_config.json"
    )

    # 初始化分析器
    matcher = EmbeddingMatcher(config)
    await matcher.initialize_llm("openai")

    # 建立自訂問題
    from src.main.python.models import ExamQuestion, QuestionType

    question = ExamQuestion(
        question_id="CUSTOM_001",
        content="不動產經紀業者應於營業處所明顯處揭示哪些資訊？",
        question_type=QuestionType.MULTIPLE_CHOICE
    )

    # 分析問題
    result = await matcher.analyze_question(question)

    if result:
        print(f"信心度: {result.confidence:.2f}")
        print(f"匹配法條: {result.matched_articles}")
        print(f"分析推理: {result.reasoning}")

# 執行分析
asyncio.run(analyze_custom_question())
```

---

## 📚 下一步

完成快速入門後，建議閱讀：

1. **[進階使用指南](./advanced-usage.md)** - 深入功能與自訂配置
2. **[API 文檔](../api/)** - 程式化使用方式
3. **[開發指南](../dev/)** - 了解系統架構和開發原則
4. **[故障排除](./troubleshooting.md)** - 詳細的問題解決方案

### 社群支援

如果遇到問題：
1. 查看 [故障排除文檔](./troubleshooting.md)
2. 檢查 [GitHub Issues](https://github.com/bheadwei/LegalStatuteAnalysis/issues)
3. 查閱 [開發指南](../dev/development-guide.md) 了解系統設計理念

---

## 🎯 總結

恭喜！您已經成功：

- ✅ 安裝並配置了 LegalStatuteAnalysis_V1
- ✅ 完成第一次分析測試
- ✅ 了解基本使用方式
- ✅ 學會查看和理解分析結果

**下一步建議：**
- 使用真實 LLM API 進行更準確的分析
- 嘗試分析自己的考題資料
- 探索進階功能和自訂選項

**記住：** 系統遵循 Linus Torvalds 的實用主義原則 - 簡單、可靠、專注於解決實際問題。如果遇到複雜情況，優先考慮簡單的解決方案。