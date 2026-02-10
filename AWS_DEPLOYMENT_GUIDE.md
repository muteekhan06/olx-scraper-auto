# ☁️ AWS EC2 ("Forever Server") Setup Guide

This guide moves your scraper from GitHub Actions to your own **AWS EC2 Server**. This guarantees it runs **exactly** when you want, with no waiting time.

---

## 🛠️ Phase 1: Launch Your Server (Free Tier)

1.  **Login to AWS Console**: [console.aws.amazon.com](https://console.aws.amazon.com)
2.  Search for **EC2** and click **Launch Instance**.
3.  **Name**: `OLX-Scraper-Bot`
4.  **OS Images**: Choose **Ubuntu** (Select "Ubuntu Server 24.04 LTS" or "22.04 LTS").
5.  **Instance Type**: `t2.micro` or `t3.micro` (Look for the "Free tier eligible" tag).
6.  **Key Pair**:
    *   Click "Create new key pair".
    *   Name it `olx-key`.
    *   Format: `.pem`.
    *   Download it and **Save it safely**.
7.  **Storage**: 8GB or 30GB (Free tier allows up to 30GB).
8.  Click **Launch Instance**.

---

## 🔗 Phase 2: Connect to Server

1.  Go to your EC2 Dashboard and click on your new instance.
2.  Click **Connect** (Top right).
3.  Go to the **EC2 Instance Connect** tab.
4.  Click **Connect** button (opens a terminal in your browser).
    *   *Alternatively, use SSH if you know how, but browser is easier.*

---

## ⚙️ Phase 3: Install & Setup (The Easy Way)

Copy and paste these commands into the black terminal window one by one:

### 1. Download Your Code
*(Replace the URL below with your actual repo URL if different)*
```bash
git clone https://github.com/muteekhan06/olx-scraper-auto.git
cd olx-scraper-auto
```

### 2. Run the Setup Script
I created this script to handle all the complex installation (Chrome, Python, etc.) for you.
```bash
chmod +x setup_ec2.sh
./setup_ec2.sh
```
*Wait for it to finish (approx 2-3 mins).*

---

## 🔑 Phase 4: Add Your Secrets

We need to create the credential files manually on your server.

### 1. Create client_secret.json
Run this command:
```bash
nano config/client_secret.json
```
*   Paste the content of your `client_secret.json` here.
*   Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 2. Create google_token.json
Run this command:
```bash
nano config/google_token.json
```
*   Paste the content of your `google_token.json` here.
*   Press `Ctrl+X`, then `Y`, then `Enter` to save.

### 3. Setup Environment Variables
Run this command to open your environment file:
```bash
nano .env
```
Paste these lines (Fill in your real values):
```text
GOOGLE_SHEET_ID=your_lahore_sheet_id_here
KARACHI_SHEET_ID=your_karachi_sheet_id_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```
*   Press `Ctrl+X`, then `Y`, then `Enter`.

---

## ⏰ Phase 5: Schedule the Automation (Cron)

This works like an alarm clock inside the server.

1.  Open the scheduler:
    ```bash
    crontab -e
    ```
    *(If it asks for a number, type `1` and Enter).*

2.  Scroll to the bottom and paste these two lines:

    ```bash
    # Lahore Scraper - 9:00 AM PKT (04:00 UTC)
    0 4 * * * cd /home/ubuntu/olx-scraper-auto && export $(cat .env | xargs) && export LOCATIONS="lahore" && python3 run_batch.py >> lahore.log 2>&1

    # Karachi Scraper - 9:00 AM PKT (04:00 UTC)
    0 4 * * * cd /home/ubuntu/olx-scraper-auto && export $(cat .env | xargs) && export LOCATIONS="karachi" && export GOOGLE_SHEET_ID=$KARACHI_SHEET_ID && python3 run_batch.py >> karachi.log 2>&1
    ```

3.  Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## ✅ You Are Done!

*   The server is on.
*   The code is installed.
*   The schedule is set for **exactly 9:00 AM PKT** (04:00 server time).
*   **To test it manually right now:**
    ```bash
    export $(cat .env | xargs) && export LOCATIONS="lahore" && python3 run_batch.py
    ```

Enjoy your lifetime* scraper!
*(Remember AWS Free Tier is 12 months free for new accounts).*
