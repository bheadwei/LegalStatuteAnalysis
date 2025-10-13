#!/usr/bin/env python3
"""
FastAPI 後端 API 服務
提供法條匹配數據的 REST API

啟動方式：
    cd /home/bheadwei/LegalStatuteAnalysis
    python backend/api/main.py

    或使用 uvicorn:
    uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import uvicorn

from backend.models.schemas import (
    ReportSummary, ReportDetail, LawSummary, LawDetail, StatsResponse
)
from backend.services.data_service import DataService


# ========== 配置 ==========
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "output" / "embedded_results"
FRONTEND_DIR = BASE_DIR / "frontend"

# ========== FastAPI 應用初始化 ==========
app = FastAPI(
    title="法條智能匹配系統 API",
    description="提供法律考試題目與法條智能匹配結果的 REST API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ========== CORS 設定（允許前端跨域請求）==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制具體域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 數據服務初始化 ==========
data_service = DataService(DATA_DIR)


# ========== API 端點 ==========

@app.get("/api/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "data_dir_exists": DATA_DIR.exists(),
        "frontend_dir": str(FRONTEND_DIR),
        "frontend_dir_exists": FRONTEND_DIR.exists()
    }


@app.get("/api/stats", response_model=StatsResponse)
async def get_statistics():
    """
    獲取統計資訊

    Returns:
        統計資訊，包含總報告數、總題數、涉及法條數等
    """
    return data_service.get_stats()


@app.get("/api/reports", response_model=List[ReportSummary])
async def get_all_reports():
    """
    獲取所有報告列表

    Returns:
        報告摘要列表，按年份降序排列
    """
    return data_service.get_all_reports()


@app.get("/api/report/{report_id}", response_model=ReportDetail)
async def get_report_detail(
    report_id: str = PathParam(..., description="報告 ID，如 113190_1301_民法概要")
):
    """
    獲取特定報告的完整數據

    Args:
        report_id: 報告 ID

    Returns:
        報告詳細數據，包含所有題目和選項的法條匹配結果

    Raises:
        HTTPException: 404 若報告不存在
    """
    report = data_service.get_report_detail(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail=f"報告 {report_id} 不存在")
    return report


@app.get("/api/laws", response_model=List[LawSummary])
async def get_all_laws():
    """
    獲取所有法條摘要列表（按法條聚合）

    用於首頁的法條卡片展示

    Returns:
        法條摘要列表，按匹配次數降序排列
    """
    return data_service.get_all_laws()


@app.get("/api/law/{law_id}", response_model=LawDetail)
async def get_law_detail(
    law_id: str = PathParam(..., description="法條 ID，如 CPLA-12")
):
    """
    獲取特定法條的詳細資料和所有相關題目

    Args:
        law_id: 法條 ID

    Returns:
        法條詳細資料，包含法條內容和所有匹配的題目

    Raises:
        HTTPException: 404 若法條不存在
    """
    law = data_service.get_law_detail(law_id)
    if law is None:
        raise HTTPException(status_code=404, detail=f"法條 {law_id} 不存在")
    return law


# ========== 靜態檔案服務（前端） ==========

@app.get("/")
async def serve_frontend_index():
    """提供前端首頁"""
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="前端檔案不存在")
    return FileResponse(index_file)


@app.get("/question.html")
async def serve_frontend_question():
    """提供前端題目頁面"""
    question_file = FRONTEND_DIR / "question.html"
    if not question_file.exists():
        raise HTTPException(status_code=404, detail="前端檔案不存在")
    return FileResponse(question_file)


# 掛載靜態檔案目錄（CSS/JS）
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


# ========== 啟動函式 ==========
def main():
    """啟動 Web 伺服器"""
    print("=" * 70)
    print("🚀 法條智能匹配系統 - 前後端分離版")
    print("=" * 70)
    print(f"📁 數據目錄: {DATA_DIR}")
    print(f"📁 前端目錄: {FRONTEND_DIR}")
    print(f"🌐 前端網址: http://localhost:8000")
    print(f"📊 API 文檔: http://localhost:8000/api/docs")
    print(f"💡 停止服務: Ctrl+C")
    print("=" * 70)

    # 檢查目錄
    if not DATA_DIR.exists():
        print(f"❌ 錯誤: 數據目錄不存在 - {DATA_DIR}")
        return

    if not FRONTEND_DIR.exists():
        print(f"❌ 錯誤: 前端目錄不存在 - {FRONTEND_DIR}")
        return

    # 統計報告數量
    report_count = len(list(DATA_DIR.glob("*_mapped_embedded.json")))
    print(f"✅ 找到 {report_count} 個報告檔案")
    print()

    # 啟動伺服器
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True  # 開發模式自動重載
    )


if __name__ == "__main__":
    main()
