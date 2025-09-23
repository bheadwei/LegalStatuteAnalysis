# 進階使用指南 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **適用對象**：有經驗的使用者、開發者
> **前置條件**：已完成[快速入門指南](./quick-start.md)

---

## 🎯 概覽

本指南涵蓋 LegalStatuteAnalysis_V1 的進階功能，包括自訂配置、批量處理優化、多 LLM 策略、性能調優和擴展功能。遵循 Linus "實用主義" 原則，專注於解決實際的複雜需求。

---

## ⚙️ 進階配置

### 系統配置深度自訂

**配置檔案位置：** `src/main/resources/config/law_config.json`

```json
{
  "version": "3.0",
  "description": "法規與考題解析設定檔 - LLM 驅動版本",

  "law_definitions": {
    "不動產經紀業管理條例.md": {
      "law_code": "REA-ACT",
      "law_name": "不動產經紀業管理條例",
      "revision_date_roc": "民國 110 年 01 月 27 日",
      "category": "不動產經紀",
      "authority": "內政部",
      "priority": 1,                    // 新增：法條優先級
      "enable_fuzzy_match": true        // 新增：啟用模糊匹配
    }
  },

  "exam_sets": {
    "custom_exam_2024": {               // 自訂考試集
      "name": "2024年自訂法規考試",
      "year": 2024,
      "question_file": "data/custom_questions.json",
      "parser_type": "llm",
      "batch_size": 10,                 // 新增：批次處理大小
      "confidence_threshold": 0.7       // 新增：信心度閾值
    }
  },

  "llm_config": {
    "default_provider": "openai",
    "fallback_provider": "simulation",
    "timeout_seconds": 30,              // 新增：超時設定
    "max_concurrent": 5,                // 新增：最大並發數
    "retry_attempts": 3,                // 新增：重試次數

    "providers": {
      "openai": {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "max_tokens": 4000,
        "api_key_env": "OPENAI_API_KEY",
        "rate_limit_rpm": 500,          // 新增：速率限制
        "cost_per_1k_tokens": 0.00015   // 新增：成本追蹤
      },

      "custom_local": {                 // 新增：自訂本地模型
        "model": "local-llama-7b",
        "base_url": "http://localhost:8080",
        "temperature": 0.1,
        "max_tokens": 2000,
        "custom_headers": {
          "X-Custom-Auth": "your-token"
        }
      }
    }
  },

  "analysis_settings": {                // 新增：分析設定區塊
    "enable_detailed_reasoning": true,
    "include_confidence_breakdown": true,
    "save_raw_responses": false,
    "enable_parallel_processing": true
  }
}
```

### 環境變數進階配置

**建立 `.env.production` 文件：**
```env
# 生產環境配置
OPENAI_API_KEY=prod_openai_key
ANTHROPIC_API_KEY=prod_claude_key
GEMINI_API_KEY=prod_gemini_key

# 性能調優
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=60
RETRY_DELAY=2

# 日誌設定
LOG_LEVEL=INFO
LOG_FILE=logs/production.log

# 快取設定
ENABLE_CACHE=true
CACHE_TTL=3600
CACHE_DIR=tmp/cache

# 成本控制
MONTHLY_TOKEN_LIMIT=1000000
COST_ALERT_THRESHOLD=50.00
```

**載入特定環境配置：**
```bash
# 載入生產環境配置
export ENV=production
python tools/scripts/run_core_embedding.py --env production
```

---

## 🚀 批量處理優化

### 大規模分析策略

**1. 智能批次處理**

