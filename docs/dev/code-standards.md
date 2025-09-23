# 程式碼規範 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **基於**：Linus Torvalds "好品味" 程式設計原則
> **工具**：Black, isort, mypy, pytest

---

## 🎯 核心品味標準

"好品味是一種直覺，需要經驗累積。消除邊界情況永遠優於增加條件判斷。"

### 📏 基本度量標準

```python
# ✅ 好品味的函式
def calculate_confidence(similarities: List[float]) -> float:
    """計算信心度 - 單一職責，無特殊情況"""
    return sum(similarities) / len(similarities) if similarities else 0.0

# ❌ 糟糕品味的函式
def process_data_and_calculate_confidence_and_format_output(data, config, options):
    """做太多事情的函式"""
    # ... 50+ 行程式碼
    pass
```

**度量指標：**
- **函式長度**：≤ 20 行（超過就分拆）
- **縮排深度**：≤ 3 層（超過就重新設計）
- **函式參數**：≤ 5 個（太多就用物件封裝）
- **圈複雜度**：≤ 10（太複雜就簡化邏輯）

---

## 🏗️ 架構設計原則

### 1. 單一職責原則（SOLID 的 S）

```python
# ✅ 每個類別只做一件事
class QuestionAnalyzer:
    """只負責分析問題"""
    def analyze(self, question: ExamQuestion) -> AnalysisResult:
        pass

class ReportGenerator:
    """只負責產生報告"""
    def generate(self, results: List[AnalysisResult]) -> str:
        pass

# ❌ 違反單一職責
class QuestionProcessorAndReportGeneratorAndEmailSender:
    """做太多事情"""
    pass
```

### 2. 依賴反轉（SOLID 的 D）

```python
# ✅ 依賴抽象，不依賴具體實作
class AnalysisService:
    def __init__(self, llm_provider: LLMProvider):  # 依賴介面
        self.llm = llm_provider

# ❌ 直接依賴具體實作
class AnalysisService:
    def __init__(self):
        self.openai_client = OpenAI(api_key="...")  # 硬編碼依賴
```

### 3. 消除特殊情況

```python
# ✅ 統一處理，無特殊情況
def process_all_questions(questions: List[ExamQuestion]) -> List[AnalysisResult]:
    """統一處理所有類型的問題"""
    return [analyze_question(q) for q in questions]

# ❌ 充滿特殊情況
def process_questions(questions):
    results = []
    for q in questions:
        if q.type == "multiple_choice":
            if len(q.options) == 2:
                result = binary_choice_analysis(q)
            elif len(q.options) > 4:
                result = complex_choice_analysis(q)
            else:
                result = standard_choice_analysis(q)
        elif q.type == "essay":
            if len(q.content) < 100:
                result = short_essay_analysis(q)
            else:
                result = long_essay_analysis(q)
        # ... 更多特殊情況
    return results
```

---

## 🔧 程式碼格式規範

### Python 程式碼風格

**使用工具：**
```bash
# 自動格式化
black src/ tools/ --line-length 88
isort src/ tools/ --profile black

# 檢查
black src/ tools/ --check
isort src/ tools/ --check-only
```

**命名慣例：**
```python
# 變數和函式：snake_case
question_content = "..."
def analyze_question(): pass

# 類別：PascalCase
class EmbeddingMatcher: pass
class LLMProvider: pass

# 常數：SCREAMING_SNAKE_CASE
MAX_QUESTIONS = 1000
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# 私有方法：前綴底線
def _internal_helper(): pass

# 魔術方法：雙底線
def __str__(self): pass
```

### 型別注解（強制）

```python
# ✅ 清晰的型別注解
from typing import List, Optional, Dict, Any

def analyze_question(
    question: ExamQuestion,
    articles: List[LawArticle],
    config: SystemConfig
) -> Optional[AnalysisResult]:
    """分析單一問題 - 型別明確"""
    pass

# ❌ 缺少型別注解
def analyze_question(question, articles, config):
    """看不出參數和回傳值的型別"""
    pass
```

**型別檢查：**
```bash
mypy src/main/python/ --strict
```

---

## 📝 註釋與文檔

### Docstring 標準

