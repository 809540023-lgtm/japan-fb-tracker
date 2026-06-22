# 日本食品・飲料展會追蹤（GitHub + Render 部署版）

一個會自動更新的展會追蹤網站：
- **網站**：公開網址，列出日本即將舉辦的食品・飲料實體展，自動算倒數天數、標示 30 天內即將開展者。
- **每週 Cron Job**：每週一自動重新抓資料（移除已結束、刷新 JFEX 參展商數），可選擇推播「1 個月內即將開展」到 Slack/Discord。

---

## 檔案結構
```
japan-fb-tracker/
├── app.py            # FastAPI 網站（/、/api/events、/refresh）
├── tracker.py        # 展會主清單 + 計算/過濾邏輯（新增展會改這裡）
├── refresh_job.py    # 每週 Cron Job：呼叫 /refresh，可選推播
├── requirements.txt
├── render.yaml       # Render 藍圖：自動建立網站 + Cron Job
├── static/index.html # 儀表板前端
└── README.md
```

---

## 部署步驟（不需要 git 指令，全程在瀏覽器點）

### 1) 放到 GitHub
1. 登入 https://github.com → 右上「+」→ **New repository** → 取名 `japan-fb-tracker` → Create。
2. 進到空 repo 頁 → **Add file → Upload files** → 把本資料夾內**所有檔案（含 static 資料夾）**拖進去 → **Commit changes**。
   - （要保留資料夾結構：把整個 `japan-fb-tracker` 內容拖入；`static/index.html` 要在 `static/` 底下。）

### 2) 部署到 Render
1. 登入 https://render.com（可用 GitHub 帳號登入）。
2. **New + → Blueprint** → 選你剛建的 repo → Render 會讀 `render.yaml`，自動建立**網站**和**Cron Job** → **Apply**。
3. 等網站部署完成，會得到網址，例如 `https://japan-fb-tracker.onrender.com` → 打開就是儀表板。

### 3) 讓每週自動更新生效
1. Render → 進入 **japan-fb-tracker-weekly**（Cron Job）→ **Environment** →
   - `SERVICE_URL` = 你上一步拿到的網站網址（例：`https://japan-fb-tracker.onrender.com`）
   - （可選）`SLACK_WEBHOOK` = 你的 Slack 或 Discord incoming webhook，用來收即將開展通知
2. 存檔。之後每週一會自動跑 `refresh_job.py`：更新資料、(若設了 webhook) 推播提醒。
   - 想立刻測試：在 Cron Job 頁按 **Run now**。

> 小提醒：Render 免費方案的網站閒置久了會休眠；每週 Cron 呼叫 `/refresh` 會把它喚醒並刷新，所以排程時間點資料一定是新的。若要永遠不休眠可升級付費方案。

---

## 怎麼新增 / 修改展會
打開 `tracker.py`，在 `EVENTS` 清單複製一筆改內容即可（`start`/`end` 用 `YYYY-MM-DD`）。
已結束的展會（end 日期已過）會自動隱藏，不必手動刪。改完 commit 到 GitHub，Render 會自動重新部署。

## 本機測試（選用）
```
pip install -r requirements.txt
uvicorn app:app --reload
# 開 http://localhost:8000
```

## 資料來源
JFEX／日本食品輸出EXPO、FOODEX JAPAN、CAFERES JAPAN、日本國際水產展、Hi Japan、
Supermarket Trade Show 等官方網站；JFEX 參展商數即時取自其公開 Algolia 檢索 API。