```python
# tools/scripts/advanced_batch_analysis.py
import asyncio
import time
from typing import List, Optional
from src.main.python.models import ExamQuestion, SystemConfig
from src.main.python.core import EmbeddingMatcher

class AdvancedBatchProcessor:
    """
    進階批量處理器 - Linus 式實用主義

    特色：
    - 動態批次大小調整
    - 智能錯誤恢復
    - 進度追蹤和統計
    - 成本控制
    """

    def __init__(self, config: SystemConfig):
        self.config = config
        self.matcher = EmbeddingMatcher(config)
        self.stats = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "total_cost": 0.0,
            "start_time": None
        }

    async def process_large_dataset(self,
                                   questions: List[ExamQuestion],
                                   initial_batch_size: int = 5,
                                   max_batch_size: int = 20) -> List[AnalysisResult]:
        """智能批量處理大型資料集"""

        self.stats["start_time"] = time.time()
        results = []
        batch_size = initial_batch_size

        # 初始化 LLM
        await self.matcher.initialize_llm(self.config.llm_config["default_provider"])

        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]

            # 處理批次
            batch_start_time = time.time()
            batch_results = await self._process_batch(batch)
            batch_duration = time.time() - batch_start_time

            # 動態調整批次大小
            batch_size = self._adjust_batch_size(
                batch_size, batch_duration, len(batch_results), len(batch)
            )
            batch_size = min(batch_size, max_batch_size)

            results.extend(batch_results)
            self._update_stats(batch_results)

            # 進度報告
            progress = (i + len(batch)) / len(questions) * 100
            self._print_progress(progress, batch_duration, batch_size)

            # 成本控制檢查
            if self._check_cost_limit():
                print("⚠️ 達到成本限制，停止處理")
                break

            # 適當的延遲避免速率限制
            if i + batch_size < len(questions):
                await asyncio.sleep(self._calculate_delay(batch_duration))

        return results

    def _adjust_batch_size(self, current_size: int, duration: float,
                          successful: int, total: int) -> int:
        """根據性能動態調整批次大小"""
        success_rate = successful / total if total > 0 else 0
        avg_time_per_item = duration / total if total > 0 else float('inf')

        # 如果成功率高且處理快速，增加批次大小
        if success_rate > 0.9 and avg_time_per_item < 2.0:
            return min(current_size + 2, 20)

        # 如果成功率低或處理慢，減少批次大小
        elif success_rate < 0.7 or avg_time_per_item > 5.0:
            return max(current_size - 1, 1)

        return current_size
```

**使用範例：**
```bash
# 大規模批量分析
python tools/scripts/advanced_batch_analysis.py \
    --input data/large_exam_set.json \
    --provider openai \
    --initial-batch-size 5 \
    --max-batch-size 20 \
    --cost-limit 10.0
```

### 分散式處理

**2. 多進程並行處理**

```python
# tools/scripts/distributed_analysis.py
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import json

def process_chunk(chunk_data):
    """處理資料塊的工作函式"""
    questions, config_path, provider = chunk_data

    # 在每個進程中初始化
    config = SystemConfig.load_from_file(config_path)
    matcher = EmbeddingMatcher(config)

    # 處理這個塊
    results = []
    for question in questions:
        result = asyncio.run(matcher.analyze_question(question))
        if result:
            results.append(result)

    return results

def distributed_analysis(questions: List[ExamQuestion],
                        num_processes: int = None) -> List[AnalysisResult]:
    """分散式分析處理"""

    if num_processes is None:
        num_processes = min(mp.cpu_count(), 4)  # 限制最大進程數

    # 分割資料
    chunk_size = len(questions) // num_processes
    chunks = [questions[i:i + chunk_size]
              for i in range(0, len(questions), chunk_size)]

    # 準備每個塊的資料
    chunk_data = [(chunk, "config/law_config.json", "openai")
                  for chunk in chunks]

    # 並行處理
    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        chunk_results = list(executor.map(process_chunk, chunk_data))

    # 合併結果
    all_results = []
    for results in chunk_results:
        all_results.extend(results)

    return all_results
```

---

## 🤖 多 LLM 策略

### 智能提供者選擇

**3. 自適應 LLM 路由**

