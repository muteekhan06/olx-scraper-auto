"""
OLXify - Cloud Batch Runner
Run this script to execute the scraping pipeline without a GUI.
Ideal for GitHub Actions or Cron jobs.
"""

import os
import sys
import json
import requests
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import scraper and exporter functions
from app.scraper import scrape_listings
from app.contact_fetcher import fetch_contacts
from app.exporter import export_to_tsv, export_to_json, ensure_dir
from app.google_sheets import is_google_sheets_configured, export_to_google_sheets
from app.config import OUTPUT_CONFIG

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def send_notification(status_type, stats=None, error=None):
    """Send a premium notification to Discord."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if status_type == "start":
        color = 16776960 # Yellow
        title = "⏳ OLX Scraper Started"
        # stats might be just the location string here if we pass it carefully
        locs = stats.get("locations", "All") if stats else "Unknown"
        desc = f"Job initialized for locations: **{locs}**"
    elif status_type == "success":
        color = 65280  # Green
        title = "🚀 OLX Scraper Success"
        count = stats['count'] if stats else 0
        desc = f"**{count}** new leads added to your sheet!"
    else: # error
        color = 16711680  # Red
        title = "❌ OLX Scraper Failed"
        desc = f"**Error:** {error}"

    # Build the payload
    payload = {
        "embeds": [{
            "title": title,
            "description": desc,
            "color": color,
            "fields": [
                {"name": "📅 Date", "value": timestamp, "inline": True},
            ],
            "footer": {"text": "OLXify Automation • Free Cloud Runner"}
        }]
    }
    
    # Add Location field if available
    if stats and stats.get("locations"):
         payload["embeds"][0]["fields"].append(
             {"name": "📍 Locations", "value": stats.get("locations"), "inline": True}
         )
    
    # Add Sheet Link if available (only for success)
    if status_type == "success" and stats and stats.get("sheet_url"):
        payload["embeds"][0]["fields"].append(
            {"name": "📊 Google Sheet", "value": f"[Click to View]({stats['sheet_url']})", "inline": False}
        )

    try:
        requests.post(webhook_url, json=payload)
        log(f"🔔 {status_type.capitalize()} notification sent!")
    except Exception as e:
        log(f"⚠️ Failed to send notification: {e}")

def main():
    print("\n" + "=" * 50)
    print("  OLXify - Cloud Batch Runner")
    print("=" * 50)
    
    # Configuration
    MAX_PAGES = int(os.environ.get("MAX_PAGES", 5))
    MAX_LISTINGS = int(os.environ.get("MAX_LISTINGS", 50))
    LOCATIONS = os.environ.get("LOCATIONS", "all")
    
    stats = {
        "count": 0,
        "locations": LOCATIONS,
        "sheet_url": None
    }
    
    # Send Start Notification
    send_notification("start", stats)
    
    try:
        log(f"Starting batch job...")
        
        # Parse locations
        selected_locations = None
        if LOCATIONS.lower() == "lahore":
            from app.config import LOCATIONS_LAHORE
            selected_locations = list(LOCATIONS_LAHORE.keys())
            log("📍 Mode: Lahore City Only")
        elif LOCATIONS.lower() == "karachi":
            from app.config import LOCATIONS_KARACHI
            selected_locations = list(LOCATIONS_KARACHI.keys())
            log("📍 Mode: Karachi City Only")
        elif LOCATIONS.lower() != "all":
            selected_locations = [x.strip() for x in LOCATIONS.split(",") if x.strip()]
        else:
            log("📍 Mode: All Locations (Lahore + Karachi)")
        
        # 1. Scrape Listings
        log("Phase 1: Discovery (Scraping Listings & Details)")
        listings = scrape_listings(
            max_pages=MAX_PAGES,
            max_listings=MAX_LISTINGS,
            progress_callback=log,
            selected_locations=selected_locations
        )
        
        if not listings:
            log("❌ No listings found. Exiting.")
            send_notification("error", stats, error="No listings found on OLX.")
            return
        
        stats["count"] = len(listings)
        log(f"✅ Discovered {len(listings)} listings.")
        
        # 2. Fetch Contacts (Guest Mode)
        log("Phase 2: Contact Enrichment")
        try:
            listings = fetch_contacts(listings, progress_callback=log)
        except Exception as e:
            log(f"⚠️ Contact fetching had issues: {e}")
        
        # 3. Export to Files
        log("Phase 3: Exporting Data")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        filename = f"olx_cloud_{timestamp}"
        export_to_tsv(listings, filename)
        
        # 4. Export to Google Sheets
        if is_google_sheets_configured():
            log("Phase 4: Uploading to Google Sheets")
            sheet_id = OUTPUT_CONFIG.GOOGLE_SHEET_ID
            if sheet_id:
                url = export_to_google_sheets(
                    data=listings,
                    spreadsheet_id=sheet_id,
                    progress_callback=log
                )
                stats["sheet_url"] = url
                log(f"🎉 Success! Sheet updated: {url}")
        
        # Send Success Notification
        send_notification("success", stats)
        log("✅ Batch Job Complete.")

    except Exception as e:
        log(f"❌ Critical Error: {e}")
        send_notification("error", stats, error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
