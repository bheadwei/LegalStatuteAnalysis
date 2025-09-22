#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法條考題智能對應系統 - 資料載入器
提供標準化的資料載入和轉換功能
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from .law_models import (
    LawArticle, ExamQuestion, QuestionType, SystemConfig
)

logger = logging.getLogger(__name__)


class LawArticleLoader:
    """法條資料載入器"""
    
    # CSV 欄位映射
    COLUMN_MAPPING = {
        '法規代碼': 'law_code',
        '法規名稱': 'law_name', 
        '修正日期（民國）': 'revision_date',
        '法規類別': 'category',
        '主管機關': 'authority',
        '章節編號': 'chapter_no',
        '章節標題': 'chapter_title',
        '條文主號': 'article_no_main',
        '條文次號': 'article_no_sub',
        '條文完整內容': 'content'
    }
    
    @classmethod
    def load_from_csv(cls, csv_path: str) -> List[LawArticle]:
        """從 CSV 文件載入法條資料"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"📊 從 CSV 載入 {len(df)} 筆法條資料: {csv_path}")
            
            # 重命名欄位
            df_renamed = df.rename(columns=cls.COLUMN_MAPPING)
            
            articles = []
            for _, row in df_renamed.iterrows():
                article = LawArticle(
                    law_code=str(row['law_code']),
                    law_name=str(row['law_name']),
                    revision_date=str(row['revision_date']),
                    chapter_no=int(row['chapter_no']),
                    chapter_title=str(row['chapter_title']),
                    article_no_main=int(row['article_no_main']),
                    article_no_sub=int(row['article_no_sub']),
                    content=str(row['content']),
                    category=str(row.get('category', '')) if pd.notna(row.get('category')) else None,
                    authority=str(row.get('authority', '')) if pd.notna(row.get('authority')) else None
                )
                articles.append(article)
            
            logger.info(f"✅ 成功載入 {len(articles)} 條法規條文")
            return articles
            
        except Exception as e:
            logger.error(f"❌ 載入法條資料失敗: {e}")
            raise
    
    @classmethod
    def load_from_config(cls, config: SystemConfig) -> List[LawArticle]:
        """從系統配置載入法條資料"""
        # 預留功能：未來可以從配置的法條定義直接載入
        # 目前仍使用 CSV 方式
        csv_path = "results/law_articles.csv"  # 預設路徑
        return cls.load_from_csv(csv_path)


class ExamQuestionLoader:
    """考題資料載入器"""
    
    @classmethod
    def load_from_json(cls, json_path: str) -> List[ExamQuestion]:
        """從 JSON 文件載入考題資料"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"📊 從 JSON 載入考題資料: {json_path}")
            
            questions = []
            
            # 載入申論題
            essay_section = data.get('essay_section', {})
            for essay_q in essay_section.get('questions', []):
                question = ExamQuestion(
                    question_number=essay_q['question_number'],
                    content=essay_q['content'],
                    question_type=QuestionType.ESSAY,
                    options={},
                    correct_answer=None,
                    points=essay_q.get('points', 25),
                    section="essay"
                )
                questions.append(question)
            
            # 載入選擇題
            mc_section = data.get('multiple_choice_section', {})
            for mc_q in mc_section.get('questions', []):
                question = ExamQuestion(
                    question_number=mc_q['question_number'],
                    content=mc_q['content'],
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    options=mc_q.get('options', {}),
                    correct_answer=mc_q.get('correct_answer'),
                    points=mc_q.get('points', 2),
                    section="multiple_choice"
                )
                questions.append(question)
            
            logger.info(f"✅ 成功載入 {len(questions)} 道考試題目")
            logger.info(f"   - 申論題: {len([q for q in questions if q.is_essay])} 道")
            logger.info(f"   - 選擇題: {len([q for q in questions if q.is_multiple_choice])} 道")
            
            return questions
            
        except Exception as e:
            logger.error(f"❌ 載入考題資料失敗: {e}")
            raise
    
    @classmethod
    def load_from_config(cls, config: SystemConfig, exam_set_name: str) -> List[ExamQuestion]:
        """從系統配置載入指定考試集的題目"""
        exam_sets = config.exam_sets
        if exam_set_name not in exam_sets:
            raise ValueError(f"找不到考試集: {exam_set_name}")
        
        exam_config = exam_sets[exam_set_name]
        
        # 檢查是否有已經解析好的 LLM 版本
        llm_output_file = "results/exam_113_complete_llm_improved.json"
        if Path(llm_output_file).exists():
            logger.info("🎯 使用 LLM 優化版本的考題資料")
            return cls.load_from_json(llm_output_file)
        
        # 否則使用配置中指定的文件
        output_file = exam_config.get('output_file')
        if output_file and Path(output_file).exists():
            return cls.load_from_json(output_file)
        
        raise FileNotFoundError(f"找不到考題資料文件: {output_file}")


class DataRepository:
    """資料倉庫 - 統一管理所有資料載入"""
    
    def __init__(self, config: SystemConfig):
        self.config = config
        self._law_articles: Optional[List[LawArticle]] = None
        self._exam_questions: Optional[List[ExamQuestion]] = None
    
    @property
    def law_articles(self) -> List[LawArticle]:
        """延遲載入法條資料"""
        if self._law_articles is None:
            self._law_articles = LawArticleLoader.load_from_config(self.config)
        return self._law_articles
    
    @property  
    def exam_questions(self) -> List[ExamQuestion]:
        """延遲載入考題資料"""
        if self._exam_questions is None:
            # 預設載入第一個考試集
            exam_set_names = list(self.config.exam_sets.keys())
            if not exam_set_names:
                raise ValueError("配置中沒有定義考試集")
            
            first_exam_set = exam_set_names[0]
            self._exam_questions = ExamQuestionLoader.load_from_config(
                self.config, first_exam_set
            )
        return self._exam_questions
    
    def load_exam_set(self, exam_set_name: str) -> List[ExamQuestion]:
        """載入指定的考試集"""
        return ExamQuestionLoader.load_from_config(self.config, exam_set_name)
    
    def reload_data(self) -> None:
        """重新載入所有資料"""
        self._law_articles = None
        self._exam_questions = None
        logger.info("🔄 已清除快取，下次存取時將重新載入資料")
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取資料統計"""
        return {
            "law_article_count": len(self.law_articles),
            "exam_question_count": len(self.exam_questions),
            "essay_question_count": len([q for q in self.exam_questions if q.is_essay]),
            "mc_question_count": len([q for q in self.exam_questions if q.is_multiple_choice]),
            "law_codes": list(set(a.law_code for a in self.law_articles)),
            "exam_sets": list(self.config.exam_sets.keys())
        }
