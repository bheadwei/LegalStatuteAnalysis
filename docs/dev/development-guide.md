# 開發指南 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **基於**：CLAUDE.md 中的 Linus Torvalds 開發哲學
> **狀態**：活躍

---

## 🎯 核心開發哲學

本專案遵循 Linux 內核創始人 Linus Torvalds 的開發哲學，強調實用主義、簡潔性和技術卓越。

### 📚 Linus 的四大原則

**1. "好品味"(Good Taste) - 第一準則**
```python
# ❌ 糟糕的品味：特殊情況處理
def delete_node(head, target):
    if head.data == target:  # 特殊情況：刪除頭節點
        return head.next
    current = head
    while current.next:
        if current.next.data == target:
            current.next = current.next.next
            break
        current = current.next
    return head

# ✅ 好品味：消除特殊情況
def delete_node(head_ref, target):
    indirect = head_ref
    while indirect and indirect.data != target:
        indirect = indirect.next
    if indirect:
        indirect = indirect.next
```

**2. "Never break userspace" - 鐵律**
- 任何導致現有 API 崩潰的改動都是 bug
- 向後相容性是神聖不可侵犯的
- 新功能必須通過擴展實現，而非破壞

**3. 實用主義 - 信仰**
- 解決實際問題，而不是假想的威脅
- 程式碼要為現實服務，不是為論文服務
- 拒絕過度設計和理論完美

**4. 簡潔執念 - 標準**
- 如果需要超過 3 層縮排，重新設計它
- 函式必須短小精悍，只做一件事並做好
- 複雜性是萬惡之源

---

## 🏗️ 專案架構概覽

### 核心設計原則

```
src/main/python/
├── core/           # 核心 LLM 分析引擎
├── models/         # Pydantic 資料模型
├── services/       # 業務邏輯服務層
├── api/           # 外部介面
└── utils/         # 工具函式
```

**資料流向（Linus 式分析）：**
1. **資料擁有權明確**：每個模組都有明確的資料責任
2. **單向依賴**：避免循環依賴的複雜性
3. **最小介面**：模組間通過最少的接口通信

---

## 🔧 開發工作流程

### 強制性任務前檢查

在開始任何程式碼修改前，**必須**執行以下檢查：

```bash
# 1. 預防技術債務 - 先搜尋
grep -r "class.*Matcher" src/  # 尋找現有實作
grep -r "def analyze" src/     # 尋找相似功能

# 2. 理解資料結構
head -50 src/main/python/models/law_models.py

# 3. 檢查依賴關係
python -c "import src.main.python.models.law_models; print('✅ 模型載入成功')"
```

### Linus 式問題解決流程

每當遇到技術問題，按以下 5 層思考：

**第一層：資料結構分析**
```text
"Bad programmers worry about the code. Good programmers worry about data structures."

關鍵問題：
- 核心資料是什麼？它們的關係如何？
- 資料流向哪裡？誰擁有它？誰修改它？
- 有沒有不必要的資料複製或轉換？
```

**第二層：特殊情況識別**
```text
"好程式碼沒有特殊情況"

檢查清單：
- 找出所有 if/else 分支
- 哪些是真正的業務邏輯？哪些是糟糕設計的補丁？
- 能否重新設計資料結構來消除這些分支？
```

**第三層：複雜度審查**
```text
"如果實作需要超過3層縮排，重新設計它"

評估標準：
- 這個功能的本質是什麼？（一句話說清）
- 當前方案用了多少概念來解決？
- 能否減少到一半？再一半？
```

**第四層：破壞性分析**
```text
"Never break userspace"

風險評估：
- 列出所有可能受影響的現有功能
- 哪些依賴會被破壞？
- 如何在不破壞任何東西的前提下改進？
```

**第五層：實用性驗證**
```text
"Theory and practice sometimes clash. Theory loses. Every single time."

現實檢驗：
- 這個問題在生產環境真實存在嗎？
- 有多少使用者真正遇到這個問題？
- 解決方案的複雜度是否與問題的嚴重性匹配？
```

---

## 📝 程式碼品味標準

### ✅ 好品味的例子

