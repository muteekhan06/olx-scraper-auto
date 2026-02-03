# ☁️ OLXify: Complete Cloud Automation Guide

This guide contains everything you need to run OLXify automatically in the cloud (GitHub Actions) for **FREE**, every single day at **9:00 AM PKT**.

---

## 🛠️ Part 1: Prerequisites (Do this ONCE)

You need 3 keys from your local project to give to the cloud robot.

### 1. Google Sheets ID
*   Open your Google Sheet in your browser.
*   Look at the URL: `https://docs.google.com/spreadsheets/d/1aBcDeFgHiJkLmNoPqrStUvWxYz/edit`
*   The ID is the long random part: `1aBcDeFgHiJkLmNoPqrStUvWxYz`
*   **Save this ID.**

### 2. Google Client Secret
*   Open the file: `config/client_secret.json` in your project folder.
*   Copy the **ENTIRE** content of this file.

### 3. Google Token
*   Open the file: `config/google_token.json` in your project folder.
*   Copy the **ENTIRE** content of this file.

*(Note: You do NOT need OLX cookies. The system uses advanced Guest Mode automatically.)*

---

## 🔔 Part 2: Setup Instant Mobile Alerts (Discord)

To get a "Ding!" on your phone when new leads arrive, we use Discord. It is faster and more reliable than email.

1.  **Download Discord** on your phone and Create a Free Account.
2.  **Create a Server**: Click the "**+**" icon on the left sidebar -> "Create My Own" -> "For me and my friends". Name it "OLX Leads".
3.  **Create a Webhook** (Do this on PC for ease):
    *   Right-click the "general" text channel.
    *   Click **Edit Channel** (Gear icon).
    *   Go to **Integrations** (left menu).
    *   Click **Webhooks**.
    *   Click **New Webhook**.
    *   Click on "Spidey Bot" (or whatever name it gives).
    *   **Change Name** to: `OLXify Bot`.
    *   Click **Copy Webhook URL**.
    *   **Save this URL.** It looks like: `https://discord.com/api/webhooks/1234.../AbCd...`

---

## ☁️ Part 3: Deploy to Cloud (GitHub)

1.  **Create Repo**: Go to GitHub.com -> Create a **New Repository**.
    *   Name: `olx-scraper-auto`
    *   Visibility: **Private** (Important!)
    *   Click **Create repository**.

2.  **Upload Code**:
    *   If you know Git: `git init`, `git add .`, `git commit -m "init"`, `git push...`
    *   If you don't know Git: Click "uploading an existing file" on GitHub, drag all your files there, and commit.

3.  **Add Secrets (The Most Important Step)**:
    *   Go to your Repo Settings -> **Secrets and variables** -> **Actions**.
    *   Click **New repository secret**.
    *   Add these 4 secrets EXACTLY as written below:

| Secret Name | Value to Paste |
| :--- | :--- |
| `GOOGLE_SHEET_ID` | The ID you saved in Part 1. |
| `GOOGLE_CLIENT_SECRET` | Content of `config/client_secret.json`. |
| `GOOGLE_TOKEN_JSON` | Content of `config/google_token.json`. |
| `DISCORD_WEBHOOK_URL` | The URL you copied in Part 2. |

---

## 🚀 Part 4: Test & Relax

### Test It Immediately
1.  Go to the **Actions** tab in your GitHub repository.
2.  Click on **OLX Daily Scraper** in the left sidebar.
3.  Click the **Run workflow** button (blue button on right).
4.  Wait 2-5 minutes.
5.  **Result**: 
    *   Check your Google Sheet: New rows will appear.
    *   Check your Phone: You will get a notification from Discord with the stats!

### Automatic Schedule
*   You don't need to do anything else.
*   The robot wakes up every day at **9:00 AM Pakistan Time** automatically.
*   It runs faithfully in the background, for free, forever.