```python
class AdaptiveLLMRouter:
    """
    自適應 LLM 路由器 - 根據問題特徵選擇最佳提供者

    策略：
    - 簡單問題 → 快速便宜的模型
    - 複雜問題 → 高品質模型
    - 失敗自動降級
    """

    def __init__(self, config: SystemConfig):
        self.config = config
        self.providers = {}
        self.performance_history = {}

        # 初始化所有可用提供者
        for provider_name in ["openai", "claude", "gemini", "simulation"]:
            try:
                provider_config = config.get_llm_config(provider_name)
                self.providers[provider_name] = LLMProviderFactory.create_provider(provider_config)
            except Exception as e:
                logger.warning(f"無法初始化提供者 {provider_name}: {e}")

    async def analyze_with_best_provider(self, question: ExamQuestion) -> Optional[AnalysisResult]:
        """使用最佳提供者分析問題"""

        # 分析問題複雜度
        complexity = self._analyze_question_complexity(question)

        # 根據複雜度選擇提供者策略
        if complexity < 0.3:
            provider_priority = ["gemini", "openai", "claude", "simulation"]
        elif complexity < 0.7:
            provider_priority = ["openai", "claude", "gemini", "simulation"]
        else:
            provider_priority = ["claude", "openai", "gemini", "simulation"]

        # 嘗試提供者
        for provider_name in provider_priority:
            if provider_name not in self.providers:
                continue

            try:
                provider = self.providers[provider_name]
                if not provider.is_available:
                    continue

                result = await provider.analyze(self._build_prompt(question))

                # 記錄成功
                self._record_success(provider_name, question, result)
                return self._parse_result(result)

            except Exception as e:
                logger.warning(f"提供者 {provider_name} 失敗: {e}")
                self._record_failure(provider_name, question, e)
                continue

        return None

    def _analyze_question_complexity(self, question: ExamQuestion) -> float:
        """分析問題複雜度（0.0-1.0）"""
        complexity_score = 0.0

        # 基於內容長度
        content_length = len(question.content)
        complexity_score += min(content_length / 500, 0.3)

        # 基於選項數量
        if question.options:
            complexity_score += min(len(question.options) / 6, 0.2)

        # 基於問題類型
        if question.question_type == QuestionType.ESSAY:
            complexity_score += 0.4
        elif question.question_type == QuestionType.MULTIPLE_CHOICE:
            complexity_score += 0.2

        # 基於關鍵詞複雜度
        complex_keywords = ["但書", "例外", "得", "應", "不得", "除"]
        keyword_count = sum(1 for keyword in complex_keywords
                          if keyword in question.content)
        complexity_score += min(keyword_count / 10, 0.1)

        return min(complexity_score, 1.0)
```

### LLM 投票機制

**4. 多模型共識決策**

```python
class EnsembleLLMAnalyzer:
    """
    集成 LLM 分析器 - 多個模型投票決定最終結果

    原理：
    - 多個 LLM 獨立分析同一問題
    - 綜合所有結果產生最終答案
    - 提供信心度加權
    """

    def __init__(self, providers: List[LLMProvider]):
        self.providers = providers

    async def ensemble_analyze(self, question: ExamQuestion) -> Optional[AnalysisResult]:
        """集成分析 - 多模型投票"""

        # 並行調用所有提供者
        tasks = [provider.analyze(self._build_prompt(question))
                for provider in self.providers if provider.is_available]

        if not tasks:
            return None

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 解析所有有效回應
        valid_results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.warning(f"提供者 {i} 失敗: {response}")
                continue

            try:
                result = self._parse_response(response)
                if result:
                    valid_results.append(result)
            except Exception as e:
                logger.warning(f"回應解析失敗: {e}")

        if not valid_results:
            return None

        # 投票決定最終結果
        return self._vote_on_results(valid_results)

    def _vote_on_results(self, results: List[Dict]) -> AnalysisResult:
        """對多個結果進行投票"""

        # 收集所有匹配的法條
        all_articles = []
        article_votes = {}
        confidence_scores = []

        for result in results:
            confidence_scores.append(result.get('confidence', 0.0))

            for article in result.get('matched_articles', []):
                all_articles.append(article)
                article_votes[article] = article_votes.get(article, 0) + 1

        # 根據投票數排序法條
        sorted_articles = sorted(article_votes.items(),
                               key=lambda x: x[1], reverse=True)

        # 計算綜合信心度
        avg_confidence = sum(confidence_scores) / len(confidence_scores)

        # 信心度加權：如果多個模型都給出高信心度，提升最終信心度
        confidence_boost = min(len(results) * 0.1, 0.3)
        final_confidence = min(avg_confidence + confidence_boost, 1.0)

        return AnalysisResult(
            question_id=question.question_id,
            confidence=final_confidence,
            confidence_level=ConfidenceLevel.from_score(final_confidence),
            matched_articles=[article for article, _ in sorted_articles],
            primary_article=sorted_articles[0][0] if sorted_articles else None,
            reasoning=f"集成分析結果：{len(results)} 個模型投票，平均信心度 {avg_confidence:.2f}"
        )
```

