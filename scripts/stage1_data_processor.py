#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一階段：資料處理與分析
整合題目、法條、匹配關係資料，建立完整的關聯結構
"""

import json
import pandas as pd
import os
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, base_path: str = "/home/bheadwei/LegalStatuteAnalysis_V2"):
        self.base_path = base_path
        self.results_path = os.path.join(base_path, "results")
        
        # 資料檔案路徑
        self.questions_file = os.path.join(self.results_path, "core_embedding_enhanced_format_gemini.json")
        self.matches_file = os.path.join(self.results_path, "core_embedding_matches_gemini.json")
        self.laws_file = os.path.join(self.results_path, "law_articles.csv")
        
        # 資料結構
        self.questions_data = {}
        self.matches_data = {}
        self.laws_data = {}
        self.integrated_data = {}
        
    def load_questions_data(self) -> Dict[str, Any]:
        """載入題目資料"""
        logger.info("載入題目資料...")
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.questions_data = {
                'metadata': data.get('metadata', {}),
                'questions': data.get('questions', [])
            }
            
            logger.info(f"成功載入 {len(self.questions_data['questions'])} 題")
            return self.questions_data
            
        except Exception as e:
            logger.error(f"載入題目資料失敗: {e}")
            raise
    
    def load_matches_data(self) -> Dict[str, Any]:
        """載入法條匹配資料"""
        logger.info("載入法條匹配資料...")
        try:
            with open(self.matches_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.matches_data = {
                'metadata': data.get('metadata', {}),
                'question_matches': data.get('question_matches', [])
            }
            
            logger.info(f"成功載入 {len(self.matches_data['question_matches'])} 個匹配記錄")
            return self.matches_data
            
        except Exception as e:
            logger.error(f"載入匹配資料失敗: {e}")
            raise
    
    def load_laws_data(self) -> Dict[str, Any]:
        """載入法條資料"""
        logger.info("載入法條資料...")
        try:
            df = pd.read_csv(self.laws_file, encoding='utf-8')
            
            # 轉換為字典格式，以法條ID為key
            laws_dict = {}
            for _, row in df.iterrows():
                law_id = f"{row['法規代碼']}-{row['條文主號']}"
                if row['條文次號'] != 0:
                    law_id += f"-{row['條文次號']}"
                
                laws_dict[law_id] = {
                    'id': law_id,
                    'law_code': row['法規代碼'],
                    'law_name': row['法規名稱'],
                    'chapter_title': row['章節標題'],
                    'article_no_main': row['條文主號'],
                    'article_no_sub': row['條文次號'],
                    'content': row['條文完整內容'],
                    'category': row['法規類別'],
                    'authority': row['主管機關'],
                    'amend_date': row['修正日期（民國）']
                }
            
            self.laws_data = laws_dict
            logger.info(f"成功載入 {len(self.laws_data)} 條法條")
            return self.laws_data
            
        except Exception as e:
            logger.error(f"載入法條資料失敗: {e}")
            raise
    
    def build_question_law_mapping(self) -> Dict[str, List[Dict]]:
        """建立題目與法條的對應關係"""
        logger.info("建立題目與法條對應關係...")
        
        question_law_mapping = defaultdict(list)
        
        # 從匹配資料中建立對應關係
        for match in self.matches_data['question_matches']:
            question_id = match['question_id']
            
            for article in match['matched_articles']:
                article_id = article['id']
                
                # 檢查法條是否存在於法條資料中
                if article_id in self.laws_data:
                    law_info = self.laws_data[article_id].copy()
                    law_info['similarity'] = article.get('similarity', 0)
                    question_law_mapping[question_id].append(law_info)
                else:
                    logger.warning(f"法條 {article_id} 不存在於法條資料中")
        
        logger.info(f"建立 {len(question_law_mapping)} 個題目的法條對應關係")
        return dict(question_law_mapping)
    
    def build_law_question_mapping(self) -> Dict[str, List[Dict]]:
        """建立法條與題目的對應關係"""
        logger.info("建立法條與題目對應關係...")
        
        law_question_mapping = defaultdict(list)
        
        # 從題目資料中建立對應關係
        for question in self.questions_data['questions']:
            question_id = str(question['question_number'])
            
            # 從選項中提取法條引用
            for option_key, option_data in question['options'].items():
                if len(option_data) > 1:  # 如果有法條引用
                    law_reference = option_data[1]  # 第二個元素是法條引用
                    
                    # 解析法條引用格式 (例如: "不動產經紀業管理條例 第29條")
                    if '第' in law_reference and '條' in law_reference:
                        # 提取法條名稱和條號
                        parts = law_reference.split('第')
                        if len(parts) == 2:
                            law_name = parts[0].strip()
                            article_part = parts[1].replace('條', '').strip()
                            
                            # 尋找對應的法條
                            for law_id, law_data in self.laws_data.items():
                                if (law_data['law_name'] == law_name and 
                                    str(law_data['article_no_main']) == article_part):
                                    
                                    question_info = {
                                        'question_id': question_id,
                                        'question_number': question['question_number'],
                                        'question_content': question['content'][0],
                                        'option_key': option_key,
                                        'option_content': option_data[0],
                                        'is_correct': option_key == question['correct_answer']
                                    }
                                    
                                    law_question_mapping[law_id].append(question_info)
        
        logger.info(f"建立 {len(law_question_mapping)} 個法條的題目對應關係")
        return dict(law_question_mapping)
    
    def integrate_data(self) -> Dict[str, Any]:
        """整合所有資料"""
        logger.info("開始整合資料...")
        
        # 載入所有資料
        self.load_questions_data()
        self.load_matches_data()
        self.load_laws_data()
        
        # 建立對應關係
        question_law_mapping = self.build_question_law_mapping()
        law_question_mapping = self.build_law_question_mapping()
        
        # 整合資料結構
        self.integrated_data = {
            'metadata': {
                'total_questions': len(self.questions_data['questions']),
                'total_laws': len(self.laws_data),
                'total_matches': len(self.matches_data['question_matches']),
                'processing_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'questions': self.questions_data['questions'],
            'laws': self.laws_data,
            'question_law_mapping': question_law_mapping,
            'law_question_mapping': law_question_mapping
        }
        
        logger.info("資料整合完成")
        return self.integrated_data
    
    def generate_statistics(self) -> Dict[str, Any]:
        """生成統計資料"""
        logger.info("生成統計資料...")
        
        stats = {
            'law_statistics': {},
            'question_statistics': {},
            'mapping_statistics': {}
        }
        
        # 法條統計
        law_categories = defaultdict(int)
        law_authorities = defaultdict(int)
        laws_with_questions = 0
        
        for law_id, law_data in self.laws_data.items():
            law_categories[law_data['category']] += 1
            law_authorities[law_data['authority']] += 1
            
            if law_id in self.integrated_data['law_question_mapping']:
                laws_with_questions += 1
        
        stats['law_statistics'] = {
            'total_laws': len(self.laws_data),
            'laws_with_questions': laws_with_questions,
            'laws_without_questions': len(self.laws_data) - laws_with_questions,
            'categories': dict(law_categories),
            'authorities': dict(law_authorities)
        }
        
        # 題目統計
        total_options = 0
        correct_options = 0
        
        for question in self.questions_data['questions']:
            total_options += len(question['options'])
            correct_options += 1  # 每題有一個正確答案
        
        stats['question_statistics'] = {
            'total_questions': len(self.questions_data['questions']),
            'total_options': total_options,
            'correct_options': correct_options,
            'average_options_per_question': total_options / len(self.questions_data['questions'])
        }
        
        # 對應關係統計
        stats['mapping_statistics'] = {
            'question_law_mappings': len(self.integrated_data['question_law_mapping']),
            'law_question_mappings': len(self.integrated_data['law_question_mapping']),
            'average_laws_per_question': sum(len(laws) for laws in self.integrated_data['question_law_mapping'].values()) / len(self.integrated_data['question_law_mapping']) if self.integrated_data['question_law_mapping'] else 0,
            'average_questions_per_law': sum(len(questions) for questions in self.integrated_data['law_question_mapping'].values()) / len(self.integrated_data['law_question_mapping']) if self.integrated_data['law_question_mapping'] else 0
        }
        
        logger.info("統計資料生成完成")
        return stats
    
    def save_integrated_data(self, output_file: str = None) -> str:
        """儲存整合後的資料"""
        if output_file is None:
            output_file = os.path.join(self.results_path, "integrated_data_stage1.json")
        
        logger.info(f"儲存整合資料到 {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.integrated_data, f, ensure_ascii=False, indent=2)
            
            logger.info("整合資料儲存成功")
            return output_file
            
        except Exception as e:
            logger.error(f"儲存整合資料失敗: {e}")
            raise
    
    def save_statistics(self, stats: Dict[str, Any], output_file: str = None) -> str:
        """儲存統計資料"""
        if output_file is None:
            output_file = os.path.join(self.results_path, "statistics_stage1.json")
        
        logger.info(f"儲存統計資料到 {output_file}")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            
            logger.info("統計資料儲存成功")
            return output_file
            
        except Exception as e:
            logger.error(f"儲存統計資料失敗: {e}")
            raise

def main():
    """主函數"""
    logger.info("開始第一階段資料處理...")
    
    try:
        # 初始化處理器
        processor = DataProcessor()
        
        # 整合資料
        integrated_data = processor.integrate_data()
        
        # 生成統計
        statistics = processor.generate_statistics()
        
        # 儲存結果
        integrated_file = processor.save_integrated_data()
        stats_file = processor.save_statistics(statistics)
        
        # 輸出摘要
        logger.info("=" * 50)
        logger.info("第一階段處理完成摘要:")
        logger.info(f"總題目數: {integrated_data['metadata']['total_questions']}")
        logger.info(f"總法條數: {integrated_data['metadata']['total_laws']}")
        logger.info(f"有考題的法條數: {statistics['law_statistics']['laws_with_questions']}")
        logger.info(f"整合資料檔案: {integrated_file}")
        logger.info(f"統計資料檔案: {stats_file}")
        logger.info("=" * 50)
        
        return True
        
    except Exception as e:
        logger.error(f"第一階段處理失敗: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
