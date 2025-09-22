#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整法條複習筆記生成器
按法規分別生成完整的筆記檔案，包含所有條文和相關考題
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
import re

PROJECT_ROOT = Path(__file__).parent.parent

class CompleteLawNotesGenerator:
    """完整法條複習筆記生成器"""
    
    def __init__(self):
        self.law_articles = {}  # 法條資料
        self.exam_results = {}  # 考題結果
        self.law_question_mapping = defaultdict(list)  # 法條 -> 考題映射
        self.law_groups = defaultdict(list)  # 按法規分組
        
    def load_data(self):
        """載入所有資料"""
        print("📊 載入法條資料...")
        self._load_law_articles()
        
        print("📝 載入考題結果...")
        self._load_exam_results()
        
        print("🔗 建立法條-考題關聯...")
        self._build_law_question_mapping()
        
        print("📂 建立法規分組...")
        self._build_law_groups()
        
    def _load_law_articles(self):
        """載入法條資料"""
        csv_path = PROJECT_ROOT / "results" / "law_articles.csv"
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        for _, row in df.iterrows():
            article_id = f"{row['法規代碼']}-{row['條文主號']}"
            if row['條文次號'] > 0:
                article_id += f"-{row['條文次號']}"
            
            self.law_articles[article_id] = {
                "law_code": row['法規代碼'],
                "law_name": row['法規名稱'],
                "chapter_no": row['章節編號'],
                "chapter_title": row['章節標題'],
                "article_no_main": row['條文主號'],
                "article_no_sub": row['條文次號'],
                "article_title": row.get('條文標題', ''),
                "content": row['條文完整內容'],
                "category": row.get('法規類別', ''),
                "authority": row.get('主管機關', ''),
                "revision_date": row.get('修正日期（民國）', '')
            }
    
    def _load_exam_results(self):
        """載入考題結果"""
        results_path = PROJECT_ROOT / "results" / "core_embedding_enhanced_format.json"
        
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.exam_results = data
    
    def _build_law_question_mapping(self):
        """建立法條與考題的關聯"""
        questions = self.exam_results.get('questions', [])
        
        for question in questions:
            q_num = question['question_number']
            
            # 處理題目本身的法條匹配
            question_law_match = self._extract_law_reference(question['content'][1])
            if question_law_match:
                self.law_question_mapping[question_law_match].append({
                    'type': 'question',
                    'question_number': q_num,
                    'content': question['content'][0],
                    'correct_answer': question['correct_answer'],
                    'points': question['points'],
                    'options': question['options']
                })
            
            # 處理各選項的法條匹配
            for option_letter, option_data in question['options'].items():
                option_content = option_data[0]
                option_law_match = self._extract_law_reference(option_data[1])
                
                if option_law_match:
                    is_correct = (option_letter == question['correct_answer'])
                    
                    self.law_question_mapping[option_law_match].append({
                        'type': 'option',
                        'question_number': q_num,
                        'option_letter': option_letter,
                        'option_content': option_content,
                        'is_correct': is_correct,
                        'question_content': question['content'][0],
                        'all_options': question['options'],
                        'correct_answer': question['correct_answer'],
                        'points': question['points'],
                        'law_reference': option_data[1]
                    })
    
    def _extract_law_reference(self, match_text: str) -> str:
        """從匹配文字中提取法條代碼"""
        if not match_text or '第' not in match_text or '條' not in match_text:
            return None
        
        # 根據法規名稱對應代碼 (必須與 CSV 中的法規代碼完全一致)
        law_name_mapping = {
            '不動產經紀業管理條例': 'REA-ACT',
            '不動產經紀業管理條例施行細則': 'REA-RULES', 
            '公寓大廈管理條例': 'CMCA',
            '消費者保護法': 'CPA',
            '公平交易法': 'FTA'
        }
        
        # 找出法規名稱和條號
        for law_name, law_code in law_name_mapping.items():
            if law_name in match_text:
                # 提取條號
                match = re.search(r'第(\d+)條', match_text)
                if match:
                    article_no = match.group(1)
                    return f"{law_code}-{article_no}"
        
        return None
    
    def _build_law_groups(self):
        """建立法規分組"""
        for article_id, article_data in self.law_articles.items():
            law_name = article_data['law_name']
            self.law_groups[law_name].append((article_id, article_data))
        
        # 按條號排序
        for law_name in self.law_groups:
            self.law_groups[law_name].sort(key=lambda x: (x[1]['chapter_no'], x[1]['article_no_main'], x[1]['article_no_sub']))
    
    def generate_all_notes(self):
        """生成所有法規的筆記"""
        print("📝 開始生成完整法條筆記...")
        
        notes_dir = PROJECT_ROOT / "results" / "法條筆記"
        notes_dir.mkdir(exist_ok=True)
        
        for law_name in sorted(self.law_groups.keys()):
            output_path = notes_dir / f"{law_name}_複習筆記.md"
            self._generate_law_note(law_name, str(output_path))
        
        # 生成總覽檔案
        self._generate_overview(notes_dir / "法條複習筆記總覽.md")
        
        print(f"✅ 所有筆記已生成完成: {notes_dir}")
    
    def _generate_law_note(self, law_name: str, output_path: str):
        """生成單一法規的筆記"""
        articles = self.law_groups[law_name]
        
        # 取得考試基本資訊
        metadata = self.exam_results.get('metadata', {})
        exam_year = self._extract_year_from_title(metadata.get('exam_title', ''))
        course_name = metadata.get('course_name', '')
        
        markdown_content = self._generate_law_header(law_name, exam_year, course_name)
        
        # 按章節分組
        chapter_groups = defaultdict(list)
        for article_id, article_data in articles:
            chapter_key = (article_data['chapter_no'], article_data['chapter_title'])
            chapter_groups[chapter_key].append((article_id, article_data))
        
        # 生成各章節內容
        for chapter_key in sorted(chapter_groups.keys()):
            chapter_no, chapter_title = chapter_key
            chapter_articles = chapter_groups[chapter_key]
            markdown_content += self._generate_chapter_section(chapter_no, chapter_title, chapter_articles, exam_year, course_name)
        
        # 生成統計資訊
        markdown_content += self._generate_law_statistics(law_name, articles)
        
        # 儲存檔案
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"📄 已生成: {law_name}_複習筆記.md")
    
    def _generate_law_header(self, law_name: str, exam_year: str, course_name: str) -> str:
        """生成法規筆記標題"""
        metadata = self.exam_results.get('metadata', {})
        
        header = f"""# 📚 {law_name} 複習筆記

## 📋 基本資訊
- **法規名稱**: {law_name}
- **考試年度**: {exam_year}
- **考試科目**: {course_name}
- **分析時間**: {metadata.get('timestamp', '')}
- **分析模型**: {metadata.get('embedding_model', '')}

---

## 📖 使用說明

本筆記包含 **{law_name}** 的完整條文內容及相關考題：

- 🎯 **完整條文**: 包含所有條文，不論是否有考題對應
- ✅ **正確選項**: 標示為正確答案的選項
- ❌ **錯誤選項**: 標示為錯誤答案的選項
- 📝 **考題標籤**: 標示年份和科目
- 🔗 **法條引用**: 各選項參照的法條出處

---

"""
        return header
    
    def _generate_chapter_section(self, chapter_no: int, chapter_title: str, articles: List[tuple], exam_year: str, course_name: str) -> str:
        """生成章節內容"""
        content = f"\n## 📖 第{chapter_no}章 {chapter_title}\n\n"
        
        for article_id, article_data in articles:
            content += self._generate_article_section(article_id, article_data, exam_year, course_name)
        
        return content
    
    def _generate_article_section(self, article_id: str, article_data: Dict, exam_year: str, course_name: str) -> str:
        """生成單一法條的完整章節"""
        article_no = article_data['article_no_main']
        if article_data['article_no_sub'] > 0:
            article_no = f"{article_no}-{article_data['article_no_sub']}"
        
        content = f"\n### 📋 第 {article_no} 條"
        
        # 加入條文標題（如果有）
        if article_data.get('article_title') and article_data['article_title'].strip():
            content += f" {article_data['article_title']}"
        
        content += "\n\n"
        
        # 法條內容
        content += f"**條文內容:**\n\n"
        content += f"> {article_data['content']}\n\n"
        
        # 檢查是否有相關考題
        related_questions = self.law_question_mapping.get(article_id, [])
        
        if related_questions:
            content += f"**📝 相關考題:**\n\n"
            content += self._generate_related_questions(related_questions, exam_year, course_name)
        else:
            content += f"**📝 相關考題:**\n\n"
            content += f"🔸 **無對應考題**\n\n"
        
        content += "---\n\n"
        return content
    
    def _generate_related_questions(self, related_questions: List[Dict], exam_year: str, course_name: str) -> str:
        """生成相關考題內容"""
        content = ""
        
        # 按題號分組
        question_groups = defaultdict(list)
        for item in related_questions:
            question_groups[item['question_number']].append(item)
        
        for q_num in sorted(question_groups.keys()):
            items = question_groups[q_num]
            content += self._generate_complete_question(q_num, items, exam_year, course_name)
        
        return content
    
    def _generate_complete_question(self, q_num: int, items: List[Dict], exam_year: str, course_name: str) -> str:
        """生成完整題目內容"""
        content = f"\n#### 🎯 第 {q_num} 題 `{exam_year}年 {course_name}`\n\n"
        
        # 取得完整題目資訊
        question_item = None
        option_items = []
        
        for item in items:
            if item['type'] == 'question':
                question_item = item
            else:
                option_items.append(item)
        
        # 如果沒有question_item，從option_item中取得完整資訊
        if not question_item and option_items:
            first_option = option_items[0]
            question_content = first_option['question_content']
            all_options = first_option['all_options']
            correct_answer = first_option['correct_answer']
            points = first_option['points']
        else:
            question_content = question_item['content']
            all_options = question_item['options']
            correct_answer = question_item['correct_answer']
            points = question_item['points']
        
        # 顯示題目
        content += f"**題目:**\n{question_content}\n\n"
        
        # 顯示所有選項
        content += f"**選項:**\n\n"
        for option_letter in ['A', 'B', 'C', 'D']:
            if option_letter in all_options:
                option_text = all_options[option_letter][0]
                option_law_ref = all_options[option_letter][1]
                
                # 判斷是否為正確答案
                status_icon = "✅" if option_letter == correct_answer else "❌"
                
                content += f"- **{option_letter}** {status_icon}: {option_text}\n"
                content += f"  - 📖 *參照法條: {option_law_ref}*\n\n"
        
        content += f"**✅ 正確答案:** {correct_answer} ({points} 分)\n\n"
        
        # 標示本條文在此題中的關聯性
        related_options = [item for item in option_items if item['question_number'] == q_num]
        if related_options:
            content += f"**🔗 本條文關聯:**\n"
            for item in related_options:
                status = "正確答案" if item['is_correct'] else "錯誤選項"
                content += f"- 選項 {item['option_letter']} ({status}): {item['option_content'][:50]}...\n"
            content += "\n"
        
        return content
    
    def _generate_law_statistics(self, law_name: str, articles: List[tuple]) -> str:
        """生成法規統計資訊"""
        content = "\n## 📊 統計資訊\n\n"
        
        # 計算有考題關聯的法條數量
        related_count = 0
        total_count = len(articles)
        
        for article_id, _ in articles:
            if article_id in self.law_question_mapping:
                related_count += 1
        
        content += f"**條文統計:**\n"
        content += f"- 總條文數: {total_count} 條\n"
        content += f"- 有考題關聯: {related_count} 條\n"
        content += f"- 關聯比例: {related_count/total_count*100:.1f}%\n\n"
        
        # 章節統計
        chapter_stats = defaultdict(int)
        chapter_related_stats = defaultdict(int)
        
        for article_id, article_data in articles:
            chapter_title = article_data['chapter_title']
            chapter_stats[chapter_title] += 1
            if article_id in self.law_question_mapping:
                chapter_related_stats[chapter_title] += 1
        
        content += f"**章節統計:**\n"
        for chapter_title in sorted(chapter_stats.keys()):
            total = chapter_stats[chapter_title]
            related = chapter_related_stats.get(chapter_title, 0)
            percentage = related/total*100 if total > 0 else 0
            content += f"- {chapter_title}: {related}/{total} 條 ({percentage:.1f}%)\n"
        
        return content
    
    def _generate_overview(self, output_path: str):
        """生成總覽檔案"""
        metadata = self.exam_results.get('metadata', {})
        exam_year = self._extract_year_from_title(metadata.get('exam_title', ''))
        
        content = f"""# 📚 {exam_year}年不動產經紀相關法規 複習筆記總覽

## 📋 考試資訊
- **考試名稱**: {metadata.get('exam_title', '')}
- **科目名稱**: {metadata.get('course_name', '')}
- **考試時間**: {metadata.get('exam_duration', '')}
- **分析時間**: {metadata.get('timestamp', '')}

---

## 📖 法規列表

"""
        
        for law_name in sorted(self.law_groups.keys()):
            articles = self.law_groups[law_name]
            related_count = sum(1 for article_id, _ in articles if article_id in self.law_question_mapping)
            total_count = len(articles)
            percentage = related_count/total_count*100 if total_count > 0 else 0
            
            content += f"### 📖 [{law_name}](./{law_name}_複習筆記.md)\n\n"
            content += f"- **總條文數**: {total_count} 條\n"
            content += f"- **有考題關聯**: {related_count} 條 ({percentage:.1f}%)\n"
            content += f"- **筆記檔案**: `{law_name}_複習筆記.md`\n\n"
        
        # 整體統計
        total_articles = len(self.law_articles)
        total_related = len(self.law_question_mapping)
        overall_percentage = total_related/total_articles*100 if total_articles > 0 else 0
        
        content += f"""
## 📊 整體統計

- **法規數量**: {len(self.law_groups)} 部
- **總條文數**: {total_articles} 條
- **有考題關聯**: {total_related} 條
- **整體關聯比例**: {overall_percentage:.1f}%
- **考題總數**: {metadata.get('total_questions', 0)} 題

---

## 🎯 使用建議

1. **按法規複習**: 點擊上方連結進入各法規的完整筆記
2. **重點條文**: 優先複習有考題關聯的條文
3. **完整學習**: 所有條文都已包含，建議完整閱讀
4. **考題練習**: 每條有關聯的法條都附有完整考題

"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"📄 已生成總覽: 法條複習筆記總覽.md")
    
    def _extract_year_from_title(self, title: str) -> str:
        """從考試標題中提取年份"""
        match = re.search(r'(\d{3})年', title)
        return match.group(1) if match else "113"

def main():
    """主程式"""
    print("📚 完整法條複習筆記生成器")
    print("=" * 50)
    
    try:
        # 建立生成器
        generator = CompleteLawNotesGenerator()
        
        # 載入資料
        generator.load_data()
        
        # 生成所有筆記
        generator.generate_all_notes()
        
        print(f"\n🎉 所有筆記生成完成！")
        
        # 顯示統計
        total_laws = len(generator.law_groups)
        total_articles = len(generator.law_articles)
        related_articles = len(generator.law_question_mapping)
        
        print(f"📊 生成統計:")
        print(f"   - 法規數量: {total_laws} 部")
        print(f"   - 總條文數: {total_articles} 條")
        print(f"   - 有考題關聯: {related_articles} 條")
        print(f"   - 關聯比例: {related_articles/total_articles*100:.1f}%")
        
    except Exception as e:
        print(f"❌ 生成失敗: {e}")
        raise

if __name__ == "__main__":
    main()
