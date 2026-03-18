# 🚗 OLXify

**High-performance OLX car listings scraper with automated Google Sheets export.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-4.15+-green.svg)](https://selenium.dev)
[![Flask](https://img.shields.io/badge/Flask-3.0+-red.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

- 🔍 **Smart Scraping** - Extracts car listings from OLX Pakistan (Lahore)
- 📞 **Contact Fetching** - Automatically retrieves seller phone numbers & WhatsApp
- 📊 **Google Sheets Sync** - One-click export directly to your spreadsheet
- ⚡ **Optimized Speed** - Fast scraping with anti-detection measures
- 🔐 **Session Persistence** - Login once, run automated forever
- 🌐 **Premium Web UI** - Beautiful dark-mode dashboard

---

## 🖥️ Screenshots

### Dashboard
*Premium dark-mode interface with real-time progress tracking*

### Auto-Export
*Data automatically syncs to Google Sheets after each scrape*

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/olxify.git
cd olxify
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python run.py
```

### 4. Open in browser
```
http://127.0.0.1:5000
```

---

## Karachi Manual Control Dashboard (Vercel)

- Karachi workflow can be run manually with area selection from a secure single-admin dashboard.
- Lahore automation remains independent.
- Setup guide: `VERCEL_DASHBOARD_GUIDE.md`

---

## 📋 Configuration

### OLX Login (One-Time)
1. First scrape with "Fetch Contacts" enabled opens browser
2. Login to OLX manually
3. Cookies saved for future runs (7 days validity)

### Google Sheets (One-Time Setup)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Google Sheets API
3. Create OAuth credentials (Desktop app)
4. Download JSON → Rename to `client_secret.json`
5. Place in project root folder
6. First export opens browser for Google login
7. Fully automated after that!

---

## 📁 Project Structure

```
olxify/
├── run.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── client_secret.json      # Google OAuth credentials (you provide)
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── driver.py           # Chrome WebDriver management
│   ├── scraper.py          # Core scraping logic
│   ├── contact_fetcher.py  # Contact info fetcher
│   ├── exporter.py         # TSV/JSON export
│   ├── cookies.py          # Session persistence
│   ├── google_sheets.py    # Google Sheets integration
│   └── web.py              # Flask web server
├── templates/
│   └── index.html          # Web UI
├── static/                 # Static assets
└── output/                 # Generated TSV/JSON files
```

---

## ⚙️ Settings

Edit `app/config.py` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_MAX_LISTINGS` | 50 | Maximum listings to scrape |
| `DETAIL_WORKERS` | 3 | Parallel scraping threads |
| `GOOGLE_SHEET_ID` | Your ID | Target spreadsheet |

---

## 🔒 Security

- ✅ No credentials stored in code
- ✅ Cookies encrypted locally
- ✅ OAuth tokens auto-refresh
- ✅ Anti-detection measures built-in

---

## 📦 Dependencies

- `Flask` - Web framework
- `Selenium` - Browser automation
- `BeautifulSoup4` - HTML parsing
- `google-api-python-client` - Google Sheets API
- `requests` - HTTP requests

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Please respect OLX's Terms of Service and use responsibly. The author is not responsible for any misuse of this software.

---

## 🌟 Star History

If you find this useful, please give it a star! ⭐

---

**Made with ❤️ for the Pakistani car market**
