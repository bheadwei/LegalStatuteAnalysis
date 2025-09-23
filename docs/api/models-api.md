# 資料模型 API 文檔 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **模組路徑**：`src.main.python.models`
> **狀態**：活躍

---

## 📋 概覽

資料模型模組提供類型安全的資料結構，使用 Pydantic 和 dataclass 確保資料一致性和序列化支援。遵循 Linus "好品味" 原則，所有模型都簡潔明瞭，無特殊情況處理。

---

## 🏗️ 核心模型

### LawArticle - 法條資料模型

**用途：** 表示單一法條的完整資訊

```python
from src.main.python.models import LawArticle

@dataclass
class LawArticle:
    """法條資料模型 - 簡潔的資料結構，無複雜邏輯"""
    law_code: str          # 法律代碼，如 "REA-ACT"
    law_name: str          # 法律名稱，如 "不動產經紀業管理條例"
    revision_date: str     # 修訂日期
    chapter_no: int        # 章節號碼
    chapter_title: str     # 章節標題
    article_no_main: int   # 主條號
    article_no_sub: int    # 子條號 (0 表示無子條)
    content: str           # 法條內容
    category: Optional[str] = None    # 分類
    authority: Optional[str] = None   # 主管機關
```

**屬性方法：**

```python
# 唯一識別碼
article_id: str
# 範例：REA-ACT-13 或 REA-ACT-13-1

# 顯示標籤
article_label: str
# 範例：第13條 或 第13-1條

# 完整標題
full_title: str
# 範例：不動產經紀業管理條例 第13條
```

**使用範例：**

```python
# 建立法條物件
article = LawArticle(
    law_code="REA-ACT",
    law_name="不動產經紀業管理條例",
    revision_date="民國 110 年 01 月 27 日",
    chapter_no=2,
    chapter_title="經紀業之管理",
    article_no_main=13,
    article_no_sub=0,
    content="不動產經紀業者應於營業處所明顯處揭示...",
    category="不動產經紀",
    authority="內政部"
)

# 取得屬性
print(article.article_id)    # "REA-ACT-13"
print(article.full_title)    # "不動產經紀業管理條例 第13條"

# 序列化
article_dict = article.to_dict()
```

---

### ExamQuestion - 考試題目模型

**用途：** 表示考試題目的完整資訊

```python
@dataclass
class ExamQuestion:
    """考試題目模型 - 統一處理所有題型，無特殊情況"""
    question_id: str                    # 題目唯一識別碼
    content: str                        # 題目內容
    question_type: QuestionType         # 題目類型
    options: List[str] = field(default_factory=list)  # 選項列表
    correct_answer: Optional[str] = None               # 正確答案
    explanation: Optional[str] = None                  # 解釋說明
    source_exam: Optional[str] = None                  # 來源考試
    year: Optional[int] = None                         # 考試年度
    subject: Optional[str] = None                      # 考試科目
```

**使用範例：**

```python
from src.main.python.models import ExamQuestion, QuestionType

# 選擇題
question = ExamQuestion(
    question_id="Q001",
    content="不動產經紀業者應於營業處所明顯處揭示哪些資訊？",
    question_type=QuestionType.MULTIPLE_CHOICE,
    options=["A. 營業執照", "B. 經紀人證書", "C. 收費標準", "D. 以上皆是"],
    correct_answer="D",
    source_exam="113年專門職業及技術人員高等考試",
    year=113,
    subject="不動產經紀相關法規"
)

# 序列化
question_dict = question.to_dict()
```

---

### AnalysisResult - 分析結果模型

**用途：** 儲存 LLM 分析的結果

```python
@dataclass
class AnalysisResult:
    """分析結果模型 - 清晰的結構，便於後續處理"""
    question_id: str                    # 對應的題目 ID
    confidence: float                   # 信心度 (0.0-1.0)
    confidence_level: ConfidenceLevel   # 信心度等級
    matched_articles: List[str]         # 匹配的法條 ID 列表
    primary_article: Optional[str] = None      # 主要相關法條
    reasoning: Optional[str] = None            # 分析推理過程
    processing_time: Optional[float] = None    # 處理時間(秒)
    llm_provider: Optional[LLMProvider] = None # 使用的 LLM 提供者
    raw_response: Optional[str] = None         # LLM 原始回應
```

**使用範例：**

```python
from src.main.python.models import AnalysisResult, ConfidenceLevel, LLMProvider

result = AnalysisResult(
    question_id="Q001",
    confidence=0.85,
    confidence_level=ConfidenceLevel.HIGH,
    matched_articles=["REA-ACT-13", "REA-ACT-14"],
    primary_article="REA-ACT-13",
    reasoning="題目明確詢問營業處所揭示要求，直接對應第13條規定",
    processing_time=2.3,
    llm_provider=LLMProvider.OPENAI
)
```

---

## 🔧 列舉型別 (Enums)

### QuestionType - 題目類型

```python
class QuestionType(Enum):
    """題目類型枚舉 - 支援的考題格式"""
    MULTIPLE_CHOICE = "multiple_choice"  # 選擇題
    ESSAY = "essay"                      # 問答題
    TRUE_FALSE = "true_false"            # 是非題
```

### LLMProvider - LLM 提供者

```python
class LLMProvider(Enum):
    """支援的 LLM 提供者"""
    OPENAI = "openai"           # OpenAI GPT 系列
    CLAUDE = "claude"           # Anthropic Claude
    LOCAL = "local"             # 本地模型
    SIMULATION = "simulation"   # 模擬模式(測試用)
```

