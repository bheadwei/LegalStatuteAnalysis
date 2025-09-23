#!/usr/bin/env python3
"""
測試核心 Embedding 匹配系統
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定路徑
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.core_embedding.embedding_matcher import EmbeddingMatcher

def test_single_question():
    """測試單一題目匹配"""
    print("🧪 測試單一題目匹配")
    print("-" * 30)
    
    # 檢查 API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 請設定 OPENAI_API_KEY 環境變數")
        return
    
    # 初始化匹配器
    matcher = EmbeddingMatcher(api_key)
    
    # 載入法條資料
    law_csv_path = PROJECT_ROOT / "results" / "law_articles.csv"
    print(f"載入法條資料: {law_csv_path}")
    
    if not matcher.load_law_articles(str(law_csv_path)):
        print("❌ 法條資料載入失敗")
        return
    
    # 測試題目
    test_question = "不動產經紀人員執行業務時，應遵守哪些規定？"
    
    print(f"\n測試題目: {test_question}")
    print("-" * 50)
    
    # 執行匹配
    result = matcher.match_question(test_question, "test_01")
    
    print(f"處理時間: {result.processing_time:.2f} 秒")
    print(f"匹配結果 (前 3 條):")
    
    for i, article in enumerate(result.matched_articles[:3], 1):
        print(f"\n{i}. 相似度: {article['similarity']:.4f}")
        print(f"   法規: {article['law_name']}")
        print(f"   條文: 第{article['article_no_main']}條")
        print(f"   內容: {article['content'][:100]}...")

def test_single_option():
    """測試單一選項匹配"""
    print("\n\n🧪 測試單一選項匹配")
    print("-" * 30)
    
    # 檢查 API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 請設定 OPENAI_API_KEY 環境變數")
        return
    
    # 初始化匹配器
    matcher = EmbeddingMatcher(api_key)
    
    # 載入法條資料
    law_csv_path = PROJECT_ROOT / "results" / "law_articles.csv"
    if not matcher.load_law_articles(str(law_csv_path)):
        print("❌ 法條資料載入失敗")
        return
    
    # 測試題目和選項
    question = "不動產經紀業的營業保證金規定，下列何者正確？"
    option_A = "公司組織經營者，應繳存營業保證金新臺幣一千萬元"
    
    print(f"測試題目: {question}")
    print(f"測試選項 A: {option_A}")
    print("-" * 50)
    
    # 執行匹配
    result = matcher.match_option(question, "A", option_A, "test_02")
    
    print(f"處理時間: {result.processing_time:.2f} 秒")
    print(f"匹配結果 (前 3 條):")
    
    for i, article in enumerate(result.matched_articles[:3], 1):
        print(f"\n{i}. 相似度: {article['similarity']:.4f}")
        print(f"   法規: {article['law_name']}")
        print(f"   條文: 第{article['article_no_main']}條")
        print(f"   內容: {article['content'][:100]}...")

if __name__ == "__main__":
    test_single_question()
    test_single_option()
