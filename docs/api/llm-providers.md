# LLM 提供者 API 文檔 - LegalStatuteAnalysis_V1

> **文件版本**：1.0
> **最後更新**：2025-09-23
> **模組路徑**：`src.main.python.services.llm`
> **狀態**：活躍

---

## 📋 概覽

LLM 提供者模組實現統一的多 LLM 支援，遵循 Linus "消除特殊情況" 原則，所有提供者都實現相同介面，確保切換無痛且業務邏輯不變。

---

## 🎯 統一介面設計

### LLMProvider 抽象基類

**設計理念：** 一個介面統治所有 LLM，無特殊情況

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    """
    LLM 提供者統一介面 - Linus 式設計

    原則：
    - 單一介面：所有 LLM 都實現相同方法
    - 無特殊情況：不同提供者的差異在實現內部處理
    - 簡潔明瞭：只提供必要的方法，不過度設計
    """

    @abstractmethod
    async def analyze(self, prompt: str) -> str:
        """
        核心分析方法 - 唯一需要實現的業務邏輯

        Args:
            prompt: 分析提示詞

        Returns:
            str: LLM 回應的 JSON 字串

        Raises:
            LLMProviderError: LLM 調用失敗時拋出
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        取得模型資訊

        Returns:
            Dict: 包含 provider, model, version 等資訊
        """
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """檢查提供者是否可用（API 金鑰、網路等）"""
        pass
```

---

## 🤖 具體實現

### OpenAIProvider - GPT 系列

**特色：** 支援 GPT-3.5/GPT-4 系列模型

```python
from openai import AsyncOpenAI
from src.main.python.models import LLMConfig

