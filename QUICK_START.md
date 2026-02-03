# 🚀 Quick Start Guide - Multi-Location Scraper

## Installation & Setup

### 1. Install Dependencies

```bash
cd "c:\Users\mutee\Downloads\OLXify - Copy"
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python run.py
```

The browser will automatically open to `http://127.0.0.1:5000`

---

## Using the Multi-Location Feature

### Step 1: Select Locations

On the dashboard, you'll see 4 location checkboxes:

```
┌─────────────────────────────────────────┐
│  Select Locations (50 listings each)    │
│  [✓ Select All Locations]               │
│                                         │
│  ☑ 📍 Johar Town    ☑ 📍 Model Town    │
│  ☑ 📍 Valencia Town ☑ 📍 Askari        │
└─────────────────────────────────────────┘
```

**Options:**
- Check individual locations you want to scrape
- Click "Select All Locations" to select/deselect all
- At least 1 location must be selected

---

### Step 2: Configure Settings

**Max Pages per Location:**
- Default: 3 pages
- Range: 1-10 pages
- Each page contains ~24 listings
- Scraper stops at 50 listings even if more pages set

**Fetch Contact Information:**
- ☑ Checked: Opens browser for login, fetches phone numbers
- ☐ Unchecked: Scrapes only public listing data

---

### Step 3: Start Scraping

Click **"🚀 Start Scraping"** button

**What happens:**
1. Button disabled, shows spinner
2. Progress log starts updating in real-time
3. For each selected location:
   - Loads pages until 50 listings found
   - Extracts full details (concurrent)
   - Shows progress: "📍 Location: Processed X/50..."
4. Exports to TSV + JSON + Google Sheets
5. Button re-enabled when complete

---

## Progress Log Examples

### Scraping 2 Locations:

```
10:30:15  🧹 Cleaned up 2 old local file(s)
10:30:16  Selected locations: Johar Town, Model Town
10:30:16  Starting: max_pages=3, listings_per_location=50
10:30:17  📍 Johar Town: Starting scrape (target: 50 listings)...
10:30:18  📍 Johar Town: Page 1/3...
10:30:21  Found 24 listings
10:30:22  📍 Johar Town: Page 2/3...
10:30:25  Found 24 listings
10:30:26  📍 Johar Town: Page 3/3...
10:30:29  Found 24 listings
10:30:30  📍 Johar Town: Reached target of 50 listings.
10:30:31  📍 Johar Town: Collected 50 listings. Fetching details...
10:31:15  📍 Johar Town: Processed 5/50 listings...
10:32:00  📍 Johar Town: Processed 10/50 listings...
...
10:33:45  📍 Johar Town: Processed 50/50 listings...
10:33:46  ✅ Johar Town: Completed! 50 listings scraped.

10:33:47  📍 Model Town: Starting scrape (target: 50 listings)...
10:33:48  📍 Model Town: Page 1/3...
...
10:36:30  ✅ Model Town: Completed! 50 listings scraped.

10:36:31  🎉 All locations complete! Total: 100 listings from 2 location(s).
10:36:32  Exporting to TSV...
10:36:35  Exporting to Google Sheets...
10:36:40  ✅ Added to Google Sheets!
10:36:41  🎉 Complete! 100 listings exported to TSV + Google Sheets!
```

---

## Output Files

### Location

```
c:\Users\mutee\Downloads\OLXify - Copy\output\
```

### Files Created

```
olx_lahore_2026-02-03.tsv     ← Main output (tab-separated)
olx_lahore_2026-02-03.json    ← Same data (JSON format)
```

### File Format (TSV)

```
Ad ID    Title               Price      Location      Scraped_Location  Location_Key
1234567  Honda City 2020     25 Lacs    Johar Town    Johar Town        johar_town
1234568  Toyota Corolla...   30 Lacs    Model Town    Model Town        model_town
```

### New Columns

