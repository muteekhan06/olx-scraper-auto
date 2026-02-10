# ☁️ OLXify: Oracle Cloud Always Free Deployment

Your scraper will run on Oracle's cloud **FOREVER for FREE**.
No tricks, no expiration, no charges.

---

## 📋 What You Get (Free Forever)

- 1 Ubuntu Server (1 CPU, 1GB RAM)
- 200GB Storage
- Runs 24/7/365
- Your scraper fires at **exactly** 9:00 AM PKT every day

---

## 🚀 Phase 1: Create Oracle Cloud Account (5 minutes)

1. Go to: **[cloud.oracle.com/free](https://www.oracle.com/cloud/free/)**
2. Click **"Start for free"**
3. Fill in your details:
   - **Country**: Pakistan
   - **Name**: Your name
   - **Email**: Your email
   - **Home Region**: Choose **"UAE East (Abu Dhabi)"** or **"India South (Hyderabad)"** — pick whichever is closest to Pakistan for low latency
4. **Verify Email** (check inbox, click link)
5. **Add Card**: Enter your debit/credit card.
   - ⚠️ They will place a **temporary hold of ~$1** which is refunded immediately.
   - 🔒 They will **NEVER charge** you. The card is only to prove you are a real person.
6. Click **"Start My Free Trial"**

You now have an Oracle Cloud account.

---

## 🖥️ Phase 2: Launch Your Server (5 minutes)

1. Log into [cloud.oracle.com](https://cloud.oracle.com)
2. In the search bar at the top, type **"Instances"** and click on **"Instances (Compute)"**
3. Click the blue **"Create Instance"** button.
4. Configure it:

   | Setting | Value |
   |---|---|
   | **Name** | `olx-scraper` |
   | **Image** | Click "Edit" → Select **"Canonical Ubuntu 22.04"** |
   | **Shape** | `VM.Standard.E2.1.Micro` (it says "Always Free eligible") |
   | **Networking** | Leave defaults (it creates a VCN for you) |

5. **SSH Key** (Very Important):
   - Select **"Generate a key pair for me"**
   - Click **"Save Private Key"** — downloads a `.key` file
   - **SAVE THIS FILE SAFELY.** You need it to connect.

6. Click **"Create"** and wait ~60 seconds for it to turn **RUNNING** (green).

7. **Copy the Public IP Address** shown on the instance details page.
   - It looks like: `129.154.xxx.xxx`

---

## 🔗 Phase 3: Connect to Your Server

### Option A: Using Cloud Shell (Easiest - No Downloads)
1. In Oracle Cloud Console, click the **"Cloud Shell"** icon (top right, looks like `>_`).
2. A terminal opens at the bottom of your browser.
3. You need to upload your SSH key first:
   - Click the **gear icon** in Cloud Shell → **Upload**
   - Upload the `.key` file you downloaded.
4. Run these commands:
   ```bash
   chmod 600 ~/your-key-file.key
   ssh -i ~/your-key-file.key ubuntu@YOUR_PUBLIC_IP
   ```
   - Replace `your-key-file.key` with the actual filename.
   - Replace `YOUR_PUBLIC_IP` with the IP you copied.
5. Type `yes` when asked about fingerprint.

### Option B: Using PowerShell (From Your PC)
1. Open PowerShell on your Windows PC.
2. Navigate to where you saved the `.key` file:
   ```powershell
   ssh -i "C:\Users\mutee\Downloads\your-key-file.key" ubuntu@YOUR_PUBLIC_IP
   ```

You are now inside your server! 🎉

---

## ⚙️ Phase 4: Install Everything (Copy-Paste, 3 minutes)

Run these commands one by one in the server terminal:

### Step 1: Download your code
```bash
git clone https://github.com/muteekhan06/olx-scraper-auto.git
cd olx-scraper-auto
```

### Step 2: Run the automated setup
```bash
chmod +x setup_ec2.sh
./setup_ec2.sh
```
Wait for it to finish (2-3 minutes). You'll see `✅ Setup Complete!`

---

## 🔑 Phase 5: Add Your Secrets (2 minutes)

### 1. Create client_secret.json
```bash
nano config/client_secret.json
```
- Paste the **entire content** of your local `config/client_secret.json` file.
- Press **Ctrl+X**, then **Y**, then **Enter** to save.

### 2. Create google_token.json
```bash
nano config/google_token.json
```
- Paste the **entire content** of your local `config/google_token.json` file.
- Press **Ctrl+X**, then **Y**, then **Enter** to save.

### 3. Create the environment file
```bash
nano .env
```
Paste these 3 lines (replace with YOUR actual values):
```
GOOGLE_SHEET_ID=YOUR_LAHORE_SHEET_ID
KARACHI_SHEET_ID=1dhXrAWpnbDvsqdqoS3yCi1X9tUTg6R6POZrR7rrq46k
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/1468257130761945355/njML49_cu2SyEgpM_qF72n13Xc1YHQyf6iriENZXF9jvsjaNOGbBx2-444WPYYbACloA
```
- Press **Ctrl+X**, then **Y**, then **Enter** to save.

---

## ⏰ Phase 6: Schedule the Daily Runs (1 minute)

This is the "alarm clock" that fires your scraper every morning.

### 1. Set the server timezone to Pakistan
```bash
sudo timedatectl set-timezone Asia/Karachi
```

### 2. Open the scheduler
```bash
crontab -e
```
If it asks you to choose an editor, type **1** (for nano) and press Enter.

### 3. Scroll to the very bottom and paste these lines:
```
# ==========================================
# OLXify Automated Scrapers
# ==========================================

# Lahore Scraper - Runs at 9:00 AM PKT
0 9 * * * cd /home/ubuntu/olx-scraper-auto && export $(cat .env | xargs) && LOCATIONS="lahore" python3 run_batch.py >> /home/ubuntu/lahore.log 2>&1

# Karachi Scraper - Runs at 9:00 AM PKT
0 9 * * * cd /home/ubuntu/olx-scraper-auto && export $(cat .env | xargs) && LOCATIONS="karachi" GOOGLE_SHEET_ID="$KARACHI_SHEET_ID" python3 run_batch.py >> /home/ubuntu/karachi.log 2>&1
```

Press **Ctrl+X**, then **Y**, then **Enter** to save.

---

## ✅ Phase 7: Test It Right Now!

### Test Lahore Scraper:
```bash
cd /home/ubuntu/olx-scraper-auto
export $(cat .env | xargs)
LOCATIONS="lahore" python3 run_batch.py
```

### Test Karachi Scraper:
```bash
cd /home/ubuntu/olx-scraper-auto
export $(cat .env | xargs)
LOCATIONS="karachi" GOOGLE_SHEET_ID="$KARACHI_SHEET_ID" python3 run_batch.py
```

If you see the progress logs and get a Discord notification, **everything is perfect!**

---

## 📊 Useful Commands (Cheat Sheet)

| What | Command |
|---|---|
| Check Lahore logs | `tail -50 /home/ubuntu/lahore.log` |
| Check Karachi logs | `tail -50 /home/ubuntu/karachi.log` |
| Check if cron is running | `crontab -l` |
| Update code from GitHub | `cd /home/ubuntu/olx-scraper-auto && git pull` |
| Restart the server | `sudo reboot` |
| Check server uptime | `uptime` |

---

## 🔒 Important Notes

1. **Your server runs 24/7.** You never need to turn it on. It's always ready.
2. **No charges. Ever.** Oracle's "Always Free" tier does not expire.
3. **If you lose your SSH key**, you can still access via Oracle Cloud Shell.
4. **To update your scraper code**, just push to GitHub and run `git pull` on the server.

🎉 **Congratulations! You now have a lifetime, free, perfectly reliable scraping server.**
