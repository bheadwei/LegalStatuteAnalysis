# LegalStatuteAnalysis - 法律文件與法條智能對應系統

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-1.7+-purple.svg)](https://python-poetry.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-green.svg)](https://openai.com/)

## 📋 專案簡介

自動化法律文件（如考試題目、案例）與相關法條的對應系統。透過 Embedding 與 LLM 智能匹配，快速、準確地找出文本內容所對應的法條，並產出清晰的 HTML 報告。

## 🎯 核心功能

1. **PDF 解析考題** - 自動讀取並解析 PDF 格式的考卷與答案（使用 MinerU + GPU 加速）
2. **法條 Embedding** - 將法律條文轉換為向量，建立語義搜索資料庫
3. **LLM 智能對應** - 利用 OpenAI Embedding 和 LLM 進行智能匹配
4. **HTML 報告生成** - 結構化匹配結果，生成清晰的 HTML 報告
5. **批次處理** - 支援批量處理多份考卷

## 📊 成功標準

- **對應準確率**：> 90%
- **處理速度**：< 5 秒/題
- **報告品質**：內容正確、格式清晰、無錯誤

## 🚀 快速開始

### 1. 環境需求

- Python 3.9+
- Poetry 1.7+
- CUDA（可選，用於 GPU 加速 PDF 轉換）
- OpenAI API Key

### 2. 安裝依賴

使用 Poetry 安裝：

```bash
# 安裝 Poetry（如果尚未安裝）
curl -sSL https://install.python-poetry.org | python3 -

# 安裝專案依賴
poetry install
```

或使用傳統 pip：

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

```bash
cp .env.example .env
# 編輯 .env 填入以下資訊：
# OPENAI_API_KEY=your_api_key_here
```

## 📖 完整操作流程

### 🔄 方式一：單一考卷處理（推薦新手）

處理單份考卷（考題 + 答案）到最終 HTML 報告：

```bash
# 1. PDF 轉 JSON（需要考題 PDF 和答案 PDF）
poetry run python tools/scripts/process_single_exam.py \
  --question data/questions/113190_1302_不動產估價概要.pdf \
  --answer data/answer/113190_ANS1302_不動產估價概要.pdf \
  --markdown-dir output/markdown \
  --output-dir output/parsed_qa

# 2. 轉換為對應格式
poetry run python tools/scripts/convert_qa_format.py

# 3. 執行 Embedding 對應（使用法條資料庫）
poetry run python tools/scripts/run_embedding_matching.py

# 4. 生成 HTML 報告
poetry run python tools/scripts/convert_embedded_results_to_html.py
```

**輸出位置**：`output/html_reports/index.html`

### 🚄 方式二：批次處理（處理多份考卷）

處理資料夾內的所有考卷：

```bash
# 批次處理所有 PDF
poetry run python tools/scripts/batch_process_exams.py \
  --questions-dir data/questions \
  --answers-dir data/answer \
  --output-dir output/parsed_qa

# 後續步驟同方式一的步驟 2-4
```

### ⚡ 方式三：完整流水線（一鍵到底）

```bash
# 執行完整流程（PDF → JSON → Embedding → HTML）
poetry run python tools/scripts/run_complete_pipeline.py \
  --input-dir data \
  --output-dir output
```

## 📁 專案結構

```
LegalStatuteAnalysis/
├── 📄 CLAUDE.md                        # Claude Code 協作配置（人類主導版）
├── 📄 README.md                        # 專案文件（本檔案）
├── 📄 pyproject.toml                   # Poetry 專案配置
├── 📄 .env.example                     # 環境變數範例
├── 📄 .gitignore                       # Git 忽略規則
│
├── 📁 src/                             # 原始碼
│   ├── 📁 core_embedding/              # 核心 Embedding 邏輯
│   │   ├── embedding_matcher.py        # OpenAI Embedding 對應器
│   │   └── gemini_embedding_matcher.py # Gemini Embedding 對應器（實驗性）
│   ├── 📁 models/                      # 資料模型
│   │   ├── law_models.py               # 法條資料模型
│   │   └── data_loaders.py             # 資料載入器
│   ├── 📁 parsing/                     # LLM 解析模組
│   │   └── llm_parser.py               # LangChain LLM 解析器
│   ├── 📁 pdf_converter/               # PDF 轉換模組
│   │   ├── core.py                     # MinerU PDF 轉換核心
│   │   └── cli.py                      # CLI 介面
│   └── 📁 test/                        # 測試
│       ├── unit/                       # 單元測試
│       └── integration/                # 整合測試
│
├── 📁 tools/scripts/                   # 執行腳本（主要操作入口）
│   ├── process_single_exam.py          # ⭐ 單一考卷處理
│   ├── batch_process_exams.py          # ⭐ 批次考卷處理
│   ├── run_complete_pipeline.py        # ⭐ 完整流水線
│   ├── convert_qa_format.py            # 格式轉換
│   ├── run_embedding_matching.py       # Embedding 對應
│   ├── convert_embedded_results_to_html.py  # HTML 生成
│   └── prepare_laws_csv.py             # 法條資料準備
│
├── 📁 data/                            # 原始資料
│   ├── 📁 questions/                   # 考題 PDF
│   ├── 📁 answer/                      # 答案 PDF
│   └── 📁 laws/                        # 法條資料（CSV/JSON）
│
├── 📁 output/                          # 輸出檔案（所有處理結果）
│   ├── 📁 markdown/                    # PDF 轉換的 Markdown
│   ├── 📁 parsed_qa/                   # 解析後的考題 JSON
│   ├── 📁 qa_mapped/                   # 格式化的考題對應
│   ├── 📁 embedded_results/            # Embedding 對應結果
│   └── 📁 html_reports/                # 最終 HTML 報告
│       ├── index.html                  # 📊 總覽頁（從這裡開始）
│       └── *_embedded.html             # 各考卷詳細報告
│
└── 📁 docs/                            # 文件
    ├── api/                            # API 文件
    ├── dev/                            # 開發指南
    └── user/                           # 使用者手冊
```

## 🔑 重要腳本說明

### 主要腳本（按使用頻率排序）

| 腳本名稱 | 功能 | 使用場景 |
|---------|------|---------|
| `process_single_exam.py` | 處理單一考卷（PDF→JSON） | 新增單份考卷 |
| `convert_qa_format.py` | 轉換 JSON 格式 | 準備 Embedding |
| `run_embedding_matching.py` | 執行法條對應 | 智能匹配法條 |
| `convert_embedded_results_to_html.py` | 生成 HTML 報告 | 產出最終報告 |
| `batch_process_exams.py` | 批次處理考卷 | 處理多份考卷 |
| `run_complete_pipeline.py` | 完整流水線 | 一鍵處理 |

### 輔助腳本

| 腳本名稱 | 功能 |
|---------|------|
| `prepare_laws_csv.py` | 準備法條資料庫 |
| `reprocess_single_exam.py` | 重新處理特定考卷 |
| `test_core_embedding.py` | 測試 Embedding 功能 |

## 🛠️ 技術棧

- **開發語言**：Python 3.9+
- **依賴管理**：Poetry
- **LLM Provider**：OpenAI API (GPT-4o-mini)
- **Embedding**：OpenAI text-embedding-3-large
- **PDF 轉換**：MinerU (支援 GPU CUDA 加速)
- **LLM 框架**：LangChain
- **資料驗證**：Pydantic
- **使用模式**：CLI 命令列工具

## 📝 開發指南

請閱讀 [CLAUDE.md](CLAUDE.md) 了解完整的開發規範和協作流程。

### 關鍵開發原則

1. **人類主導**：Claude 是副駕駛，人類是決策者
2. **Linus 哲學**：好品味、簡潔、實用主義
3. **預防技術債**：先搜尋現有功能，避免重複
4. **強制提交**：每完成一個階段必須 Git commit + push

## 🔧 配置說明

### OpenAI API 配置

在 `.env` 檔案設定：

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

### PDF 轉換選項

```bash
# 使用 GPU（推薦，速度快 10 倍）
poetry run python tools/scripts/process_single_exam.py --question ... --answer ...

# 不使用 GPU（無 CUDA 環境）
poetry run python tools/scripts/process_single_exam.py --question ... --answer ... --no-gpu
```

## 📊 輸出說明

### HTML 報告結構

生成的 HTML 報告包含：

1. **考卷總覽** (`index.html`)
   - 所有考卷列表
   - 快速導航連結

2. **考卷詳細報告** (`{exam_name}_embedded.html`)
   - 第一個分頁：**按題號瀏覽**
     - 完整題目與選項
     - 每個選項對應的 Top 3 法條
     - 法條內容與相似度分數
   - 第二個分頁：**按分數排序**
     - 依相似度排序的法條對應
   - 第三個分頁：**按法條瀏覽題目**
     - 從法條角度查看相關題目

### 資料夾說明

- `markdown/` - 保留 PDF 原始轉換結果，除錯時使用
- `parsed_qa/` - LLM 解析後的結構化 JSON，可直接查看題目內容
- `qa_mapped/` - 準備進行 Embedding 的格式化資料
- `embedded_results/` - 完整的對應結果（包含 Embedding 向量）
- `html_reports/` - **最重要**，直接開啟 `index.html` 查看報告

## 🌐 Web 瀏覽介面

### 啟動 Web 伺服器

除了直接開啟 HTML 檔案，你也可以啟動 Web 伺服器來瀏覽報告：

```bash
# 啟動 FastAPI Web 伺服器
poetry run python tools/scripts/web_server.py
```

伺服器啟動後：
- 🌐 訪問網址：http://localhost:8000
- 📊 API 文檔：http://localhost:8000/docs
- 🛑 停止服務：按 `Ctrl+C`

### Web 伺服器功能

1. **靜態報告瀏覽**
   - 自動載入所有 HTML 報告
   - 支援三種瀏覽模式（按年份、按法條、按高頻法條）
   - 深色模式自動適配

2. **REST API 端點**
   ```bash
   GET /api/reports     # 列出所有報告
   GET /api/stats       # 獲取統計資訊
   GET /health          # 健康檢查
   ```

3. **現代化 UI/UX**
   - 平滑滾動效果
   - 載入動畫
   - 響應式設計（支援手機、平板）
   - 自訂滾動條樣式
   - 懸停互動效果

### API 使用範例

```bash
# 列出所有報告
curl http://localhost:8000/api/reports

# 獲取統計資訊
curl http://localhost:8000/api/stats

# 健康檢查
curl http://localhost:8000/health
```

## 🐛 常見問題

### Q: GPU 加速無法使用？

A: 檢查是否安裝 CUDA，或使用 `--no-gpu` 選項。

### Q: OpenAI API 錯誤？

A: 確認 `.env` 檔案中的 `OPENAI_API_KEY` 是否正確。

### Q: 解析錯誤（LaTeX 符號）？

A: 已在 `src/parsing/llm_parser.py` 中處理，自動修正 JSON escape 問題。

### Q: 找不到法條資料？

A: 確認 `data/laws/` 目錄有對應的法條 CSV 檔案。

## 🚦 處理狀態檢查

```bash
# 檢查已處理的考卷數量
ls output/parsed_qa/*.json | wc -l

# 檢查已完成 Embedding 的數量
ls output/embedded_results/*.json | wc -l

# 檢查已生成的 HTML 報告
ls output/html_reports/*.html | wc -l
```

## 🐙 版本控制

本專案使用 Git 進行版本控制，遵循 Conventional Commits 規範。

### 提交訊息格式

```
<類型>(<範圍>): <主旨>

feat(embedding): 新增法條向量化功能
fix(pdf): 修正 PDF 解析編碼問題
docs(readme): 更新操作步驟說明
```

## 📄 授權

請參考 LICENSE 檔案。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

開發前請閱讀 [CLAUDE.md](CLAUDE.md) 了解協作規範。

---

**最後更新**：2025-10-12
**版本**：2.0.0
**維護者**：@bheadwei

## 📈 專案統計

- 支援法條：民法、土地法、不動產估價技術規則等
- 已處理考卷：16 份（400 題，1600 個選項）
- 平均準確率：> 90%
- 平均處理速度：< 3 秒/題

---

**🎯 快速開始建議**：

1. 新手：使用 `process_single_exam.py` 處理單份考卷
2. 批次：使用 `batch_process_exams.py` 處理多份考卷
3. 查看結果：開啟 `output/html_reports/index.html`