```python
def calculate_confidence(similarities: List[float]) -> float:
    """計算相似度的信心度分數。

    使用簡單的平均值算法，符合 Linus 的"最笨但最清晰"原則。

    Args:
        similarities: 相似度分數列表，每個值應在 0.0-1.0 範圍內

    Returns:
        float: 平均信心度分數，如果輸入為空則回傳 0.0

    Raises:
        ValueError: 如果 similarities 中包含負值

    Example:
        >>> calculate_confidence([0.8, 0.9, 0.7])
        0.8
    """
    if not similarities:
        return 0.0

    if any(s < 0 for s in similarities):
        raise ValueError("Similarities must be non-negative")

    return sum(similarities) / len(similarities)
```

### 註釋原則

```python
# ✅ 解釋「為什麼」，不解釋「什麼」
# 使用平均值而非加權平均，因為我們沒有足夠資料來確定權重
confidence = sum(similarities) / len(similarities)

# ❌ 說明顯而易見的事情
# 計算總和然後除以長度
confidence = sum(similarities) / len(similarities)

# ✅ 解釋複雜的業務邏輯
# 根據 Linus 原則：如果相似度低於閾值，直接回傳 None 而非嘗試修正
if confidence < threshold:
    return None

# ❌ 重複程式碼的註釋
# 如果信心度小於閾值，回傳 None
if confidence < threshold:
    return None
```

---

## 🚨 錯誤處理規範

### 簡潔的錯誤處理

```python
# ✅ 明確的錯誤處理
class AnalysisError(Exception):
    """分析過程中的錯誤"""
    pass

def analyze_question(question: ExamQuestion) -> AnalysisResult:
    """分析問題 - 快速失敗，不隱藏錯誤"""
    if not question.content.strip():
        raise AnalysisError(f"Question {question.question_id} has empty content")

    try:
        result = llm_analyze(question.content)
    except LLMError as e:
        raise AnalysisError(f"LLM analysis failed: {e}") from e

    return result

# ❌ 複雜的錯誤恢復
def analyze_question_with_fallback(question):
    """複雜的錯誤處理邏輯"""
    try:
        return primary_analysis(question)
    except PrimaryError:
        try:
            return secondary_analysis(question)
        except SecondaryError:
            try:
                return fallback_analysis(question)
            except FallbackError:
                return default_result()  # 隱藏了真正的錯誤
```

**錯誤處理原則：**
1. **快速失敗**：不要嘗試從不可恢復的錯誤中恢復
2. **詳細記錄**：使用 logger，不使用 print
3. **保持堆疊**：使用 `raise ... from e`
4. **具體異常**：不要捕捉 `Exception`，要捕捉具體的異常類型

---

## 🧪 測試規範

### 測試結構

```python
# ✅ 清晰的測試結構
def test_calculate_confidence_with_valid_similarities():
    """測試正常情況的信心度計算"""
    # Arrange
    similarities = [0.8, 0.9, 0.7]
    expected = 0.8

    # Act
    result = calculate_confidence(similarities)

    # Assert
    assert result == expected

def test_calculate_confidence_with_empty_list():
    """測試邊界情況：空列表"""
    # Arrange
    similarities = []
    expected = 0.0

    # Act
    result = calculate_confidence(similarities)

    # Assert
    assert result == expected

def test_calculate_confidence_with_negative_values():
    """測試異常情況：負值輸入"""
    # Arrange
    similarities = [0.8, -0.1, 0.7]

    # Act & Assert
    with pytest.raises(ValueError, match="Similarities must be non-negative"):
        calculate_confidence(similarities)
```

### 測試命名慣例

```
test_[function_name]_[scenario]_[expected_result]

範例：
- test_analyze_question_with_valid_input_returns_result()
- test_analyze_question_with_empty_content_raises_error()
- test_calculate_confidence_with_mixed_values_returns_average()
```

### 測試覆蓋率

```bash
# 執行測試並檢查覆蓋率
pytest src/test/ --cov=src/main/python --cov-report=html

# 目標覆蓋率：≥ 80%
# 關鍵模組覆蓋率：≥ 90%
```

---

## 📦 模組組織規範

### 檔案結構