**使用範例：**
```python
# 集成分析
providers = [
    LLMProviderFactory.create_provider(config.get_llm_config("openai")),
    LLMProviderFactory.create_provider(config.get_llm_config("claude")),
    LLMProviderFactory.create_provider(config.get_llm_config("gemini"))
]

ensemble = EnsembleLLMAnalyzer(providers)
result = await ensemble.ensemble_analyze(question)
```

---

## 📊 性能調優與監控

### 詳細性能追蹤

**5. 性能監控儀表板**

```python
class PerformanceMonitor:
    """
    性能監控器 - Linus 式簡潔實用

    監控指標：
    - 響應時間統計
    - 成功率追蹤
    - 成本分析
    - 錯誤模式識別
    """

    def __init__(self):
        self.metrics = {
            "requests": [],
            "errors": [],
            "costs": [],
            "start_time": time.time()
        }

    def record_request(self, provider: str, duration: float,
                      success: bool, tokens: int = 0, cost: float = 0.0):
        """記錄請求指標"""
        self.metrics["requests"].append({
            "timestamp": time.time(),
            "provider": provider,
            "duration": duration,
            "success": success,
            "tokens": tokens,
            "cost": cost
        })

        if cost > 0:
            self.metrics["costs"].append(cost)

    def generate_report(self) -> Dict[str, Any]:
        """產生性能報告"""
        requests = self.metrics["requests"]
        if not requests:
            return {"error": "無性能資料"}

        # 基本統計
        total_requests = len(requests)
        successful_requests = sum(1 for r in requests if r["success"])
        success_rate = successful_requests / total_requests

        # 響應時間統計
        durations = [r["duration"] for r in requests]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        # 成本統計
        total_cost = sum(self.metrics["costs"])
        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0

        # 提供者統計
        provider_stats = {}
        for request in requests:
            provider = request["provider"]
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "requests": 0,
                    "successes": 0,
                    "total_duration": 0
                }

            provider_stats[provider]["requests"] += 1
            if request["success"]:
                provider_stats[provider]["successes"] += 1
            provider_stats[provider]["total_duration"] += request["duration"]

        # 計算每個提供者的平均性能
        for provider, stats in provider_stats.items():
            stats["success_rate"] = stats["successes"] / stats["requests"]
            stats["avg_duration"] = stats["total_duration"] / stats["requests"]

        return {
            "summary": {
                "total_requests": total_requests,
                "success_rate": success_rate,
                "avg_response_time": avg_duration,
                "max_response_time": max_duration,
                "min_response_time": min_duration,
                "total_cost": total_cost,
                "avg_cost_per_request": avg_cost_per_request
            },
            "provider_breakdown": provider_stats,
            "uptime": time.time() - self.metrics["start_time"]
        }
```

### 快取機制

**6. 智能結果快取**

