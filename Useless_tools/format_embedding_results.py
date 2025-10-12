#!/usr/bin/env python3
"""
格式轉換工具
將 core_embedding_matches.json 轉換為 rag_enhanced_sample.json 的格式
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# 設定路徑
PROJECT_ROOT = Path(__file__).parent.parent

def format_similarity_text(matched_articles: List[Dict[str, Any]]) -> str:
    """格式化相似度文本"""
    formatted_parts = []
    for article in matched_articles:
        law_name = article['law_name']
        article_no = article['article_no_main']
        similarity = article['similarity']
        formatted_parts.append(f"{law_name} 第{article_no}條")
    
    return " | ".join(formatted_parts)

def convert_to_enhanced_format(input_file: str, output_file: str):
    """轉換格式"""
    print(f"🔄 轉換格式: {input_file} -> {output_file}")
    
    # 讀取原始資料
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 讀取原始考題檔案以取得完整資訊
    original_exam_file = PROJECT_ROOT / "results" / "exam_113_complete_llm_improved.json"
    with open(original_exam_file, 'r', encoding='utf-8') as f:
        exam_data = json.load(f)
    
    # 建立題目字典以便快速查找
    questions_dict = {}
    for question in exam_data.get('multiple_choice_section', {}).get('questions', []):
        questions_dict[str(question['question_number'])] = question
    
    # 建立選項匹配字典
    option_matches_dict = {}
    for option_match in data['option_matches']:
        q_id = option_match['question_id']
        option_letter = option_match['option_letter']
        
        if q_id not in option_matches_dict:
            option_matches_dict[q_id] = {}
        
        option_matches_dict[q_id][option_letter] = option_match
    
    # 轉換結果
    enhanced_results = {
        "metadata": {
            "exam_title": exam_data.get('exam_metadata', {}).get('exam_title', ''),
            "course_name": exam_data.get('exam_metadata', {}).get('course_name', ''),
            "exam_duration": exam_data.get('exam_metadata', {}).get('exam_duration', ''),
            "source_file": data['metadata']['source_file'],
            "embedding_model": data['metadata']['embedding_model'],
            "timestamp": data['metadata']['timestamp'],
            "total_law_articles": data['metadata']['total_law_articles'],
            "total_questions": len(data['question_matches']),
            "format_version": "enhanced_v1.0"
        },
        "questions": []
    }
    
    for question_match in data['question_matches']:
        q_id = question_match['question_id']
        
        # 取得原始題目資訊
        original_question = questions_dict.get(q_id, {})
        
        # 構建題目內容
        question_content_parts = [
            question_match['question_content'],
            format_similarity_text(question_match['matched_articles'])
        ]
        
        # 構建選項內容
        options_formatted = {}
        original_options = original_question.get('options', {})
        question_option_matches = option_matches_dict.get(q_id, {})
        
        for option_letter in ['A', 'B', 'C', 'D']:
            if option_letter in original_options and option_letter in question_option_matches:
                option_content = original_options[option_letter]
                option_match = question_option_matches[option_letter]
                
                options_formatted[option_letter] = [
                    option_content,
                    format_similarity_text(option_match['matched_articles'])
                ]
        
        # 構建最終結果
        enhanced_question = {
            "question_number": int(q_id),
            "content": question_content_parts,
            "options": options_formatted,
            "points": original_question.get('points', 2),
            "correct_answer": original_question.get('correct_answer', '')
        }
        
        enhanced_results["questions"].append(enhanced_question)
    
    # 保存結果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 格式轉換完成: {len(enhanced_results['questions'])} 題")
    print(f"💾 結果已保存: {output_file}")

def main():
    """主程式"""
    input_file = PROJECT_ROOT / "results" / "core_embedding_matches.json"
    output_file = PROJECT_ROOT / "results" / "core_embedding_enhanced_format.json"
    
    print("📝 核心 Embedding 結果格式轉換")
    print("=" * 50)
    print(f"輸入檔案: {input_file}")
    print(f"輸出檔案: {output_file}")
    print("=" * 50)
    
    if not input_file.exists():
        print(f"❌ 輸入檔案不存在: {input_file}")
        return
    
    try:
        convert_to_enhanced_format(str(input_file), str(output_file))
        
        # 顯示範例
        with open(output_file, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        print("\n📋 考題資訊:")
        print("-" * 50)
        metadata = sample_data['metadata']
        print(f"考試名稱: {metadata['exam_title']}")
        print(f"科目名稱: {metadata['course_name']}")
        print(f"考試時間: {metadata['exam_duration']}")
        print(f"題目總數: {metadata['total_questions']}")
        print(f"法條總數: {metadata['total_law_articles']}")
        print(f"處理時間: {metadata['timestamp']}")
        
        print("\n📋 格式範例 (第一題):")
        print("-" * 30)
        first_question = sample_data['questions'][0]
        print(f"題號: {first_question['question_number']}")
        print(f"題目: {first_question['content'][0][:50]}...")
        print(f"匹配: {first_question['content'][1]}")
        print(f"選項數: {len(first_question['options'])}")
        print(f"正確答案: {first_question['correct_answer']}")
        
    except Exception as e:
        print(f"❌ 轉換失敗: {e}")
        raise

if __name__ == "__main__":
    main()
