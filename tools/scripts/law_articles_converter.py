#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法規條文轉換工具 - 將Markdown格式的法規轉換為CSV
根據提供的PostgreSQL表結構生成對應的CSV數據
"""

import re
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ColumnConfig:
    """欄位配置"""
    name: str
    default_value: Any = None

class LawArticleConverter:
    """法規條文轉換器 - 中文欄位，自動擴展"""
    
    def __init__(self, config_file: Optional[str] = "law_config.json"):
        """
        初始化轉換器
        
        Args:
            config_file: 法規配置文件路徑，預設使用 law_config.json
        """
        self.law_definitions = self._load_law_definitions(config_file)
        self.columns = self._get_column_configs()
        
    def _load_law_definitions(self, config_file: Optional[str]) -> Dict[str, Dict[str, str]]:
        """載入法規定義 - 統一從 law_config.json 管理"""
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    law_defs = config.get('law_definitions', {})
                    logger.info(f"✅ 從配置文件載入 {len(law_defs)} 個法規定義: {config_file}")
                    return law_defs
            except Exception as e:
                logger.error(f"❌ 無法載入配置文件 {config_file}: {e}")
        
        # 如果配置文件不存在，給出明確錯誤提示
        logger.error(f"❌ 必須提供有效的配置文件: {config_file}")
        logger.error("💡 請確保 law_config.json 存在並包含 law_definitions 配置")
        return {}
    
    def _get_column_configs(self) -> List[ColumnConfig]:
        """取得欄位配置"""
        return [
            ColumnConfig('法規代碼'),
            ColumnConfig('法規名稱'),
            ColumnConfig('修正日期（民國）'),
            ColumnConfig('法規類別'),
            ColumnConfig('主管機關'),
            ColumnConfig('章節編號'),
            ColumnConfig('章節標題'),
            ColumnConfig('條文主號'),
            ColumnConfig('條文次號'),
            ColumnConfig('條文完整內容')
        ]
        
    def add_law_definition(self, filename: str, law_info: Dict[str, str]):
        """動態添加法規定義"""
        self.law_definitions[filename] = law_info
        logger.info(f"已添加法規定義: {filename}")
    
    def auto_detect_law_info(self, file_path: Path, content: str) -> Dict[str, str]:
        """自動檢測法規資訊"""
        filename = file_path.name
        
        # 從內容中提取法規名稱和修正日期
        law_name_match = re.search(r'法規名稱：(.+)', content)
        revision_date_match = re.search(r'修正日期：(.+)', content)
        
        # 自動生成法規代碼
        law_code = self._generate_law_code(filename)
        
        return {
            'law_code': law_code,
            'law_name': law_name_match.group(1).strip() if law_name_match else filename.replace('.md', ''),
            'revision_date_roc': revision_date_match.group(1).strip() if revision_date_match else '',
            'category': '自動檢測',
            'authority': '待確認'
        }
    
    def _generate_law_code(self, filename: str) -> str:
        """自動生成法規代碼"""
        name = filename.replace('.md', '')
        
        # 關鍵字映射
        keyword_mapping = {
            '不動產經紀': 'REA',
            '公寓大廈': 'CMCA', 
            '公平交易': 'FTA',
            '消費者保護': 'CPA',
            '施行細則': 'RULES',
            '管理條例': 'ACT',
            '管理辦法': 'REG'
        }
        
        code_parts = []
        for keyword, code in keyword_mapping.items():
            if keyword in name:
                code_parts.append(code)
        
        if code_parts:
            return '-'.join(code_parts)
        else:
            # 回退方案：使用檔名的前幾個字
            return 'AUTO-' + ''.join([c for c in name if c.isalnum()])[:6].upper()
        
    def parse_law_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """解析單個法規文件 - 支持自動檢測"""
        filename = file_path.name
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 優先使用已定義的法規資訊，否則自動檢測
        if filename in self.law_definitions:
            law_info = self.law_definitions[filename]
            logger.info(f"使用預定義法規資訊: {filename}")
        else:
            law_info = self.auto_detect_law_info(file_path, content)
            logger.info(f"自動檢測法規資訊: {filename} -> {law_info['law_code']}")
            # 將檢測到的資訊加入定義中，供後續使用
            self.law_definitions[filename] = law_info
        
        # 移除檔案最前面的法規名稱和修正日期行
        lines = content.split('\n')
        content_lines = []
        skip_next = False
        
        for line in lines:
            if skip_next and line.strip() == '':
                skip_next = False
                continue
            if line.startswith('法規名稱：'):
                skip_next = True
                continue
            if skip_next:
                continue
            content_lines.append(line)
        
        content = '\n'.join(content_lines)
        
        # 解析結構
        articles = []
        current_chapter = {'no': 1, 'title': '總則'}  # 預設章節
        
        # 先找出所有章節
        chapters = self._extract_chapters(content)
        
        # 如果沒有章節，使用預設章節
        if not chapters:
            chapters = [{'no': 1, 'title': '總則'}]
        
        # 解析條文
        articles = self._extract_articles(content, law_info, chapters)
        
        logger.info(f"解析 {filename}: {len(articles)} 條條文")
        return articles
    
    def _extract_chapters(self, content: str) -> List[Dict[str, Any]]:
        """提取章節資訊"""
        chapters = []
        
        # 匹配章節標題（支持中文數字和阿拉伯數字）
        patterns = [
            r'^# 第\s*(\d+)\s*章\s*(.+)$',  # 阿拉伯數字：第1章
            r'^# 第\s*([一二三四五六七八九十]+)\s*章\s*(.+)$'  # 中文數字：第一章
        ]
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            for i, pattern in enumerate(patterns):
                match = re.match(pattern, line)
                if match:
                    chapter_num_str = match.group(1).strip()
                    chapter_title = match.group(2).strip()
                    
                    # 簡化：直接使用順序編號
                    chapter_no = len(chapters) + 1
                    full_title = f'第{chapter_num_str}章 {chapter_title}'
                    
                    chapters.append({
                        'no': chapter_no,
                        'title': full_title
                    })
                    break
        
        return chapters
    
    def _extract_articles(self, content: str, law_info: Dict[str, str], 
                         chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取條文資訊"""
        articles = []
        
        # 分割內容，找出每一條
        lines = content.split('\n')
        current_chapter = chapters[0] if chapters else {'no': 1, 'title': '總則'}
        current_article = None
        current_text_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 檢查是否為章節標題
            chapter_match = re.match(r'^# 第\s*([一二三四五六七八九十\d]+)\s*章', line)
            if chapter_match:
                # 保存當前條文
                if current_article:
                    current_article['text_full'] = self._clean_article_text('\n'.join(current_text_lines))
                    articles.append(current_article)
                    current_article = None
                    current_text_lines = []
                
                # 簡化：根據章節出現順序更新當前章節
                chapter_index = len([c for c in chapters if 'used' in c]) if chapters else 0
                if chapter_index < len(chapters):
                    current_chapter = chapters[chapter_index]
                    current_chapter['used'] = True
                
                i += 1
                continue
            
            # 檢查是否為條文標題
            article_match = re.match(r'^# 第\s*(\d+(?:-\d+)?)\s*條(?:\s*(.*))?$', line)
            if article_match:
                # 保存前一條
                if current_article:
                    current_article['text_full'] = self._clean_article_text('\n'.join(current_text_lines))
                    articles.append(current_article)
                
                # 解析條號
                article_no_str = article_match.group(1)
                article_title = article_match.group(2) if article_match.group(2) else None
                
                if '-' in article_no_str:
                    main_no, sub_no = map(int, article_no_str.split('-'))
                else:
                    main_no = int(article_no_str)
                    sub_no = 0
                
                # 創建新的條文記錄
                current_article = {
                    'law_code': law_info['law_code'],
                    'law_name': law_info['law_name'],
                    'revision_date_roc': law_info['revision_date_roc'],
                    'category': law_info.get('category', ''),
                    'authority': law_info.get('authority', ''),
                    'chapter_no': current_chapter['no'],
                    'chapter_title': current_chapter['title'],
                    'article_no_main': main_no,
                    'article_no_sub': sub_no,
                    'title': article_title.strip() if article_title and article_title.strip() else None
                }
                current_text_lines = []
                i += 1
                continue
            
            # 如果在條文內容中，累積文字
            if current_article and line:
                # 跳過空行和純符號行
                if line and not re.match(r'^[=\-\*\#\s]*$', line):
                    current_text_lines.append(line)
            
            i += 1
        
        # 處理最後一條
        if current_article:
            current_article['text_full'] = self._clean_article_text('\n'.join(current_text_lines))
            articles.append(current_article)
        
        return articles
    
    def _clean_article_text(self, text: str) -> str:
        """清理條文內容"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not re.match(r'^[=\-\*\#\s]*$', line):
                # 移除行首的數字編號（如 1 、2 等）
                line = re.sub(r'^\d+\s+', '', line)
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    

    
    def convert_to_csv(self, input_dir: str, output_file: str):
        """轉換所有法規文件為CSV - 動態從配置文件獲取文件列表"""
        input_path = Path(input_dir)
        all_articles = []
        
        # 從配置文件動態獲取要處理的文件列表
        target_files = list(self.law_definitions.keys())
        
        if not target_files:
            logger.error("❌ 沒有找到要處理的法規文件配置")
            return
        
        logger.info(f"📋 將處理 {len(target_files)} 個法規文件")
        
        for filename in target_files:
            file_path = input_path / filename
            if file_path.exists():
                articles = self.parse_law_file(file_path)
                all_articles.extend(articles)
            else:
                logger.warning(f"⚠️ 文件不存在: {file_path}")
        
        # 寫入CSV
        self._write_csv(all_articles, output_file)
        
        logger.info(f"✅ 轉換完成！總共 {len(all_articles)} 條條文，輸出至 {output_file}")
    
    def _write_csv(self, articles: List[Dict[str, Any]], output_file: str):
        """寫入CSV文件 - 中文欄位名稱"""
        # 英文欄位到中文欄位映射（僅保留需要的欄位）
        field_mapping = {
            'law_code': '法規代碼',
            'law_name': '法規名稱', 
            'revision_date_roc': '修正日期（民國）',
            'category': '法規類別',
            'authority': '主管機關',
            'chapter_no': '章節編號',
            'chapter_title': '章節標題',
            'article_no_main': '條文主號',
            'article_no_sub': '條文次號',
            'text_full': '條文完整內容'
        }
        
        # 使用中文欄位名稱
        fieldnames = [config.name for config in self.columns]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                row = {}
                for config in self.columns:
                    chinese_name = config.name
                    # 反向查找英文欄位名
                    english_name = None
                    for eng, chi in field_mapping.items():
                        if chi == chinese_name:
                            english_name = eng
                            break
                    
                    if english_name:
                        # 一般欄位
                        row[chinese_name] = article.get(english_name, config.default_value or '')
                    else:
                        row[chinese_name] = config.default_value or ''
                
                writer.writerow(row)
        
        logger.info(f"CSV輸出完成 - 使用中文欄位名稱")
        logger.info(f"輸出欄位: {', '.join(fieldnames)}")

def main():
    """主函數"""
    print("🔧 法規條文轉換器 - 中文欄位，自動擴展")
    print("=" * 50)
    
    # 建立轉換器
    converter = LawArticleConverter()
    
    # 轉換法規文件
    output_file = "results/law_articles.csv"
    converter.convert_to_csv("results/mineru_batch", output_file)
    
    # 示範：動態添加新法規
    print("\n📊 示範: 動態添加新法規")
    converter.add_law_definition('土地法.md', {
        'law_code': 'LAND-ACT',
        'law_name': '土地法',
        'revision_date_roc': '民國 100 年 06 月 15 日',
        'category': '土地管理',
        'authority': '內政部'
    })
    
    print(f"\n✅ 法規條文轉換完成！")
    print(f"📁 輸出文件: {output_file}")
    print(f"📊 使用中文欄位名稱，可直接匯入中文資料庫")
    
    # 展示欄位配置
    print(f"\n🔗 輸出欄位 ({len(converter.columns)}個):")
    for i, config in enumerate(converter.columns, 1):
        print(f"   {i:2d}. {config.name}")
    
    print(f"\n🚀 功能特色:")
    print(f"   ✅ 中文欄位名稱")
    print(f"   ✅ 精簡欄位設計") 
    print(f"   ✅ 自動檢測法規資訊")
    print(f"   ✅ 動態添加新法規")
    print(f"   ✅ 智能代碼生成")
    print(f"   ✅ 完全中文化界面")

if __name__ == "__main__":
    main()
