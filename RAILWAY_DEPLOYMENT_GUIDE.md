# 🚅 Railway Deployment Guide (Free Tier + Chrome)

This guide deploys your OLX Scraper to **Railway.app**.
Railway is excellent because it supports Docker (for Chrome) and has a built-in Cron Scheduler.

---

## 🚀 Phase 1: Prepare Your Secrets (Do this first)

You need the **content** of your JSON files to paste into Railway.

1.  Open `config/client_secret.json` on your computer. Copy the **entire** text content.
2.  Open `config/google_token.json`. Copy the **entire** text content.

---

## 🛠️ Phase 2: Deploy to Railway

1.  **Sign Up/Login**: Go to [railway.app](https://railway.app) and login with GitHub.
2.  **New Project**: Click **"New Project"** → **"Deploy from GitHub repo"**.
3.  **Select Repository**: Choose your `olx-scraper-auto` repository.
4.  **Deploy Now**: Click "Deploy Now".

*The first build might fail or just sit there because we haven't added variables yet. That is normal.*

---

## 🔑 Phase 3: Configure Environment Variables

1.  Click on your project card in Railway.
2.  Go to the **"Variables"** tab.
3.  Add the following variables (Click "New Variable"):

| Variable Name | Value (Paste your actual data) |
|---|---|
| `GOOGLE_SHEET_ID` | Your Lahore Sheet ID |
| `KARACHI_SHEET_ID` | Your Karachi Sheet ID |
| `DISCORD_WEBHOOK_URL` | Your Discord Webhook Link |
| `GOOGLE_CLIENT_SECRET_CONTENT` | **(Paste the text from client_secret.json here)** |
| `GOOGLE_TOKEN_CONTENT` | **(Paste the text from google_token.json here)** |

*Railway will automatically trigger a redeploy when you add these.*

---

## ⏰ Phase 4: Schedule the Cron Jobs (Automatic Scraping)

Railway allows you to run "Cron Jobs" (Scheduled Tasks) separately from the web service.

1.  In your Project Dashboard, click **"New Service"** → **"Cron Job"**.
2.  **Lahore Scraper**:
    *   **Schedule**: `23 4 * * *` (Runs at 9:23 AM PKT)
        *   *(Note: Railway uses UTC time. 04:23 UTC = 09:23 PKT)*
    *   **Command**:
        ```bash
        export LOCATIONS="lahore" && python run_batch.py
        ```
3.  **Karachi Scraper**:
    *   Create **another** Cron Job service.
    *   **Schedule**: `37 4 * * *` (Runs at 9:37 AM PKT)
    *   **Command**:
        ```bash
        export LOCATIONS="karachi" && export GOOGLE_SHEET_ID=$KARACHI_SHEET_ID && python run_batch.py
        ```

---

## ✅ You Are Done!

- **Web Dashboard**: You can click the generic "Service" card to see your Web UI URL (if enabled).
- **Daily Scrapers**: The Cron Jobs will wake up automatically at 9:23 AM and 9:37 AM.
- **Logs**: You can click on any service to see the live logs while it runs.
