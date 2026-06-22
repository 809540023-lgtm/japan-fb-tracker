"""
日本食品・飲料展會追蹤 — 資料邏輯
- EVENTS: 人工維護的展會主清單（新展會在這裡加一筆即可）
- build(): 計算倒數天數、自動移除已結束的展會、(盡力)用 JFEX Algolia 補上即時參展商數
"""
from __future__ import annotations
import datetime as _dt
import requests

# ── 展會主清單 ───────────────────────────────────────────────
# 要新增展會：複製一筆，填 name/start/end/venue/url，dir 是參展商名錄(可留空)。
# 日期格式一律 YYYY-MM-DD。已結束的展會會自動隱藏，不必手動刪。
EVENTS = [
    {
        "name": "JFEX 夏 / 日本食品輸出EXPO",
        "start": "2026-06-24", "end": "2026-06-26",
        "venue": "東京 Big Sight",
        "url": "https://www.jfex.jp/hub/en-gb.html",
        "dir": "https://www.jfex.jp/sum/en-gb/search/2026m125/directory.html",
        "note": "國際食品・飲料商談Week（JFEX／日本食品輸出EXPO／Food LogiX）",
        # 可選：JFEX 該屆的 Algolia 設定，用來即時抓參展商數
        "algolia": {
            "app": "XD0U5M6Y4R",
            "key": "d5cd7d4ec26134ff4a34d736a7f9ad47",
            "index": "evt-1e41fde3-876f-4998-b93a-23a318a58f19-index",
            "edition": "eve-1dfca304-652d-4c4a-a0c4-a182127adc34",
        },
    },
    {"name": "CAFERES JAPAN 2026", "start": "2026-08-04", "end": "2026-08-06",
     "venue": "東京 Big Sight", "url": "https://caferes.jp/en/", "dir": "",
     "note": "咖啡・烘焙・甜點業最大展"},
    {"name": "日本國際水產展（28th）", "start": "2026-08-19", "end": "2026-08-20",
     "venue": "東京 Big Sight", "url": "https://10times.com/japan-seafood-technology", "dir": "",
     "note": "Japan Int'l Seafood & Technology Expo"},
    {"name": "Hi Japan 健康原料展", "start": "2026-10-14", "end": "2026-10-16",
     "venue": "東京 Big Sight", "url": "https://www.figlobal.com/japan/en/home.html", "dir": "",
     "note": "Health Ingredients Japan"},
    {"name": "JFEX 冬 / 日本食品輸出EXPO", "start": "2026-11-11", "end": "2026-11-13",
     "venue": "東京 Big Sight", "url": "https://www.jfex.jp/hub/en-gb.html", "dir": "",
     "note": "國際食品・飲料商談Week（秋季場）"},
    {"name": "超市展 SMTS 2027", "start": "2027-02-17", "end": "2027-02-19",
     "venue": "幕張 Messe（千葉）", "url": "https://www.smts.jp/en/", "dir": "",
     "note": "Supermarket Trade Show"},
    {"name": "FOODEX JAPAN 2027", "start": "2027-03-09", "end": "2027-03-12",
     "venue": "東京 Big Sight", "url": "https://foodex.jma.or.jp/en/", "dir": "",
     "note": "第52屆 國際食品飲料展（亞洲最大）"},
]


def _algolia_count(cfg: dict) -> int | None:
    """盡力抓 JFEX 該屆參展商數；失敗就回 None，不影響整體。"""
    try:
        host = f"https://{cfg['app'].lower()}-dsn.algolia.net"
        url = (f"{host}/1/indexes/{cfg['index']}/query"
               f"?x-algolia-application-id={cfg['app']}&x-algolia-api-key={cfg['key']}")
        flt = (f"recordType:exhibitor AND locale:en-gb "
               f"AND eventEditionId:{cfg['edition']}")
        r = requests.post(url, json={"params": f"query=&hitsPerPage=0&filters={flt}"}, timeout=8)
        if r.ok:
            return int(r.json().get("nbHits"))
    except Exception:
        pass
    return None


def build(today: _dt.date | None = None) -> dict:
    today = today or _dt.date.today()
    out = []
    for e in EVENTS:
        s = _dt.date.fromisoformat(e["start"])
        en = _dt.date.fromisoformat(e["end"])
        if en < today:
            continue  # 已結束，隱藏
        diff = (s - today).days
        if s <= today <= en:
            status = "live"
        elif 0 <= diff <= 30:
            status = "soon"
        else:
            status = "future"
        rec = {k: e.get(k, "") for k in ("name", "start", "end", "venue", "url", "dir", "note")}
        rec["daysUntil"] = diff
        rec["status"] = status
        if e.get("algolia"):
            c = _algolia_count(e["algolia"])
            if c is not None:
                rec["exhibitors"] = c
        out.append(rec)
    out.sort(key=lambda r: r["start"])
    alerts = [r for r in out if r["status"] in ("live", "soon")]
    return {"updated": today.isoformat(), "count": len(out), "events": out, "alerts": alerts}


if __name__ == "__main__":
    import json
    print(json.dumps(build(), ensure_ascii=False, indent=2))
