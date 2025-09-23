# 文檔目錄 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **結構標準**：基於 CLAUDE.md 標準三分類

---

## 📚 文檔結構

本專案的文檔採用標準三分類結構，遵循 Linus Torvalds "實用主義" 原則，確保資訊清晰有序且容易查找。

```
docs/
├── README.md           # 本文件 - 文檔導航
├── api/               # API 文檔 - 程式介面說明
│   ├── models-api.md      # 資料模型 API
│   ├── core-api.md        # 核心引擎 API
│   └── llm-providers.md   # LLM 提供者 API
├── user/              # 使用者指南 - 操作說明
│   ├── quick-start.md     # 快速入門指南
│   ├── advanced-usage.md  # 進階使用指南
│   └── troubleshooting.md # 故障排除指南
└── dev/               # 開發者文件 - 開發指導
    ├── development-guide.md # 開發指南
    ├── architecture.md     # 系統架構文件
    └── code-standards.md   # 程式碼規範
```

---

## 🎯 快速導航

### 👥 我是新使用者
**目標：** 快速上手使用系統

1. **[快速入門指南](./user/quick-start.md)** - 10-15分鐘完成首次分析
2. **[故障排除指南](./user/troubleshooting.md)** - 解決常見問題
3. **[進階使用指南](./user/advanced-usage.md)** - 探索更多功能

### 🔧 我是系統整合者
**目標：** 將系統整合到現有工作流程

1. **[API 文檔](./api/)** - 了解程式介面
2. **[核心引擎 API](./api/core-api.md)** - 分析功能集成
3. **[LLM 提供者 API](./api/llm-providers.md)** - 自訂 LLM 配置

### 👨‍💻 我是開發者
**目標：** 參與系統開發或擴展功能

1. **[開發指南](./dev/development-guide.md)** - Linus 開發哲學與實踐
2. **[系統架構](./dev/architecture.md)** - 理解系統設計
3. **[程式碼規範](./dev/code-standards.md)** - 編碼標準與最佳實踐

---

## 📖 文檔索引

### API 文檔 (docs/api/)

| 文件 | 描述 | 適用對象 |
|------|------|----------|
| [models-api.md](./api/models-api.md) | 資料模型完整 API，包含所有 Pydantic 模型的使用方式 | 系統整合者、開發者 |
| [core-api.md](./api/core-api.md) | 核心分析引擎 API，LLM 驅動的智能分析功能 | 系統整合者、開發者 |
| [llm-providers.md](./api/llm-providers.md) | LLM 提供者統一介面，支援 OpenAI/Claude/Gemini | 系統整合者、進階使用者 |

### 使用者指南 (docs/user/)

| 文件 | 描述 | 預計時間 |
|------|------|----------|
| [quick-start.md](./user/quick-start.md) | 從安裝到首次分析的完整指南 | 10-15 分鐘 |
| [advanced-usage.md](./user/advanced-usage.md) | 批量處理、多 LLM 策略、性能調優 | 30-45 分鐘 |
| [troubleshooting.md](./user/troubleshooting.md) | 常見問題診斷與解決方案 | 按需查閱 |

### 開發者文件 (docs/dev/)

| 文件 | 描述 | 核心概念 |
|------|------|----------|
| [development-guide.md](./dev/development-guide.md) | Linus Torvalds 開發哲學在專案中的實踐 | 好品味、實用主義 |
| [architecture.md](./dev/architecture.md) | 系統分層架構、資料流程、設計決策 | 清晰分層、無特殊情況 |
| [code-standards.md](./dev/code-standards.md) | 編碼規範、測試標準、工具配置 | 簡潔、類型安全 |

---

## 🎨 文檔設計原則

### Linus 式文檔哲學

**1. 實用主義優先**
- 每份文檔都解決實際問題
- 提供可執行的範例程式碼
- 避免理論性的長篇大論

**2. 消除特殊情況**
- 統一的文檔格式和結構
- 一致的程式碼範例風格
- 標準化的術語和概念

**3. 簡潔明瞭**
- 直接切入主題，無冗餘內容
- 使用表格和清單組織資訊
- 提供快速參考和索引

**4. 可維護性**
- 每份文檔都有版本和更新日期
- 清晰的文檔間相互引用
- 程式碼範例與實際系統同步

---

## ⚡ 使用建議

### 按使用場景選擇文檔

**🔴 緊急情況（系統不工作）**
→ [故障排除指南](./user/troubleshooting.md) → 快速診斷表

**🟡 首次使用**
→ [快速入門指南](./user/quick-start.md) → 驗證安裝 → 第一次分析

**🟢 日常使用**
→ [進階使用指南](./user/advanced-usage.md) → 特定功能章節

**🔵 系統整合**
→ [API 文檔](./api/) → 選擇相關 API

**⚪ 開發貢獻**
→ [開發指南](./dev/development-guide.md) → [程式碼規範](./dev/code-standards.md)

### 學習路徑建議

**初學者路徑：**
```
快速入門 → 故障排除 → 進階使用 → API 概覽
```

**開發者路徑：**
```
系統架構 → 開發指南 → 程式碼規範 → API 詳細文檔
```

**系統管理員路徑：**
```
快速入門 → 進階使用 → 故障排除 → LLM 提供者配置
```

---

## 🔄 文檔維護

### 更新週期

- **使用者指南**：跟隨功能發布更新
- **API 文檔**：跟隨程式碼變更即時更新
- **開發者文件**：跟隨架構變更和最佳實踐演進

### 貢獻指南

如需改進文檔：

1. **小修正**：直接提交 Pull Request
2. **新增章節**：先開 Issue 討論結構
3. **大幅重構**：遵循現有的三分類結構

### 品質標準

每份文檔都應該：
- ✅ 有明確的目標對象
- ✅ 包含可執行的範例
- ✅ 提供實際問題的解決方案
- ✅ 遵循 Markdown 格式規範
- ✅ 包含適當的交叉引用

---

## 📚 相關資源

### 專案核心文檔
- **[CLAUDE.md](../CLAUDE.md)** - Claude Code 開發規範和哲學
- **[README.md](../README.md)** - 專案總覽和基本資訊

### 外部參考
- [Linus Torvalds on Good Taste](https://medium.com/@bartobri/applying-the-linus-tarvolds-good-taste-coding-requirement-99749f37684a)
- [OpenAI API 文檔](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/docs)

---

**記住：好的文檔就像好的程式碼一樣 - 一看就懂，一用就對。**

如有任何文檔相關問題，請至 [GitHub Issues](https://github.com/bheadwei/LegalStatuteAnalysis/issues) 提出建議。