- **Scraped_Location:** Human-readable location name (e.g., "Johar Town")
- **Location_Key:** Internal location ID (e.g., "johar_town")

---

## Download Results

1. Scroll to **"Output Files"** section
2. Click **"↻ Refresh"** to update file list
3. Click **"Download"** button next to desired file

**Google Sheets:**
- Check "Google Sheets Auto-Export" card for status
- If configured, data automatically uploads after each scrape

---

## Expected Results

### 1 Location Selected (e.g., Johar Town)
- **Listings:** 50
- **Time:** 3-5 minutes
- **File Size:** ~200 KB (TSV)

### 2 Locations Selected
- **Listings:** 100
- **Time:** 6-10 minutes
- **File Size:** ~400 KB (TSV)

### 4 Locations Selected (All)
- **Listings:** 200
- **Time:** 12-20 minutes
- **File Size:** ~800 KB (TSV)

*Times vary based on network speed and contact fetching*

---

## Troubleshooting

### Issue: No locations shown
**Fix:** Refresh browser, check console for errors

### Issue: Scraper finds <50 listings
**Reason:** That location has fewer listings available
**Action:** Normal behavior, scraper collects what's available

### Issue: "No valid locations selected"
**Fix:** Check at least one location checkbox

### Issue: Contact fetching fails
**Fix:** Ensure you log in when browser opens, check cookies saved

### Issue: Google Sheets not auto-exporting
**Fix:** 
1. Check `config/client_secret.json` exists
2. Look at "Google Sheets Auto-Export" card for setup instructions
3. See `app/google_sheets.py` for configuration

---

## Tips & Best Practices

### Optimize Scraping Speed
1. **Disable Contact Fetching:** Saves 1-2 minutes per location
2. **Reduce Max Pages:** Set to 2-3 (usually enough for 50 listings)
3. **Select Fewer Locations:** Start with 1-2 for testing

### Avoid Detection
1. **Don't Run Too Often:** Wait 30+ minutes between scrapes
2. **Use Reasonable Limits:** Stick to 50 per location
3. **Enable Contact Fetch Sparingly:** Requires login, more detectable

### Data Quality
1. **Verify Exports:** Open TSV in Excel/Google Sheets
2. **Check Duplicates:** Same Ad ID = duplicate
3. **Monitor Progress Log:** Watch for errors/warnings

---

## Advanced Configuration

### Add New Location

Edit `app/config.py`:

```python
LOCATIONS_CONFIG = {
    # ... existing locations ...
    
    "dha_phase_5": {
        "name": "DHA Phase 5",
        "url": "https://www.olx.com.pk/dha-phase-5_g5000XXX/cars_c84",
        "enabled": True,
    },
}
```

Restart server to see new location in UI.

### Change Per-Location Limit

Edit `app/config.py`:

```python
class ScraperConfig:
    LISTINGS_PER_LOCATION: int = 100  # Change from 50
```

### Increase Concurrent Workers

Edit `app/config.py`:

```python
class ScraperConfig:
    DETAIL_WORKERS: int = 5  # Change from 3 (faster but more resource-intensive)
```

---

## Keyboard Shortcuts

- **Ctrl+C** in terminal: Stop server
- **F5** in browser: Refresh page
- **Ctrl+Shift+R**: Hard refresh (clear cache)

---

## Support & Documentation

📖 **Complete Analysis:** See `PROJECT_ANALYSIS.md`  
📝 **Update Details:** See `MULTI_LOCATION_UPDATE.md`  
🐛 **Report Issues:** Check progress log for error messages  

---

## Summary

**🎯 Purpose:** Scrape 50 car listings from each selected Lahore location  
**🚀 Usage:** Select locations → Set pages → Click start  
**📊 Output:** TSV + JSON files with location metadata  
**⏱️ Time:** ~3-5 minutes per location  
**✅ Status:** Production ready, fully tested  

---

**Happy Scraping! 🚗💨**
