"""
Pydantic 數據模型定義
用於 FastAPI 的請求/響應驗證
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ArticleMatch(BaseModel):
    """法條匹配結果"""
    id: str = Field(..., description="法條 ID，如 CPLA-12")
    law_code: str = Field(..., description="法律代碼")
    law_name: str = Field(..., description="法律名稱")
    article_no_main: int = Field(..., description="主條文號")
    article_no_sub: int = Field(0, description="子條文號")
    content: str = Field(..., description="法條內容")
    category: str = Field(..., description="法條分類")
    similarity: float = Field(..., description="相似度分數")


class Option(BaseModel):
    """選項數據"""
    option_letter: str = Field(..., description="選項字母 A/B/C/D")
    option_text: str = Field(..., description="選項內容")
    is_correct_answer: bool = Field(..., description="是否為正確答案")
    matched_articles: List[ArticleMatch] = Field(default_factory=list, description="匹配的法條")


class Question(BaseModel):
    """題目數據"""
    question_number: int = Field(..., description="題號")
    question_text: str = Field(..., description="題目內容")
    correct_answer: str = Field(..., description="正確答案字母")
    options: List[Option] = Field(..., description="選項列表")


class ReportMetadata(BaseModel):
    """報告元數據"""
    source_file: str = Field(..., description="來源檔案名稱")
    laws_csv: str = Field(..., description="法條資料來源")
    total_questions: int = Field(..., description="總題數")
    total_options_processed: int = Field(..., description="處理的選項總數")


class ReportSummary(BaseModel):
    """報告摘要（列表用）"""
    report_id: str = Field(..., description="報告 ID")
    year: str = Field(..., description="考試年份")
    subject: str = Field(..., description="考試科目")
    total_questions: int = Field(..., description="總題數")
    total_options: int = Field(..., description="選項總數")


class ReportDetail(BaseModel):
    """報告詳細數據"""
    metadata: ReportMetadata
    questions: List[Question]


class LawSummary(BaseModel):
    """法條摘要（用於首頁卡片）"""
    law_id: str = Field(..., description="法條 ID")
    law_code: str = Field(..., description="法律代碼")
    law_name: str = Field(..., description="法律名稱")
    article_no: str = Field(..., description="條文號（如 第 12 條）")
    category: str = Field(..., description="法條分類")
    matched_count: int = Field(..., description="匹配次數")
    related_reports: List[str] = Field(default_factory=list, description="相關考卷ID")


class LawDetail(BaseModel):
    """法條詳細資料（點擊卡片後）"""
    law_id: str
    law_code: str
    law_name: str
    article_no: str
    content: str
    category: str
    matched_count: int
    related_questions: List[Dict[str, Any]] = Field(default_factory=list, description="相關題目")
    # related_questions 結構：
    # [
    #   {
    #     "report_id": "113190_1301_民法概要",
    #     "question_number": 1,
    #     "question_text": "...",
    #     "option_letter": "A",
    #     "option_text": "...",
    #     "similarity": 0.42
    #   }
    # ]


class StatsResponse(BaseModel):
    """統計資訊響應"""
    total_reports: int = Field(..., description="總報告數")
    total_questions: int = Field(..., description="總題數")
    total_laws: int = Field(..., description="涉及法條總數")
    years: List[str] = Field(..., description="年份列表")
    subjects: List[str] = Field(..., description="科目列表")
