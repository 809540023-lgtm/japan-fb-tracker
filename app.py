"""日本食品・飲料展會追蹤 — FastAPI 網站
路由：
  /             儀表板首頁
  /api/events   JSON 資料（前端讀這支）
  /refresh      重新抓取並更新快取（Cron Job 每週呼叫）
"""
import pathlib
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import tracker

app = FastAPI(title="Japan F&B Exhibition Tracker")
BASE = pathlib.Path(__file__).parent
_cache: dict = {"data": None}


def refresh() -> dict:
    _cache["data"] = tracker.build()
    return _cache["data"]


@app.on_event("startup")
def _startup():
    refresh()


@app.get("/api/events")
def api_events():
    if _cache["data"] is None:
        refresh()
    return JSONResponse(_cache["data"])


@app.get("/refresh")
def do_refresh():
    d = refresh()
    return {
        "ok": True, "updated": d["updated"], "count": d["count"],
        "alerts": [{"name": a["name"], "start": a["start"], "daysUntil": a["daysUntil"]}
                   for a in d["alerts"]],
    }


@app.get("/")
def index():
    return FileResponse(BASE / "index.html")
