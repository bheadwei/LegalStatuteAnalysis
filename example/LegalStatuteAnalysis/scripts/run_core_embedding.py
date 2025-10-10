#!/usr/bin/env python3
"""
核心 Embedding 匹配系統 - 主程式
純粹的 embedding 相似度比對，無複雜邏輯
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

def main():
    """主程式"""
    print("🎯 核心 Embedding 匹配系統")
    print("=" * 50)
    
    # 檢查 API Key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 請設定 OPENAI_API_KEY 環境變數")
        return
    
    # 檔案路徑
    law_csv_path = PROJECT_ROOT / "results" / "law_articles.csv"
    questions_file = PROJECT_ROOT / "results" / "exam_113_complete_llm_improved.json"
    output_file = PROJECT_ROOT / "results" / "core_embedding_matches.json"
    enhanced_output_file = PROJECT_ROOT / "results" / "core_embedding_enhanced_format.json"
    
    print(f"法條資料: {law_csv_path}")
    print(f"考題資料: {questions_file}")
    print(f"輸出檔案: {output_file}")
    print("=" * 50)
    
    try:
        # 初始化匹配器
        matcher = EmbeddingMatcher(api_key)
        
        # 載入法條資料
        print("📊 載入法條資料...")
        if not matcher.load_law_articles(str(law_csv_path)):
            print("❌ 法條資料載入失敗")
            return
        
        # 處理考題
        print("📝 開始處理考題...")
        results = matcher.process_exam_questions(str(questions_file), str(output_file))
        
        # 顯示統計
        stats = results["statistics"]
        print("\n📈 處理統計:")
        print(f"   題目數: {stats['questions_processed']}")
        print(f"   選項數: {stats['options_processed']}")
        print(f"   總耗時: {stats['total_processing_time']:.1f} 秒")
        print(f"   平均每題: {stats['total_processing_time'] / max(stats['questions_processed'], 1):.1f} 秒")
        
        print(f"\n✅ 完成！結果已保存至: {output_file}")
        
        # 自動轉換為增強格式
        print("\n🔄 轉換為增強格式...")
        from scripts.format_embedding_results import convert_to_enhanced_format
        convert_to_enhanced_format(str(output_file), str(enhanced_output_file))
        
        print(f"🎉 增強格式結果: {enhanced_output_file}")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        raise

if __name__ == "__main__":
    main()
