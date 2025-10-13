"""
數據服務層
負責從 JSON 檔案讀取和處理數據
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from collections import defaultdict
from backend.models.schemas import (
    ReportSummary, ReportDetail, LawSummary, LawDetail,
    StatsResponse, Question, Option, ArticleMatch, ReportMetadata
)


class DataService:
    """數據服務類"""

    def __init__(self, data_dir: Path):
        """
        初始化數據服務

        Args:
            data_dir: embedded_results 資料夾路徑
        """
        self.data_dir = data_dir
        self._cache: Dict[str, Any] = {}

    def get_all_reports(self) -> List[ReportSummary]:
        """獲取所有報告摘要列表"""
        reports = []

        for json_file in self.data_dir.glob("*_mapped_embedded.json"):
            # 解析檔案名：113190_1301_民法概要_mapped_embedded.json
            stem = json_file.stem  # 去掉 .json
            parts = stem.replace("_mapped_embedded", "").split("_")

            if len(parts) >= 3:
                year_code = parts[0]  # 113190
                year = year_code[:3]  # 113
                subject = parts[2]    # 民法概要
                report_id = f"{parts[0]}_{parts[1]}_{parts[2]}"

                # 讀取檔案獲取題數
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get("metadata", {})

                    reports.append(ReportSummary(
                        report_id=report_id,
                        year=year,
                        subject=subject,
                        total_questions=metadata.get("total_questions", 0),
                        total_options=metadata.get("total_options_processed", 0)
                    ))

        # 按年份降序排序
        reports.sort(key=lambda x: x.year, reverse=True)
        return reports

    def get_report_detail(self, report_id: str) -> Optional[ReportDetail]:
        """
        獲取特定報告的完整數據

        Args:
            report_id: 報告 ID，如 "113190_1301_民法概要"

        Returns:
            ReportDetail 或 None
        """
        # 查找對應的 JSON 檔案
        json_file = self.data_dir / f"{report_id}_mapped_embedded.json"

        if not json_file.exists():
            return None

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 轉換為 Pydantic 模型
        metadata = ReportMetadata(**data["metadata"])

        questions = []
        for q_data in data.get("question_matches", []):
            options = []
            for opt_data in q_data.get("options", []):
                # 處理 matched_articles，過濾掉 NaN 值
                matched_articles = []
                for art_data in opt_data.get("matched_articles", []):
                    # 清理 NaN 值
                    cleaned_art = {k: v for k, v in art_data.items() if v == v}  # 過濾 NaN
                    if "chapter_title" in cleaned_art and str(cleaned_art["chapter_title"]) == "nan":
                        del cleaned_art["chapter_title"]
                    if "authority" in cleaned_art and str(cleaned_art["authority"]) == "nan":
                        del cleaned_art["authority"]

                    matched_articles.append(ArticleMatch(**cleaned_art))

                options.append(Option(
                    option_letter=opt_data["option_letter"],
                    option_text=opt_data["option_text"],
                    is_correct_answer=opt_data["is_correct_answer"],
                    matched_articles=matched_articles
                ))

            questions.append(Question(
                question_number=q_data["question_number"],
                question_text=q_data["question_text"],
                correct_answer=q_data["correct_answer"],
                options=options
            ))

        return ReportDetail(metadata=metadata, questions=questions)

    def get_all_laws(self) -> List[LawSummary]:
        """
        獲取所有法條摘要（按法條聚合）
        用於首頁的法條卡片展示

        Returns:
            按匹配次數降序排列的法條列表
        """
        law_dict: Dict[str, Dict[str, Any]] = {}

        # 遍歷所有報告
        for json_file in self.data_dir.glob("*_mapped_embedded.json"):
            report_id = json_file.stem.replace("_mapped_embedded", "")

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 統計每個法條的出現次數
            for question in data.get("question_matches", []):
                for option in question.get("options", []):
                    for article in option.get("matched_articles", []):
                        law_id = article.get("id")
                        if not law_id:
                            continue

                        if law_id not in law_dict:
                            law_dict[law_id] = {
                                "law_id": law_id,
                                "law_code": article.get("law_code", ""),
                                "law_name": article.get("law_name", ""),
                                "article_no": f"第 {article.get('article_no_main', 0)} 條",
                                "category": article.get("category", ""),
                                "matched_count": 0,
                                "related_reports": set()
                            }

                        law_dict[law_id]["matched_count"] += 1
                        law_dict[law_id]["related_reports"].add(report_id)

        # 轉換為 LawSummary 列表
        laws = []
        for law_data in law_dict.values():
            law_data["related_reports"] = list(law_data["related_reports"])
            laws.append(LawSummary(**law_data))

        # 按匹配次數降序排序
        laws.sort(key=lambda x: x.matched_count, reverse=True)
        return laws

    def get_law_detail(self, law_id: str) -> Optional[LawDetail]:
        """
        獲取特定法條的詳細資料和所有相關題目

        Args:
            law_id: 法條 ID，如 "CPLA-12"

        Returns:
            LawDetail 或 None
        """
        law_info = None
        related_questions = []

        # 遍歷所有報告，找出包含此法條的題目
        for json_file in self.data_dir.glob("*_mapped_embedded.json"):
            report_id = json_file.stem.replace("_mapped_embedded", "")

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for question in data.get("question_matches", []):
                for option in question.get("options", []):
                    for article in option.get("matched_articles", []):
                        if article.get("id") == law_id:
                            # 保存法條基本資訊（第一次遇到時）
                            if law_info is None:
                                law_info = {
                                    "law_id": law_id,
                                    "law_code": article.get("law_code", ""),
                                    "law_name": article.get("law_name", ""),
                                    "article_no": f"第 {article.get('article_no_main', 0)} 條",
                                    "content": article.get("content", ""),
                                    "category": article.get("category", ""),
                                    "matched_count": 0
                                }

                            # 記錄相關題目
                            related_questions.append({
                                "report_id": report_id,
                                "question_number": question.get("question_number"),
                                "question_text": question.get("question_text", ""),
                                "option_letter": option.get("option_letter", ""),
                                "option_text": option.get("option_text", ""),
                                "similarity": article.get("similarity", 0.0)
                            })

        if law_info is None:
            return None

        law_info["matched_count"] = len(related_questions)
        law_info["related_questions"] = related_questions

        return LawDetail(**law_info)

    def get_stats(self) -> StatsResponse:
        """獲取統計資訊"""
        reports = self.get_all_reports()
        laws = self.get_all_laws()

        years = sorted(list(set(r.year for r in reports)), reverse=True)
        subjects = sorted(list(set(r.subject for r in reports)))
        total_questions = sum(r.total_questions for r in reports)

        return StatsResponse(
            total_reports=len(reports),
            total_questions=total_questions,
            total_laws=len(laws),
            years=years,
            subjects=subjects
        )
