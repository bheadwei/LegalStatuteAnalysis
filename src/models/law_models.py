#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法條考題智能對應系統 - 資料模型
提供結構化的資料類別定義，確保類型安全和資料一致性
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
import json


# --- 枚舉類型 ---

class QuestionType(Enum):
    """考題類型"""
    MULTIPLE_CHOICE = "multiple_choice"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"


class LLMProvider(Enum):
    """LLM 提供者"""
    OPENAI = "openai"
    CLAUDE = "claude"
    LOCAL = "local"
    SIMULATION = "simulation"


class ConfidenceLevel(Enum):
    """信心度等級"""
    VERY_LOW = (0.0, 0.3, "極低")
    LOW = (0.3, 0.5, "低")
    MEDIUM = (0.5, 0.7, "中等")
    HIGH = (0.7, 0.9, "高")
    VERY_HIGH = (0.9, 1.0, "極高")
    
    def __init__(self, min_score: float, max_score: float, label: str):
        self.min_score = min_score
        self.max_score = max_score
        self.label = label
    
    @classmethod
    def from_score(cls, score: float) -> ConfidenceLevel:
        """根據分數判斷信心度等級"""
        for level in cls:
            if level.min_score <= score < level.max_score:
                return level
        return cls.VERY_HIGH if score >= 0.9 else cls.VERY_LOW


# --- 基礎資料模型 ---

@dataclass
class LawArticle:
    """法條資料模型"""
    law_code: str
    law_name: str
    revision_date: str
    chapter_no: int
    chapter_title: str
    article_no_main: int
    article_no_sub: int
    content: str
    category: Optional[str] = None
    authority: Optional[str] = None
    
    @property
    def article_id(self) -> str:
        """法條唯一識別碼"""
        if self.article_no_sub > 0:
            return f"{self.law_code}-{self.article_no_main}-{self.article_no_sub}"
        return f"{self.law_code}-{self.article_no_main}"
    
    @property
    def article_label(self) -> str:
        """法條標籤顯示"""
        if self.article_no_sub > 0:
            return f"第{self.article_no_main}-{self.article_no_sub}條"
        return f"第{self.article_no_main}條"
    
    @property
    def full_title(self) -> str:
        """完整法條標題"""
        return f"{self.law_name} {self.article_label}"
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "article_id": self.article_id,
            "law_code": self.law_code,
            "law_name": self.law_name,
            "revision_date": self.revision_date,
            "category": self.category,
            "authority": self.authority,
            "chapter_no": self.chapter_no,
            "chapter_title": self.chapter_title,
            "article_no_main": self.article_no_main,
            "article_no_sub": self.article_no_sub,
            "article_label": self.article_label,
            "full_title": self.full_title,
            "content": self.content
        }


@dataclass
class ExamQuestion:
    """考題資料模型"""
    question_number: int
    content: str
    question_type: QuestionType
    options: Dict[str, str] = field(default_factory=dict)
    correct_answer: Optional[str] = None
    points: int = 2
    section: Optional[str] = None
    difficulty: Optional[str] = None
    
    @property
    def is_multiple_choice(self) -> bool:
        """是否為選擇題"""
        return self.question_type == QuestionType.MULTIPLE_CHOICE
    
    @property
    def is_essay(self) -> bool:
        """是否為申論題"""
        return self.question_type == QuestionType.ESSAY
    
    @property
    def option_count(self) -> int:
        """選項數量"""
        return len(self.options)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "question_number": self.question_number,
            "content": self.content,
            "question_type": self.question_type.value,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "points": self.points,
            "section": self.section,
            "difficulty": self.difficulty,
            "is_multiple_choice": self.is_multiple_choice,
            "is_essay": self.is_essay,
            "option_count": self.option_count
        }


# --- LLM 相關模型 ---

