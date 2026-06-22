"""每週 Cron Job：呼叫網站的 /refresh 重新抓資料；若設了 SLACK_WEBHOOK，
把『30 天內即將開展』的展會推播出去（Slack 或 Discord webhook 皆可）。

需要的環境變數（在 Render Cron Job 設定）：
  SERVICE_URL    必填，你的網站網址，例如 https://japan-fb-tracker.onrender.com
  SLACK_WEBHOOK  選填，Slack/Discord incoming webhook URL；不設就只更新、不推播
"""
import os
import requests

SERVICE_URL = os.environ.get("SERVICE_URL", "").rstrip("/")
WEBHOOK = os.environ.get("SLACK_WEBHOOK", "").strip()


def main():
    if not SERVICE_URL:
        print("[skip] SERVICE_URL 未設定")
        return
    r = requests.get(f"{SERVICE_URL}/refresh", timeout=60)
    r.raise_for_status()
    data = r.json()
    print(f"[ok] 已更新 {data.get('updated')}，共 {data.get('count')} 檔")
    alerts = data.get("alerts", [])
    for a in alerts:
        print(f"   🔔 {a['name']}  {a['start']}  {a['daysUntil']} 天後")
    if WEBHOOK and alerts:
        lines = ["🔔 日本食品・飲料展　1 個月內即將開展："]
        lines += [f"• {a['name']}（{a['start']}，{a['daysUntil']} 天後開展）" for a in alerts]
        try:
            requests.post(WEBHOOK, json={"text": "\n".join(lines)}, timeout=15)
            print("[ok] 已推播通知")
        except Exception as e:
            print("[warn] 推播失敗：", e)


if __name__ == "__main__":
    main()
