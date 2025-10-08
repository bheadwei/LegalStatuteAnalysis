# LegalStatuteAnalysis - 法律文件與法條智能對應系統

## 📋 專案簡介

自動化法律文件（如考試題目、案例）與相關法條的對應系統。透過 Embedding 與 LLM 智能匹配，快速、準確地找出文本內容所對應的法條，並產出清晰的 HTML/PDF 報告。

## 🎯 核心功能

1. **PDF 解析考題** - 自動讀取並解析 PDF 格式的輸入文件
2. **法條 Embedding** - 將法律條文轉換為向量，建立語義搜索資料庫
3. **LLM 智能對應** - 利用 Embedding 和 LLM 進行智能匹配
4. **HTML 報告生成** - 結構化匹配結果，生成清晰的 HTML 報告
5. **PDF 報告下載** - 將 HTML 報告轉換為 PDF 檔案

## 📊 成功標準

- **對應準確率**：> 90%
- **處理速度**：< 5 秒/題
- **報告品質**：內容正確、格式清晰、無錯誤

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
cp src/main/resources/config/.env.example .env
# 編輯 .env 填入 OPENAI_API_KEY
```

### 3. 執行分析

```bash
python tools/scripts/run_analysis.py --input data/pdfs/exam.pdf --output output/
```

## 📁 專案結構

```
LegalStatuteAnalysis/
├── CLAUDE.md                    # Claude Code 配置（人類主導版）
├── README.md                    # 專案文件
├── requirements.txt             # Python 依賴套件
├── src/                         # 原始碼
│   ├── main/python/             # Python 程式碼
│   │   ├── core/                # 核心邏輯（Embedding, 對應引擎）
│   │   ├── models/              # 資料模型
│   │   ├── services/            # 服務層（PDF 解析、報告生成）
│   │   ├── utils/               # 工具函式
│   │   └── api/                 # API 封裝
│   └── main/resources/config/   # 配置檔
├── tools/scripts/               # 執行腳本
├── data/                        # 原始資料
├── output/                      # 輸出檔案
├── docs/                        # 文件
└── examples/                    # 使用範例
```

## 🛠️ 技術棧

- **開發語言**：Python
- **LLM Provider**：OpenAI API
- **使用模式**：CLI 命令列工具

## 📝 開發指南

請閱讀 [CLAUDE.md](CLAUDE.md) 了解完整的開發規範和協作流程。

## 🔧 配置說明

系統配置檔案位於 `src/main/resources/config/config.json`，可調整：
- LLM 模型和參數
- Embedding 設定
- 處理並發數
- 品質指標閾值

## 🐙 版本控制

本專案使用 Git 進行版本控制，遵循 Conventional Commits 規範。

## 📄 授權

請參考 LICENSE 檔案。

---

**最後更新**：2025-10-09
**版本**：1.0.0
