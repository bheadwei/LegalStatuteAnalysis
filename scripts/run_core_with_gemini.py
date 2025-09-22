#!/usr/bin/env python3
"""
核心 Embedding 匹配系統 - Gemini 版本
使用 Google Gemini API 進行 embedding 相似度比對
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

from src.core_embedding.gemini_embedding_matcher import GeminiEmbeddingMatcher

def main():
    """主程式"""
    print("🎯 核心 Embedding 匹配系統 - Gemini 版本")
    print("=" * 60)
    
    # 檢查 API Key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ 請設定 GEMINI_API_KEY 環境變數")
        print("💡 請在 .env 文件中加入: GEMINI_API_KEY=your_gemini_api_key_here")
        return
    
    # 檔案路徑
    law_csv_path = PROJECT_ROOT / "results" / "law_articles.csv"
    questions_file = PROJECT_ROOT / "results" / "exam_113_complete_llm_improved.json"
    output_file = PROJECT_ROOT / "results" / "core_embedding_matches_gemini.json"
    enhanced_output_file = PROJECT_ROOT / "results" / "core_embedding_enhanced_format_gemini.json"
    
    print(f"法條資料: {law_csv_path}")
    print(f"考題資料: {questions_file}")
    print(f"輸出檔案: {output_file}")
    print("=" * 60)
    
    # 檢查必要文件是否存在
    if not law_csv_path.exists():
        print(f"❌ 法條資料文件不存在: {law_csv_path}")
        print("💡 請先執行: python scripts/law_articles_converter.py")
        return
    
    if not questions_file.exists():
        print(f"❌ 考題資料文件不存在: {questions_file}")
        print("💡 請先執行: python scripts/run_llm_parsing.py")
        return
    
    try:
        # 初始化 Gemini 匹配器
        print("🤖 初始化 Gemini Embedding 匹配器...")
        matcher = GeminiEmbeddingMatcher(api_key)
        
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
        try:
            from scripts.format_embedding_results import convert_to_enhanced_format
            convert_to_enhanced_format(str(output_file), str(enhanced_output_file))
            print(f"🎉 增強格式結果: {enhanced_output_file}")
        except Exception as e:
            print(f"⚠️ 增強格式轉換失敗: {e}")
            print("💡 可以手動執行: python scripts/format_embedding_results.py")
        
    except Exception as e:
        print(f"❌ 執行失敗: {e}")
        print("\n🔧 故障排除建議:")
        print("1. 檢查 GEMINI_API_KEY 是否正確設定")
        print("2. 確認網路連線正常")
        print("3. 檢查 Gemini API 配額是否足夠")
        print("4. 確認必要文件存在且格式正確")
        raise

def test_gemini_connection():
    """測試 Gemini API 連線"""
    print("🧪 測試 Gemini API 連線...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 未設定")
        return False
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # 測試簡單的 embedding 請求
        response = genai.embed_content(
            model="models/embedding-001",
            content="測試文本",
            task_type="retrieval_query"
        )
        
        if response and 'embedding' in response:
            print("✅ Gemini API 連線成功")
            print(f"📊 Embedding 維度: {len(response['embedding'])}")
            return True
        else:
            print("❌ Gemini API 回應格式異常")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API 連線失敗: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gemini Embedding 匹配系統")
    parser.add_argument("--test", action="store_true", help="測試 Gemini API 連線")
    parser.add_argument("--limit", type=int, help="限制處理的題目數量（用於測試）")
    
    args = parser.parse_args()
    
    if args.test:
        test_gemini_connection()
    else:
        main()


