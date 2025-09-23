#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
純粹的 Embedding 匹配系統
題目 <-> 法條的直接 embedding 相似度比對
"""

import json
import logging
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class MatchResult:
    """匹配結果"""
    question_id: str
    question_content: str
    matched_articles: List[Dict[str, Any]]
    processing_time: float

@dataclass 
class OptionMatchResult:
    """選項匹配結果"""
    question_id: str
    option_letter: str
    option_content: str
    matched_articles: List[Dict[str, Any]]
    processing_time: float

class EmbeddingMatcher:
    """純粹的 Embedding 匹配器"""
    
    def __init__(self, openai_api_key: str, embedding_model: str = "text-embedding-3-large"):
        self.client = OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model
        
        # 法條資料
        self.law_articles: List[Dict[str, Any]] = []
        self.law_embeddings: Optional[np.ndarray] = None
        
        logger.info(f"🎯 初始化 Embedding 匹配器: {embedding_model}")

    def load_law_articles(self, csv_path: str) -> bool:
        """載入法條資料並建立 embeddings"""
        try:
            logger.info(f"📊 載入法條資料: {csv_path}")
            
            # 讀取 CSV
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"📋 載入 {len(df)} 條法規資料")
            
            # 轉換為字典格式
            self.law_articles = []
            for _, row in df.iterrows():
                article = {
                    "id": f"{row['法規代碼']}-{row['條文主號']}-{row['條文次號']}" if row['條文次號'] > 0 else f"{row['法規代碼']}-{row['條文主號']}",
                    "law_code": row['法規代碼'],
                    "law_name": row['法規名稱'],
                    "chapter_title": row['章節標題'],
                    "article_no_main": row['條文主號'],
                    "article_no_sub": row['條文次號'],
                    "content": row['條文完整內容'],
                    "category": row.get('法規類別', ''),
                    "authority": row.get('主管機關', '')
                }
                self.law_articles.append(article)
            
            # 建立 embeddings
            self._build_embeddings()
            
            logger.info(f"✅ 法條資料載入完成: {len(self.law_articles)} 條")
            return True
            
        except Exception as e:
            logger.error(f"❌ 載入法條資料失敗: {e}")
            return False

    def _build_embeddings(self):
        """建立法條 embeddings"""
        logger.info("🔧 建立法條 embeddings...")
        
        # 準備文本
        law_texts = []
        for article in self.law_articles:
            # 簡單組合：法規名稱 + 條文內容
            text = f"{article['law_name']} 第{article['article_no_main']}條 {article['content']}"
            law_texts.append(text)
        
        # 批次呼叫 OpenAI Embeddings API
        embeddings = []
        batch_size = 100
        
        for i in range(0, len(law_texts), batch_size):
            batch = law_texts[i:i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.embedding_model
            )
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
            
            logger.info(f"完成批次 {i//batch_size + 1}/{(len(law_texts)-1)//batch_size + 1}")
        
        self.law_embeddings = np.array(embeddings)
        logger.info(f"✅ 完成建立 {len(embeddings)} 條法條的 embeddings")

    def match_question(self, question_content: str, question_id: str = "", top_k: int = 1) -> MatchResult:
        """匹配單一題目"""
        start_time = time.time()
        
        if self.law_embeddings is None:
            raise ValueError("法條 embeddings 尚未建立")
        
        # 取得題目 embedding
        response = self.client.embeddings.create(
            input=[question_content],
            model=self.embedding_model
        )
        question_embedding = np.array(response.data[0].embedding).reshape(1, -1)
        
        # 計算相似度
        similarities = np.dot(question_embedding, self.law_embeddings.T)[0]
        
        # 取得 top-k 結果
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        matched_articles = []
        for idx in top_indices:
            article = self.law_articles[idx].copy()
            article['similarity'] = float(similarities[idx])
            matched_articles.append(article)
        
        processing_time = time.time() - start_time
        
        return MatchResult(
            question_id=question_id,
            question_content=question_content,
            matched_articles=matched_articles,
            processing_time=processing_time
        )

    def match_option(self, question_content: str, option_letter: str, option_content: str, question_id: str = "", top_k: int = 1) -> OptionMatchResult:
        """匹配單一選項"""
        start_time = time.time()
        
        if self.law_embeddings is None:
            raise ValueError("法條 embeddings 尚未建立")
        
        # 組合題目與選項
        combined_text = f"題目: {question_content}\n選項 {option_letter}: {option_content}"
        
        # 取得 embedding
        response = self.client.embeddings.create(
            input=[combined_text],
            model=self.embedding_model
        )
        option_embedding = np.array(response.data[0].embedding).reshape(1, -1)
        
        # 計算相似度
        similarities = np.dot(option_embedding, self.law_embeddings.T)[0]
        
        # 取得 top-k 結果
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        matched_articles = []
        for idx in top_indices:
            article = self.law_articles[idx].copy()
            article['similarity'] = float(similarities[idx])
            matched_articles.append(article)
        
        processing_time = time.time() - start_time
        
        return OptionMatchResult(
            question_id=question_id,
            option_letter=option_letter,
            option_content=option_content,
            matched_articles=matched_articles,
            processing_time=processing_time
        )

    def process_exam_questions(self, questions_file: str, output_file: str = None) -> Dict[str, Any]:
        """處理完整考題集"""
        logger.info(f"📝 處理考題集: {questions_file}")
        
        # 讀取考題
        with open(questions_file, 'r', encoding='utf-8') as f:
            exam_data = json.load(f)
        
        results = {
            "metadata": {
                "source_file": questions_file,
                "embedding_model": self.embedding_model,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_law_articles": len(self.law_articles)
            },
            "question_matches": [],
            "option_matches": [],
            "statistics": {
                "total_processing_time": 0.0,
                "questions_processed": 0,
                "options_processed": 0
            }
        }
        
        start_time = time.time()
        
        # 處理選擇題
        mc_questions = exam_data.get('multiple_choice_section', {}).get('questions', [])
        
        for question in mc_questions:
            question_id = str(question['question_number'])
            question_content = question['content']
            
            # 匹配題目
            try:
                question_match = self.match_question(question_content, question_id)
                results["question_matches"].append({
                    "question_id": question_match.question_id,
                    "question_content": question_match.question_content,
                    "matched_articles": question_match.matched_articles,
                    "processing_time": question_match.processing_time
                })
                results["statistics"]["questions_processed"] += 1
                
            except Exception as e:
                logger.error(f"題目 {question_id} 匹配失敗: {e}")
            
            # 匹配選項
            options = question.get('options', {})
            for option_letter, option_content in options.items():
                try:
                    option_match = self.match_option(question_content, option_letter, option_content, question_id)
                    results["option_matches"].append({
                        "question_id": option_match.question_id,
                        "option_letter": option_match.option_letter,
                        "option_content": option_match.option_content,
                        "matched_articles": option_match.matched_articles,
                        "processing_time": option_match.processing_time
                    })
                    results["statistics"]["options_processed"] += 1
                    
                except Exception as e:
                    logger.error(f"選項 {question_id}-{option_letter} 匹配失敗: {e}")
        
        total_time = time.time() - start_time
        results["statistics"]["total_processing_time"] = total_time
        
        # 保存結果
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 結果已保存: {output_file}")
        
        logger.info(f"✅ 處理完成: {results['statistics']['questions_processed']} 題目, {results['statistics']['options_processed']} 選項")
        
        return results
