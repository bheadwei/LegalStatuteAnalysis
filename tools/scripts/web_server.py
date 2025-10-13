#!/usr/bin/env python3
"""
FastAPI Web 伺服器 - 用於提供法條匹配報告的 Web 介面

功能：
1. 提供靜態 HTML 報告瀏覽
2. 自動掃描報告目錄
3. 提供 REST API 查詢報告列表
4. 支援跨域請求（CORS）

啟動方式：
    python tools/scripts/web_server.py
    或
    uvicorn tools.scripts.web_server:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, JSONResponse
from pathlib import Path
import json
from typing import List, Dict
import uvicorn

# ========== 配置 ==========
BASE_DIR = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = BASE_DIR / "output" / "html_reports"

# ========== FastAPI 應用初始化 ==========
app = FastAPI(
    title="法條智能匹配系統",
    description="提供法律考試題目與法條智能匹配結果的瀏覽介面",
    version="1.0.0"
)

# ========== 路由定義 ==========

@app.get("/")
async def root():
    """根路徑 - 重定向到 index.html"""
    return RedirectResponse(url="/index.html")


@app.get("/api/reports")
async def list_reports() -> JSONResponse:
    """
    列出所有可用的報告

    Returns:
        JSONResponse: 包含報告列表的 JSON 響應
        [
            {
                "filename": "110180_1101_民法概要_mapped_embedded.html",
                "year": "110",
                "subject": "民法概要",
                "url": "/110180_1101_民法概要_mapped_embedded.html"
            },
            ...
        ]
    """
    if not REPORTS_DIR.exists():
        raise HTTPException(status_code=404, detail="報告目錄不存在")

    reports = []
    for html_file in REPORTS_DIR.glob("*.html"):
        if html_file.name == "index.html":
            continue

        # 解析檔案名稱：110180_1101_民法概要_mapped_embedded.html
        parts = html_file.stem.split("_")
        if len(parts) >= 3:
            year = parts[0][:3]  # 前3位是年份
            subject = parts[2]    # 科目名稱

            reports.append({
                "filename": html_file.name,
                "year": year,
                "subject": subject,
                "url": f"/{html_file.name}"
            })

    # 按年份和科目排序
    reports.sort(key=lambda x: (x["year"], x["subject"]), reverse=True)

    return JSONResponse(content={"reports": reports, "total": len(reports)})


@app.get("/api/stats")
async def get_statistics() -> JSONResponse:
    """
    獲取報告統計資訊

    Returns:
        JSONResponse: 統計資訊
    """
    if not REPORTS_DIR.exists():
        raise HTTPException(status_code=404, detail="報告目錄不存在")

    reports = list(REPORTS_DIR.glob("*_mapped_embedded.html"))
    years = set()
    subjects = set()

    for html_file in reports:
        parts = html_file.stem.split("_")
        if len(parts) >= 3:
            years.add(parts[0][:3])
            subjects.add(parts[2])

    return JSONResponse(content={
        "total_reports": len(reports),
        "years": sorted(list(years), reverse=True),
        "subjects": sorted(list(subjects)),
        "reports_dir": str(REPORTS_DIR)
    })


@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "reports_dir_exists": REPORTS_DIR.exists(),
        "reports_count": len(list(REPORTS_DIR.glob("*_mapped_embedded.html")))
    }


# ========== 靜態檔案服務 ==========
# 必須放在最後，否則會覆蓋其他路由
app.mount("/", StaticFiles(directory=str(REPORTS_DIR), html=True), name="static")


# ========== 啟動函式 ==========
def main():
    """啟動 Web 伺服器"""
    print("=" * 60)
    print("🚀 法條智能匹配系統 Web 伺服器")
    print("=" * 60)
    print(f"📁 報告目錄: {REPORTS_DIR}")
    print(f"🌐 訪問網址: http://localhost:8000")
    print(f"📊 API 文檔: http://localhost:8000/docs")
    print(f"💡 停止服務: Ctrl+C")
    print("=" * 60)

    # 檢查報告目錄是否存在
    if not REPORTS_DIR.exists():
        print(f"❌ 錯誤: 報告目錄不存在 - {REPORTS_DIR}")
        print("請先執行報告生成腳本")
        return

    # 統計報告數量
    report_count = len(list(REPORTS_DIR.glob("*_mapped_embedded.html")))
    print(f"✅ 找到 {report_count} 個報告檔案")
    print()

    # 啟動伺服器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()