```python
# 好品味：清晰的資料模型
@dataclass
class QuestionAnalysis:
    question_id: str
    confidence: float
    primary_articles: List[str]
    reasoning: str

# 好品味：單一職責函式
def calculate_confidence(similarities: List[float]) -> float:
    """計算信心度 - 只做這一件事"""
    return sum(similarities) / len(similarities) if similarities else 0.0

# 好品味：消除特殊情況
def process_questions(questions: List[Question]) -> List[Result]:
    """處理所有問題，無特殊情況"""
    return [analyze_single_question(q) for q in questions]
```

### ❌ 糟糕品味的例子

```python
# 糟糕品味：複雜的條件判斷
def process_question(q):
    if q.type == "multiple_choice":
        if q.has_answers:
            if len(q.options) > 2:
                return complex_analysis(q)
            else:
                return simple_analysis(q)
        else:
            return no_answer_analysis(q)
    elif q.type == "essay":
        # 更多嵌套條件...
        pass

# 糟糕品味：做太多事情的函式
def mega_function(data, config, options, flags, mode):
    # 處理資料
    # 驗證配置
    # 分析選項
    # 設置旗標
    # 切換模式
    # 產生報告
    # 發送通知
    # ... 200 行程式碼
```

---

## 🚨 技術債務預防

### 強制搜尋流程

在建立任何新檔案前：

```bash
# 1. 搜尋現有功能
grep -r "embedding.*match" src/main/python/
grep -r "class.*Analysis" src/main/python/

# 2. 分析現有架構
find src/main/python/ -name "*.py" -exec basename {} \; | sort

# 3. 決策樹
# 可以擴展現有的嗎？ → 做就對了
# 必須建立新的嗎？ → 記錄原因
```

### 禁止模式

```python
# ❌ 絕對禁止：重複實作
class EmbeddingMatcher:     # 已存在
    pass

class EmbeddingMatcherV2:   # 禁止！
    pass

class ImprovedEmbeddingMatcher:  # 禁止！
    pass

# ✅ 正確做法：擴展現有
class EmbeddingMatcher:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def analyze_with_gemini(self):  # 新增方法
        pass
```

---

## 🛠️ 開發環境設定

### 必要工具

```bash
# 安裝依賴
poetry install --with dev

# 代碼品質檢查
black src/ tools/ --check
isort src/ tools/ --check-only
mypy src/main/python/

# 測試
pytest src/test/ -v
```

### Git 工作流程

```bash
# 每完成一個功能後立即提交
git add .
git commit -m "feat(core): add confidence calculation logic

Implement Linus-style simple algorithm:
- Single responsibility function
- No special cases
- Clear data flow

🤖 Generated with Claude Code"

# 自動推送（已設定 post-commit hook）
# git push origin main
```

---

## 🎯 決策輸出模式

每個技術決策必須包含：

```text
【核心判斷】
✅ 值得做：解決實際問題，符合使用者需求
❌ 不值得做：過度設計，解決不存在的問題

【關鍵洞察】
- 資料結構：使用 Pydantic 模型確保類型安全
- 複雜度：單一函式，無嵌套條件
- 風險點：確保 API 向後相容

【Linus 式方案】
1. 第一步永遠是簡化資料結構
2. 消除所有特殊情況
3. 用最笨但最清晰的方式實作
4. 確保零破壞性
```

---

## 🔍 程式碼審查標準

### 三層判斷

```text
【品味評分】
🟢 好品味：清晰、簡潔、無特殊情況
🟡 湊合：可工作但有改進空間
🔴 垃圾：複雜、難懂、充滿特殊情況

【致命問題】
- 超過 3 層縮排
- 函式做超過一件事
- 存在不必要的特殊情況處理

【改進方向】
"把這個特殊情況消除掉"
"這10行可以變成3行"
"資料結構錯了，應該是..."
```

---

## 📚 延伸閱讀

- [CLAUDE.md](../../CLAUDE.md) - 完整的開發規範
- [API 文檔](../api/) - 模組介面說明
- [使用者指南](../user/) - 功能使用方式
- [Linus Torvalds on Good Taste](https://medium.com/@bartobri/applying-the-linus-tarvolds-good-taste-coding-requirement-99749f37684a)

---

**記住：「好品味是一種直覺，需要經驗累積。消除邊界情況永遠優於增加條件判斷。」**