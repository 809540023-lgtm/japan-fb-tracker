"""日本食品・飲料展會追蹤 — FastAPI 網站
路由：
  /             儀表板首頁
  /api/events   JSON 資料（前端讀這支）
  /refresh      重新抓取並更新快取（Cron Job 每週呼叫）
"""
import pathlib
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import tracker

app = FastAPI(title="Japan F&B Exhibition Tracker")
BASE = pathlib.Path(__file__).parent

# 6 小時 TTL 快取：避免每次載入都打 JFEX Algolia API，
# 但又能讓倒數天數每天自動更新（免費方案休眠後冷啟動也會重算）。
_TTL = 6 * 3600
_cache: dict = {"data": None, "ts": 0.0}


def refresh() -> dict:
    _cache["data"] = tracker.build()
    _cache["ts"] = time.time()
    return _cache["data"]


def get_data() -> dict:
    if _cache["data"] is None or (time.time() - _cache["ts"]) > _TTL:
        refresh()
    return _cache["data"]


@app.on_event("startup")
def _startup():
    refresh()


@app.get("/api/events")
def api_events():
    return JSONResponse(get_data())


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