```python
import hashlib
import pickle
import os

class AnalysisCache:
    """
    分析結果快取 - 避免重複計算相同問題

    策略：
    - 基於問題內容的 hash 快取
    - LRU 淘汰策略
    - 可配置的過期時間
    """

    def __init__(self, cache_dir: str = "tmp/cache", max_size: int = 1000):
        self.cache_dir = cache_dir
        self.max_size = max_size
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, question: ExamQuestion, provider: str) -> str:
        """產生快取鍵值"""
        content = f"{question.content}_{provider}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, question: ExamQuestion, provider: str) -> Optional[AnalysisResult]:
        """從快取取得結果"""
        cache_key = self._get_cache_key(question, provider)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")

        if not os.path.exists(cache_file):
            return None

        # 檢查過期時間（24小時）
        if time.time() - os.path.getmtime(cache_file) > 86400:
            os.remove(cache_file)
            return None

        try:
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return None

    def set(self, question: ExamQuestion, provider: str, result: AnalysisResult):
        """儲存結果到快取"""
        cache_key = self._get_cache_key(question, provider)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.cache")

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            logger.warning(f"快取儲存失敗: {e}")

    def clear_expired(self):
        """清理過期快取"""
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            if time.time() - os.path.getmtime(filepath) > 86400:
                os.remove(filepath)
```

---

## 🔧 自訂擴展

### 自訂 LLM 提供者

**7. 建立自訂提供者**

```python
class CustomLocalProvider(LLMProvider):
    """
    自訂本地 LLM 提供者範例

    適用場景：
    - 本地部署的模型（Ollama, LocalAI 等）
    - 自建的 API 服務
    - 特殊的模型調用邏輯
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.base_url = config.base_url or "http://localhost:11434"
        self.model = config.model

    async def analyze(self, prompt: str) -> str:
        """調用本地 LLM API"""
        import aiohttp

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "top_p": 0.9,
                "max_tokens": self.config.max_tokens
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status != 200:
                    raise LLMProviderError(f"本地 API 錯誤: {response.status}")

                result = await response.json()
                return result.get("response", "")

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "custom_local",
            "model": self.model,
            "base_url": self.base_url,
            "version": "1.0"
        }

    @property
    def is_available(self) -> bool:
        """檢查本地服務是否可用"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            return response.status_code == 200
        except:
            return False

# 註冊自訂提供者
LLMProviderFactory.register_provider(
    LLMProviderEnum.LOCAL,
    CustomLocalProvider
)
```

### 自訂分析邏輯

**8. 擴展分析流程**

```python
class CustomAnalysisProcessor:
    """
    自訂分析處理器 - 擴展核心分析邏輯

    用途：
    - 添加預處理步驟
    - 實現自訂匹配算法
    - 整合外部資料源
    """

    def __init__(self, matcher: EmbeddingMatcher):
        self.matcher = matcher
        self.external_db = self._init_external_db()

    async def enhanced_analyze(self, question: ExamQuestion) -> Optional[AnalysisResult]:
        """增強分析流程"""

        # 1. 預處理問題
        processed_question = self._preprocess_question(question)

        # 2. 檢查外部資料庫
        external_hints = await self._query_external_db(processed_question)

        # 3. 執行核心分析
        core_result = await self.matcher.analyze_question(processed_question)

        if not core_result:
            return None

        # 4. 整合外部提示
        enhanced_result = self._integrate_external_hints(core_result, external_hints)

        # 5. 後處理結果
        final_result = self._postprocess_result(enhanced_result)

        return final_result

    def _preprocess_question(self, question: ExamQuestion) -> ExamQuestion:
        """預處理問題 - 清理和標準化"""
        # 移除多餘空白
        cleaned_content = ' '.join(question.content.split())

        # 標準化術語
        standardized_content = self._standardize_legal_terms(cleaned_content)

        return ExamQuestion(
            question_id=question.question_id,
            content=standardized_content,
            question_type=question.question_type,
            options=question.options
        )

    def _standardize_legal_terms(self, content: str) -> str:
        """標準化法律術語"""
        term_mapping = {
            "不動產仲介": "不動產經紀",
            "房仲": "不動產經紀",
            "地政士": "不動產估價師"
        }

        for old_term, new_term in term_mapping.items():
            content = content.replace(old_term, new_term)

        return content
```

---

## 📈 成本控制與優化

### 智能成本管理

**9. 成本追蹤與控制**