class OpenAIProvider(LLMProvider):
    """OpenAI GPT 系列提供者 - 實用主義實現"""

    def __init__(self, config: LLMConfig):
        """
        初始化 OpenAI 提供者

        Args:
            config: LLM 配置，包含模型、API 金鑰等資訊
        """
        self.config = config
        self.client = AsyncOpenAI(
            api_key=os.getenv(config.api_key_env),
            base_url=config.base_url
        )

    async def analyze(self, prompt: str) -> str:
        """使用 GPT 模型進行分析"""
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位專業的法規分析專家，請根據問題內容分析相關法條。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            raise LLMProviderError(f"OpenAI API 調用失敗: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """取得 OpenAI 模型資訊"""
        return {
            "provider": "openai",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "version": "1.0"
        }

    @property
    def is_available(self) -> bool:
        """檢查 OpenAI 是否可用"""
        return os.getenv(self.config.api_key_env) is not None
```

**支援的模型：**
- `gpt-4o-mini` - 成本效益最佳，推薦用於大量分析
- `gpt-4o` - 最高品質，適合複雜法條解析
- `gpt-3.5-turbo` - 快速響應，適合簡單匹配

**使用範例：**

```python
from src.main.python.models import LLMConfig, LLMProvider as LLMProviderEnum

# 配置 OpenAI
openai_config = LLMConfig(
    provider=LLMProviderEnum.OPENAI,
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=4000,
    api_key_env="OPENAI_API_KEY"
)

# 建立提供者
provider = OpenAIProvider(openai_config)

# 檢查可用性
if provider.is_available:
    response = await provider.analyze("分析這個法條問題...")
    print(response)
```

---

### ClaudeProvider - Anthropic Claude

**特色：** 支援 Claude 3 系列模型

```python
import anthropic

class ClaudeProvider(LLMProvider):
    """Anthropic Claude 提供者"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = anthropic.AsyncAnthropic(
            api_key=os.getenv(config.api_key_env)
        )

    async def analyze(self, prompt: str) -> str:
        """使用 Claude 模型進行分析"""
        try:
            response = await self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="你是一位專業的法規分析專家，請根據問題內容分析相關法條。",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            raise LLMProviderError(f"Claude API 調用失敗: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """取得 Claude 模型資訊"""
        return {
            "provider": "claude",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "version": "1.0"
        }

    @property
    def is_available(self) -> bool:
        """檢查 Claude 是否可用"""
        return os.getenv(self.config.api_key_env) is not None
```

**支援的模型：**
- `claude-3-haiku-20240307` - 最快響應，適合批量處理
- `claude-3-sonnet-20240229` - 平衡性能和品質
- `claude-3-opus-20240229` - 最高品質，適合複雜分析

---

### GeminiProvider - Google Gemini

**特色：** 支援 Google Gemini Pro 和 embedding 模型

```python
import google.generativeai as genai

class GeminiProvider(LLMProvider):
    """Google Gemini 提供者"""

    def __init__(self, config: LLMConfig):
        self.config = config
        genai.configure(api_key=os.getenv(config.api_key_env))
        self.model = genai.GenerativeModel(config.model)

    async def analyze(self, prompt: str) -> str:
        """使用 Gemini 模型進行分析"""
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )

            return response.text

        except Exception as e:
            raise LLMProviderError(f"Gemini API 調用失敗: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """取得 Gemini 模型資訊"""
        return {
            "provider": "gemini",
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "version": "1.0"
        }

    @property
    def is_available(self) -> bool:
        """檢查 Gemini 是否可用"""
        return os.getenv(self.config.api_key_env) is not None
```

**支援的模型：**
- `gemini-1.5-flash` - 快速響應，成本效益佳
- `gemini-1.5-pro` - 高品質分析，支援長文本
- `models/embedding-001` - 專用於 embedding 計算

---

### SimulationProvider - 測試模擬器

**特色：** 本地模擬，無需 API 金鑰，用於開發測試

```python
import json
import random
import asyncio

class SimulationProvider(LLMProvider):
    """
    模擬提供者 - Linus 式實用主義

    用途：
    - 開發階段測試
    - 無 API 金鑰時的後備選項
    - 性能基準測試
    - 演示和教學
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.mock_articles = [
            "REA-ACT-13", "REA-ACT-14", "REA-ACT-15",
            "REA-ACT-20", "REA-ACT-21", "REA-ACT-25"
        ]

    async def analyze(self, prompt: str) -> str:
        """產生模擬的分析結果"""

        # 模擬 API 延遲
        await asyncio.sleep(random.uniform(0.5, 2.0))

        # 分析提示詞複雜度，決定信心度
        complexity_score = self._analyze_prompt_complexity(prompt)

        # 產生模擬結果
        mock_result = {
            "confidence": min(0.95, max(0.3, complexity_score + random.uniform(-0.2, 0.2))),
            "matched_articles": random.sample(self.mock_articles, random.randint(1, 3)),
            "primary_article": random.choice(self.mock_articles),
            "reasoning": f"模擬分析結果：根據問題關鍵詞分析，識別出與{random.choice(['營業規範', '管理條例', '揭示義務', '執業規則'])}相關的法條規定。"
        }

        return json.dumps(mock_result, ensure_ascii=False)

    def _analyze_prompt_complexity(self, prompt: str) -> float:
        """分析提示詞複雜度 - 簡單的啟發式方法"""
        if len(prompt) < 50:
            return 0.4  # 短問題，低信心度
        elif len(prompt) > 200:
            return 0.8  # 長問題，高信心度
        else:
            return 0.6  # 中等問題，中等信心度

    def get_model_info(self) -> Dict[str, Any]:
        """取得模擬器資訊"""
        return {
            "provider": "simulation",
            "model": "mock-v1.0",
            "temperature": 0.0,
            "max_tokens": 4000,
            "version": "1.0",
            "description": "本地模擬器，用於開發測試"
        }

    @property
    def is_available(self) -> bool:
        """模擬器永遠可用"""
        return True
```

---

## 🔧 提供者工廠

### LLMProviderFactory - 統一建立介面

**用途：** 根據配置自動建立對應的 LLM 提供者

```python
from src.main.python.models import LLMConfig, LLMProvider as LLMProviderEnum

class LLMProviderFactory:
    """
    LLM 提供者工廠 - 消除建立提供者的特殊情況

    Linus 原則體現：
    - 統一入口：所有提供者通過同一方法建立
    - 無特殊邏輯：添加新提供者只需註冊一行
    - 快速失敗：不支援的提供者立即報錯
    """

    _PROVIDERS = {
        LLMProviderEnum.OPENAI: OpenAIProvider,
        LLMProviderEnum.CLAUDE: ClaudeProvider,
        LLMProviderEnum.GEMINI: GeminiProvider,
        LLMProviderEnum.SIMULATION: SimulationProvider,
    }

    @classmethod
    def create_provider(cls, config: LLMConfig) -> LLMProvider:
        """
        建立 LLM 提供者

        Args:
            config: LLM 配置

        Returns:
            LLMProvider: 對應的提供者實例

        Raises:
            ValueError: 不支援的提供者類型
        """
        provider_class = cls._PROVIDERS.get(config.provider)
        if not provider_class:
            supported = list(cls._PROVIDERS.keys())
            raise ValueError(f"不支援的 LLM 提供者: {config.provider}, 支援的提供者: {supported}")

        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> List[LLMProviderEnum]:
        """取得所有可用的提供者列表"""
        return list(cls._PROVIDERS.keys())

    @classmethod
    def register_provider(cls, provider_type: LLMProviderEnum, provider_class: type):
        """
        註冊新的提供者 - 擴展系統的唯一方法

        Args:
            provider_type: 提供者類型枚舉
            provider_class: 提供者實現類別
        """
        cls._PROVIDERS[provider_type] = provider_class
```

**使用範例：**

```python
from src.main.python.models import SystemConfig

# 載入配置
config = SystemConfig.load_from_file("config/law_config.json")
openai_config = config.get_llm_config("openai")

# 建立提供者
provider = LLMProviderFactory.create_provider(openai_config)

# 檢查可用性並使用
if provider.is_available:
    result = await provider.analyze("法條分析問題...")
    model_info = provider.get_model_info()
    print(f"使用模型: {model_info['model']}")
```

---

## 🛡️ 錯誤處理與重試機制

### 異常類型

```python
class LLMProviderError(Exception):
    """LLM 提供者基礎異常"""
    pass

class APIKeyError(LLMProviderError):
    """API 金鑰相關錯誤"""
    pass

class RateLimitError(LLMProviderError):
    """API 速率限制錯誤"""
    pass

class ModelNotAvailableError(LLMProviderError):
    """模型不可用錯誤"""
    pass
```

### 重試機制

```python
import asyncio
from typing import Optional

class RetryableProvider:
    """
    帶重試機制的提供者包裝器 - 簡單的指數退避

    Linus 原則：
    - 簡單重試：不做複雜的重試策略
    - 快速失敗：超過重試次數立即拋出異常
    - 實用主義：只處理常見的暫時性錯誤
    """

    def __init__(self, provider: LLMProvider, max_retries: int = 3):
        self.provider = provider
        self.max_retries = max_retries

    async def analyze_with_retry(self, prompt: str) -> str:
        """帶重試機制的分析"""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                return await self.provider.analyze(prompt)

            except RateLimitError as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt  # 指數退避：2, 4, 8 秒
                    logger.warning(f"速率限制，等待 {wait_time} 秒後重試...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break

            except (APIKeyError, ModelNotAvailableError):
                # 這些錯誤不需要重試
                raise

            except LLMProviderError as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = 1 + random.uniform(0, 1)  # 隨機等待 1-2 秒
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break

        # 所有重試都失敗
        raise LLMProviderError(f"所有重試失敗，最後錯誤: {last_error}")
```

---

## 📊 性能監控

### 提供者性能追蹤

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class ProviderMetrics:
    """提供者性能指標"""
    provider_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    total_tokens_used: Optional[int] = None
    total_cost: Optional[float] = None

class ProviderMonitor:
    """LLM 提供者性能監控"""

    def __init__(self):
        self.metrics: Dict[str, ProviderMetrics] = {}

    async def monitored_analyze(self, provider: LLMProvider, prompt: str) -> str:
        """監控包裝的分析方法"""
        provider_name = provider.get_model_info()["provider"]
        start_time = time.time()

        try:
            result = await provider.analyze(prompt)
            response_time = time.time() - start_time

            # 記錄成功
            self._record_success(provider_name, response_time)
            return result

        except Exception as e:
            response_time = time.time() - start_time

            # 記錄失敗
            self._record_failure(provider_name, response_time)
            raise

    def get_provider_metrics(self, provider_name: str) -> Optional[ProviderMetrics]:
        """取得指定提供者的性能指標"""
        return self.metrics.get(provider_name)

    def get_all_metrics(self) -> Dict[str, ProviderMetrics]:
        """取得所有提供者的性能指標"""
        return self.metrics.copy()
```

---

## 🔄 提供者切換策略

### 自動降級機制

```python
class FallbackProvider:
    """
    自動降級提供者 - Linus 式實用主義

    策略：
    1. 嘗試主要提供者
    2. 失敗時自動切換到備用提供者
    3. 記錄切換原因供後續分析
    """

    def __init__(self, primary: LLMProvider, fallback: LLMProvider):
        self.primary = primary
        self.fallback = fallback
        self.current_provider = primary
        self.fallback_count = 0

    async def analyze(self, prompt: str) -> str:
        """帶降級機制的分析"""

        # 嘗試主要提供者
        try:
            return await self.primary.analyze(prompt)
        except LLMProviderError as e:
            logger.warning(f"主要提供者失敗，切換到備用提供者: {e}")

            # 切換到備用提供者
            try:
                self.fallback_count += 1
                return await self.fallback.analyze(prompt)
            except LLMProviderError as fallback_error:
                raise LLMProviderError(f"主要和備用提供者都失敗 - 主要: {e}, 備用: {fallback_error}")

    def get_fallback_stats(self) -> Dict[str, Any]:
        """取得降級統計"""
        return {
            "fallback_count": self.fallback_count,
            "primary_provider": self.primary.get_model_info()["provider"],
            "fallback_provider": self.fallback.get_model_info()["provider"]
        }
```

---

## 🎯 最佳實踐範例

### 完整使用流程

```python
async def complete_llm_workflow_example():
    """完整的 LLM 使用流程範例"""

    # 1. 載入配置
    config = SystemConfig.load_from_file("config/law_config.json")

    # 2. 建立主要和備用提供者
    primary_config = config.get_llm_config("openai")
    fallback_config = config.get_llm_config("simulation")

    primary_provider = LLMProviderFactory.create_provider(primary_config)
    fallback_provider = LLMProviderFactory.create_provider(fallback_config)

    # 3. 建立帶重試和降級機制的提供者
    retryable_primary = RetryableProvider(primary_provider, max_retries=3)
    fallback_system = FallbackProvider(retryable_primary, fallback_provider)

    # 4. 建立監控
    monitor = ProviderMonitor()

    # 5. 執行分析
    prompt = "分析以下法條問題..."

    try:
        result = await monitor.monitored_analyze(fallback_system, prompt)
        print(f"分析成功: {result}")

        # 6. 檢查性能指標
        metrics = monitor.get_all_metrics()
        for provider_name, provider_metrics in metrics.items():
            print(f"{provider_name}: 成功率 {provider_metrics.successful_requests/provider_metrics.total_requests:.2%}")

    except LLMProviderError as e:
        print(f"所有提供者都失敗: {e}")
```

### 新提供者集成範例

```python
# 假設要添加一個新的本地 LLM 提供者
class LocalLlamaProvider(LLMProvider):
    """本地 Llama 模型提供者"""

    def __init__(self, config: LLMConfig):
        self.config = config
        # 初始化本地模型...

    async def analyze(self, prompt: str) -> str:
        """使用本地 Llama 模型分析"""
        # 實現本地推理邏輯...
        pass

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "provider": "local_llama",
            "model": self.config.model,
            "version": "1.0"
        }

    @property
    def is_available(self) -> bool:
        return True  # 本地模型，總是可用

# 註冊新提供者
LLMProviderFactory.register_provider(
    LLMProviderEnum.LOCAL,  # 使用現有的 LOCAL 枚舉
    LocalLlamaProvider
)
```

---

## 📈 性能對比參考

### 各提供者特性比較

| 提供者 | 響應速度 | 分析品質 | 成本效益 | 推薦場景 |
|-------|----------|----------|----------|-----------|
| GPT-4o-mini | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 大量批量分析 |
| GPT-4o | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 複雜法條解析 |
| Claude Haiku | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 快速響應需求 |
| Claude Sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 平衡性能品質 |
| Gemini Flash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 成本敏感場景 |
| Simulation | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | 開發測試 |

---

## 🎯 設計原則總結

**Linus 哲學在 LLM 提供者中的體現：**

**1. 消除特殊情況**
```python
# ✅ 統一介面，無特殊處理
async def analyze_with_any_llm(provider: LLMProvider, prompt: str) -> str:
    return await provider.analyze(prompt)  # 所有提供者都一樣

# ❌ 充滿特殊情況的舊設計
def analyze_with_specific_handling(provider_type, prompt):
    if provider_type == "openai":
        # OpenAI 特殊處理...
    elif provider_type == "claude":
        # Claude 特殊處理...
    # ... 更多特殊情況
```

**2. 實用主義優先**
- 優先支援主流、穩定的 LLM API
- 提供模擬器用於開發測試
- 簡單的錯誤處理和重試機制

**3. 簡潔介面**
- 每個提供者只需實現三個方法
- 工廠模式統一建立流程
- 最少但足夠的抽象層

**記住：好的設計讓添加新 LLM 提供者變成只需要實現一個介面的簡單工作。**