```python
# 每個模組的標準結構
src/main/python/models/
├── __init__.py          # 公開介面
├── law_models.py        # 法條相關模型
├── analysis_models.py   # 分析結果模型
└── config_models.py     # 配置模型

# __init__.py 範例
"""資料模型模組 - 提供類型安全的資料結構"""

from .law_models import LawArticle, ExamQuestion
from .analysis_models import AnalysisResult, ConfidenceLevel
from .config_models import SystemConfig, LLMConfig

__all__ = [
    "LawArticle",
    "ExamQuestion",
    "AnalysisResult",
    "ConfidenceLevel",
    "SystemConfig",
    "LLMConfig",
]
```

### 匯入順序

```python
# 1. 標準函式庫
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict

# 2. 第三方函式庫
import numpy as np
import pandas as pd
from pydantic import BaseModel

# 3. 專案內部模組
from src.main.python.models import LawArticle
from src.main.python.core import EmbeddingMatcher
```

---

## ⚡ 性能規範

### Linus 式性能優化

```python
# ✅ 簡單但有效的優化
def find_matching_articles(question: str, articles: List[LawArticle]) -> List[LawArticle]:
    """找出匹配的法條 - 簡單的線性搜尋"""
    # 不要過早優化：先讓它工作，再讓它快速
    return [article for article in articles if is_relevant(question, article)]

# ❌ 過早優化
def ultra_optimized_article_search(question, articles):
    """複雜的優化邏輯，但可能有 bug"""
    # 複雜的索引結構
    # 複雜的快取機制
    # 複雜的並行處理
    # ... 但是程式碼難以理解和維護
    pass
```

**性能原則：**
1. **正確性優先**：先讓程式碼正確，再考慮性能
2. **實測為準**：用 profiler 找出真正的瓶頸
3. **簡單優化**：優先使用成熟的函式庫
4. **避免微優化**：專注於算法級別的改進

### 記憶體使用

```python
# ✅ 使用生成器處理大資料
def process_questions_generator(questions: List[ExamQuestion]) -> Iterator[AnalysisResult]:
    """生成器模式 - 節省記憶體"""
    for question in questions:
        yield analyze_question(question)

# ❌ 一次載入所有資料到記憶體
def process_all_questions_in_memory(questions):
    """可能導致記憶體問題"""
    return [analyze_question(q) for q in questions]  # 如果 questions 很大，會有問題
```

---

## 🔍 程式碼審查檢查清單

### 提交前自檢

```bash
# 1. 格式檢查
black src/ tools/ --check
isort src/ tools/ --check-only

# 2. 型別檢查
mypy src/main/python/

# 3. 測試
pytest src/test/ -v

# 4. 覆蓋率
pytest src/test/ --cov=src/main/python --cov-fail-under=80
```

### 程式碼審查標準

**必檢項目：**

```text
【品味評分】
🟢 好品味：函式短小、邏輯清晰、無特殊情況
🟡 湊合：可工作但有改進空間
🔴 垃圾：複雜、難懂、充滿特殊情況

【技術檢查】
□ 函式長度 ≤ 20 行
□ 縮排深度 ≤ 3 層
□ 參數個數 ≤ 5 個
□ 有完整的型別注解
□ 有適當的 docstring
□ 測試覆蓋關鍵邏輯

【架構檢查】
□ 符合單一職責原則
□ 無循環依賴
□ 錯誤處理適當
□ 無重複程式碼
□ 介面設計清晰
```

---

## 📚 工具配置

### pyproject.toml 配置

```toml
[tool.black]
line-length = 88
target-version = ['py312']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src", "tools"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[tool.pytest.ini_options]
testpaths = ["src/test"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/main/python",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

### Pre-commit 設定

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black
        language_version: python3.12

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: ["--profile", "black"]

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [pydantic, types-requests]
```

---

## 🎯 總結：品味指導原則

**記住 Linus 的話：**

> "有時你可以從不同角度看問題，重寫它讓特殊情況消失，變成正常情況。這就是好品味。"

**具體到程式碼：**
1. **消除特殊情況** - 如果你的程式碼有很多 `if-elif-else`，考慮重新設計
2. **單一職責** - 如果函式名稱有「和」，可能做太多事情了
3. **簡潔明瞭** - 如果需要長篇註釋解釋，程式碼本身可能有問題
4. **實用主義** - 如果優化讓程式碼變複雜，先確保真的需要優化

**最終目標：寫出一看就懂、一改就對、一測就過的程式碼。**