```python
class CostController:
    """
    成本控制器 - 智能管理 LLM 使用成本

    功能：
    - 實時成本追蹤
    - 預算警報
    - 自動降級策略
    """

    def __init__(self, monthly_budget: float = 100.0):
        self.monthly_budget = monthly_budget
        self.current_month_cost = 0.0
        self.cost_history = []

        # 提供者成本率（每1K tokens）
        self.cost_rates = {
            "openai": {"gpt-4o-mini": 0.00015, "gpt-4o": 0.005},
            "claude": {"haiku": 0.00025, "sonnet": 0.003, "opus": 0.015},
            "gemini": {"flash": 0.000075, "pro": 0.0005}
        }

    async def controlled_analyze(self, matcher: EmbeddingMatcher,
                               question: ExamQuestion) -> Optional[AnalysisResult]:
        """成本控制的分析"""

        # 檢查預算
        if self.current_month_cost >= self.monthly_budget:
            logger.warning("已達月預算上限，切換到免費模式")
            await matcher.initialize_llm("simulation")

        # 預估成本
        estimated_cost = self._estimate_cost(question, matcher.current_provider)

        if self.current_month_cost + estimated_cost > self.monthly_budget * 0.9:
            logger.warning("接近預算上限，切換到低成本提供者")
            await matcher.initialize_llm("gemini")  # 切換到較便宜的選項

        # 執行分析
        start_time = time.time()
        result = await matcher.analyze_question(question)
        duration = time.time() - start_time

        # 記錄實際成本
        if result:
            actual_cost = self._calculate_actual_cost(question, result, matcher.current_provider)
            self._record_cost(actual_cost, duration)

        return result

    def _estimate_cost(self, question: ExamQuestion, provider: str) -> float:
        """估算分析成本"""
        # 簡化的 token 估算
        estimated_tokens = len(question.content.split()) * 2  # 粗略估算

        if provider in self.cost_rates:
            provider_rates = self.cost_rates[provider]
            model_rate = list(provider_rates.values())[0]  # 使用第一個模型的費率
            return estimated_tokens * model_rate / 1000

        return 0.0  # 免費提供者

    def get_cost_summary(self) -> Dict[str, Any]:
        """取得成本摘要"""
        return {
            "monthly_budget": self.monthly_budget,
            "current_month_cost": self.current_month_cost,
            "remaining_budget": self.monthly_budget - self.current_month_cost,
            "budget_utilization": self.current_month_cost / self.monthly_budget,
            "total_requests": len(self.cost_history),
            "avg_cost_per_request": (
                sum(h["cost"] for h in self.cost_history) / len(self.cost_history)
                if self.cost_history else 0
            )
        }
```

---

## 🔍 進階查詢與分析

### 複雜查詢支援

**10. 自訂查詢介面**

```python
class AdvancedQueryInterface:
    """
    進階查詢介面 - 支援複雜的分析需求

    功能：
    - 條件篩選
    - 批量比較
    - 趨勢分析
    - 自訂報告
    """

    def __init__(self, results_db: str = "results/analysis_results.db"):
        import sqlite3
        self.conn = sqlite3.connect(results_db)
        self._init_database()

    def _init_database(self):
        """初始化結果資料庫"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY,
                question_id TEXT,
                question_content TEXT,
                confidence REAL,
                matched_articles TEXT,
                primary_article TEXT,
                llm_provider TEXT,
                analysis_date DATE,
                processing_time REAL
            )
        """)
        self.conn.commit()

    def store_result(self, result: AnalysisResult, question: ExamQuestion):
        """儲存分析結果"""
        self.conn.execute("""
            INSERT INTO analysis_results
            (question_id, question_content, confidence, matched_articles,
             primary_article, llm_provider, analysis_date, processing_time)
            VALUES (?, ?, ?, ?, ?, ?, DATE('now'), ?)
        """, (
            result.question_id,
            question.content,
            result.confidence,
            ','.join(result.matched_articles),
            result.primary_article,
            result.llm_provider.value if result.llm_provider else None,
            result.processing_time
        ))
        self.conn.commit()

    def query_by_confidence(self, min_confidence: float = 0.7) -> List[Dict]:
        """查詢高信心度結果"""
        cursor = self.conn.execute("""
            SELECT * FROM analysis_results
            WHERE confidence >= ?
            ORDER BY confidence DESC
        """, (min_confidence,))

        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def analyze_performance_trends(self) -> Dict[str, Any]:
        """分析性能趨勢"""
        # 按日期統計
        cursor = self.conn.execute("""
            SELECT
                analysis_date,
                COUNT(*) as total_analyses,
                AVG(confidence) as avg_confidence,
                AVG(processing_time) as avg_processing_time,
                llm_provider
            FROM analysis_results
            GROUP BY analysis_date, llm_provider
            ORDER BY analysis_date DESC
        """)

        trends = cursor.fetchall()

        # 計算整體統計
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total,
                AVG(confidence) as overall_avg_confidence,
                MIN(confidence) as min_confidence,
                MAX(confidence) as max_confidence
            FROM analysis_results
        """)

        overall_stats = cursor.fetchone()

        return {
            "daily_trends": trends,
            "overall_statistics": {
                "total_analyses": overall_stats[0],
                "average_confidence": overall_stats[1],
                "confidence_range": [overall_stats[2], overall_stats[3]]
            }
        }
```