### ConfidenceLevel - 信心度等級

```python
class ConfidenceLevel(Enum):
    """信心度分級 - 根據數值範圍自動判定"""
    VERY_LOW = (0.0, 0.3, "極低")    # 0.0-0.3
    LOW = (0.3, 0.5, "低")           # 0.3-0.5
    MEDIUM = (0.5, 0.7, "中等")      # 0.5-0.7
    HIGH = (0.7, 0.9, "高")          # 0.7-0.9
    VERY_HIGH = (0.9, 1.0, "極高")   # 0.9-1.0
```

**使用範例：**

```python
# 根據分數自動判定等級
level = ConfidenceLevel.from_score(0.85)  # 回傳 HIGH
print(level.label)  # "高"
```

---

## 📦 配置模型

### SystemConfig - 系統配置

**用途：** 載入和管理系統配置檔案

```python
@dataclass
class SystemConfig:
    """系統配置模型 - 統一管理所有配置"""
    version: str
    description: str
    law_definitions: Dict[str, LawDefinition]
    exam_sets: Dict[str, ExamSet]
    llm_config: Dict[str, LLMConfig]

    @classmethod
    def load_from_file(cls, config_path: str) -> 'SystemConfig':
        """從 JSON 檔案載入配置"""
        # 實現載入邏輯
        pass
```

### LLMConfig - LLM 配置

```python
@dataclass
class LLMConfig:
    """LLM 提供者配置"""
    provider: LLMProvider
    model: str
    temperature: float = 0.0
    max_tokens: int = 4000
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None
```

**使用範例：**

```python
from src.main.python.models import SystemConfig

# 載入配置
config = SystemConfig.load_from_file("src/main/resources/config/law_config.json")

# 取得 LLM 配置
openai_config = config.get_llm_config("openai")
print(openai_config.model)        # "gpt-4o-mini"
print(openai_config.temperature)  # 0.0
```

---

## 📊 資料載入器

### LawArticleLoader - 法條載入器

**用途：** 從各種格式載入法條資料

```python
class LawArticleLoader:
    """法條資料載入器 - 統一的載入介面"""

    @staticmethod
    def load_from_csv(csv_path: str) -> List[LawArticle]:
        """從 CSV 檔案載入法條"""
        pass

    @staticmethod
    def load_from_markdown(md_path: str) -> List[LawArticle]:
        """從 Markdown 檔案載入法條"""
        pass

    @staticmethod
    def load_from_json(json_path: str) -> List[LawArticle]:
        """從 JSON 檔案載入法條"""
        pass
```

### ExamQuestionLoader - 考題載入器

```python
class ExamQuestionLoader:
    """考試題目載入器"""

    @staticmethod
    def load_from_json(json_path: str) -> List[ExamQuestion]:
        """從 JSON 檔案載入考題"""
        pass

    @staticmethod
    def load_from_markdown(md_path: str) -> List[ExamQuestion]:
        """從 Markdown 檔案載入考題"""
        pass
```

**使用範例：**

```python
from src.main.python.models import LawArticleLoader, ExamQuestionLoader

# 載入法條
articles = LawArticleLoader.load_from_csv("results/law_articles.csv")
print(f"載入 {len(articles)} 條法規")

# 載入考題
questions = ExamQuestionLoader.load_from_json("results/exam_113_complete.json")
print(f"載入 {len(questions)} 道題目")
```

---

## 🔍 資料驗證與序列化

### 自動驗證

所有模型都支援自動類型驗證：

```python
# ✅ 正確的資料會自動驗證通過
question = ExamQuestion(
    question_id="Q001",
    content="題目內容",
    question_type=QuestionType.MULTIPLE_CHOICE
)

# ❌ 錯誤的資料類型會引發異常
try:
    invalid_question = ExamQuestion(
        question_id=123,  # 應該是 str
        content="題目內容",
        question_type="invalid_type"  # 應該是 QuestionType enum
    )
except (TypeError, ValueError) as e:
    print(f"資料驗證失敗: {e}")
```

### 序列化支援

所有模型都提供 JSON 序列化：

```python
# 轉換為字典
question_dict = question.to_dict()

# 轉換為 JSON 字串
import json
question_json = json.dumps(question_dict, ensure_ascii=False, indent=2)

# 從字典重建物件
restored_question = ExamQuestion.from_dict(question_dict)
```

---

## 🎯 設計原則總結

### Linus 式設計哲學體現

**1. 好品味 - 消除特殊情況**
```python
# ✅ 統一處理所有題型，無特殊情況
def process_question(question: ExamQuestion) -> AnalysisResult:
    # 無論什麼類型的題目，都使用相同的分析邏輯
    return analyze(question)

# ❌ 避免針對不同類型的特殊處理
def process_question_with_special_cases(question):
    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        # 特殊邏輯A
    elif question.question_type == QuestionType.ESSAY:
        # 特殊邏輯B
    # ...
```

**2. 簡潔性 - 資料結構驅動**
- 每個模型職責單一明確
- 屬性命名直觀易懂
- 無複雜的繼承結構

**3. 實用主義 - 解決實際問題**
- 支援實際的考試題型格式
- 整合常用的 LLM 提供者
- 提供便利的載入和序列化方法

**4. 類型安全 - 錯誤早發現**
- 完整的型別注解
- 自動資料驗證
- IDE 友好的自動完成

---

## 📚 相關文檔

- [開發指南](../dev/development-guide.md) - 整體開發原則
- [核心引擎 API](./core-api.md) - 分析引擎接口
- [使用範例](../user/quick-start.md) - 實際使用案例