@dataclass
class LLMConfig:
    """LLM 配置模型"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 1500
    timeout: int = 30
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LLMConfig:
        """從字典創建配置"""
        provider = LLMProvider(data.get("provider", "simulation"))
        return cls(
            provider=provider,
            model=data.get("model", "sim-v1"),
            api_key=data.get("api_key"),
            api_base=data.get("api_base"),
            temperature=data.get("temperature", 0.0),
            max_tokens=data.get("max_tokens", 1500),
            timeout=data.get("timeout", 30)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout
        }


@dataclass
class LLMAnalysisResult:
    """LLM 分析結果模型"""
    success: bool
    content: str
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    confidence: Optional[float] = None
    
    @property
    def confidence_level(self) -> Optional[ConfidenceLevel]:
        """信心度等級"""
        if self.confidence is not None:
            return ConfidenceLevel.from_score(self.confidence)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "success": self.success,
            "content": self.content,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "error_message": self.error_message,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level.label if self.confidence_level else None
        }


# --- 法源對應模型 ---

@dataclass
class LawSourceMapping:
    """法源對應結果模型"""
    option_key: str
    option_content: str
    matched_articles: List[LawArticle]
    confidence_score: float
    reasoning: str
    legal_analysis: str
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """信心度等級"""
        return ConfidenceLevel.from_score(self.confidence_score)
    
    @property
    def has_high_confidence(self) -> bool:
        """是否有高信心度"""
        return self.confidence_score >= 0.7
    
    @property
    def matched_article_count(self) -> int:
        """匹配的法條數量"""
        return len(self.matched_articles)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "option_key": self.option_key,
            "option_content": self.option_content,
            "matched_articles": [article.to_dict() for article in self.matched_articles],
            "confidence_score": self.confidence_score,
            "confidence_level": self.confidence_level.label,
            "has_high_confidence": self.has_high_confidence,
            "reasoning": self.reasoning,
            "legal_analysis": self.legal_analysis,
            "matched_article_count": self.matched_article_count,
            "analysis_timestamp": self.analysis_timestamp.isoformat()
        }


@dataclass
class QuestionMapping:
    """題目法條對應結果模型"""
    question: ExamQuestion
    primary_articles: List[LawArticle]
    option_mappings: List[LawSourceMapping]
    overall_confidence: float
    llm_analysis: str
    processing_time: Optional[float] = None
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """整體信心度等級"""
        return ConfidenceLevel.from_score(self.overall_confidence)
    
    @property
    def primary_article_count(self) -> int:
        """主要法條數量"""
        return len(self.primary_articles)
    
    @property
    def option_mapping_count(self) -> int:
        """選項對應數量"""
        return len(self.option_mappings)
    
    @property
    def high_confidence_options(self) -> List[LawSourceMapping]:
        """高信心度的選項對應"""
        return [mapping for mapping in self.option_mappings if mapping.has_high_confidence]
    
    @property
    def success_rate(self) -> float:
        """成功對應比率"""
        if not self.option_mappings:
            return 0.0
        return len(self.high_confidence_options) / len(self.option_mappings)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "question": self.question.to_dict(),
            "primary_articles": [article.to_dict() for article in self.primary_articles],
            "option_mappings": [mapping.to_dict() for mapping in self.option_mappings],
            "overall_confidence": self.overall_confidence,
            "confidence_level": self.confidence_level.label,
            "llm_analysis": self.llm_analysis,
            "processing_time": self.processing_time,
            "primary_article_count": self.primary_article_count,
            "option_mapping_count": self.option_mapping_count,
            "high_confidence_options_count": len(self.high_confidence_options),
            "success_rate": self.success_rate,
            "analysis_timestamp": self.analysis_timestamp.isoformat()
        }


# --- 批次處理模型 ---

@dataclass
class MappingReport:
    """對應報告模型"""
    mappings: List[QuestionMapping]
    metadata: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total_questions(self) -> int:
        """總題目數"""
        return len(self.mappings)
    
    @property
    def average_confidence(self) -> float:
        """平均信心度"""
        if not self.mappings:
            return 0.0
        return sum(m.overall_confidence for m in self.mappings) / len(self.mappings)
    
    @property
    def high_confidence_count(self) -> int:
        """高信心度題目數"""
        return len([m for m in self.mappings if m.overall_confidence >= 0.7])
    
    @property
    def success_rate(self) -> float:
        """整體成功率"""
        if not self.mappings:
            return 0.0
        return self.high_confidence_count / self.total_questions
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "metadata": {
                **self.metadata,
                "total_questions": self.total_questions,
                "average_confidence": self.average_confidence,
                "high_confidence_count": self.high_confidence_count,
                "success_rate": self.success_rate,
                "generated_at": self.generated_at.isoformat()
            },
            "question_mappings": [mapping.to_dict() for mapping in self.mappings]
        }
    
    def save_to_file(self, file_path: str) -> None:
        """保存到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


# --- 配置模型 ---

@dataclass 
class SystemConfig:
    """系統配置模型"""
    version: str
    description: str
    law_definitions: Dict[str, Dict[str, Any]]
    exam_sets: Dict[str, Dict[str, Any]]
    llm_config: Dict[str, Any]
    output_settings: Dict[str, Any]
    
    @classmethod
    def load_from_file(cls, config_file: str = "law_config.json") -> SystemConfig:
        """從文件載入配置"""
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return cls(
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            law_definitions=data.get("law_definitions", {}),
            exam_sets=data.get("exam_sets", {}),
            llm_config=data.get("llm_config", {}),
            output_settings=data.get("output_settings", {})
        )
    
    def get_llm_config(self, provider: Optional[str] = None) -> LLMConfig:
        """獲取 LLM 配置"""
        llm_conf = self.llm_config
        target_provider = provider or llm_conf.get("default_provider", "simulation")
        provider_config = llm_conf.get("providers", {}).get(target_provider, {})
        
        return LLMConfig.from_dict({
            "provider": target_provider,
            **provider_config
        })