---

## 🎯 最佳實踐總結

### 進階使用建議

**1. 生產環境部署**

```bash
# 生產環境啟動腳本
#!/bin/bash
# production_start.sh

export ENV=production
export LOG_LEVEL=INFO
export MAX_CONCURRENT_REQUESTS=10

# 清理快取
python tools/scripts/cache_cleanup.py

# 預熱系統
python tools/scripts/system_warmup.py

# 啟動主要分析
python tools/scripts/production_analysis.py \
    --config config/production.json \
    --provider openai \
    --batch-size 10 \
    --enable-monitoring \
    --cost-limit 50.0
```

**2. 監控和警報設定**

```python
# 監控腳本
def setup_monitoring():
    """設定系統監控"""

    # 性能監控
    monitor = PerformanceMonitor()

    # 成本控制
    cost_controller = CostController(monthly_budget=100.0)

    # 健康檢查
    health_checker = SystemHealthChecker()

    return monitor, cost_controller, health_checker
```

**3. 錯誤恢復策略**

```python
class RobustAnalysisSystem:
    """
    穩健的分析系統 - 具備完整的錯誤恢復能力

    特色：
    - 斷點續傳
    - 自動重試
    - 降級策略
    - 數據完整性檢查
    """

    def __init__(self):
        self.checkpoint_manager = CheckpointManager()
        self.fallback_chain = ["openai", "claude", "gemini", "simulation"]

    async def resilient_batch_process(self, questions: List[ExamQuestion]):
        """具備恢復能力的批量處理"""

        # 檢查是否有未完成的工作
        checkpoint = self.checkpoint_manager.load_checkpoint()

        if checkpoint:
            logger.info(f"從檢查點恢復，已完成 {checkpoint['completed']} 項")
            questions = questions[checkpoint['completed']:]

        results = []
        for i, question in enumerate(questions):
            try:
                result = await self._resilient_single_analysis(question)
                if result:
                    results.append(result)

                # 定期保存檢查點
                if i % 10 == 0:
                    self.checkpoint_manager.save_checkpoint({
                        'completed': checkpoint.get('completed', 0) + i,
                        'results': results
                    })

            except Exception as e:
                logger.error(f"無法恢復的錯誤: {e}")
                continue

        return results
```

---

## 📚 進一步探索

完成進階使用後，您可以：

1. **[開發指南](../dev/development-guide.md)** - 深入了解系統架構
2. **[API 文檔](../api/)** - 探索完整的 API 功能
3. **[故障排除](./troubleshooting.md)** - 解決複雜問題
4. **貢獻代碼** - 參與系統改進

**記住 Linus 的話：** "好的系統讓複雜的任務變得簡單，而不是讓簡單的任務變得複雜。"

本進階指南的所有功能都遵循這一原則，提供強大功能的同時保持使用的簡潔性。