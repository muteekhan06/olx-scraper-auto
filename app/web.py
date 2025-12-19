"""
Advanced Web Interface for OLX Scraper.
"""

import json
import os
import threading
from datetime import date, datetime
from queue import Queue

from flask import Flask, render_template, jsonify, request, send_file, Response
from flask_cors import CORS

from app.config import SCRAPER_CONFIG, OUTPUT_CONFIG
from app.scraper import scrape_listings
from app.contact_fetcher import fetch_contacts
from app.exporter import export_to_tsv, export_to_json, ensure_dir

app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

scraper_state = {
    "running": False,
    "phase": "idle",
    "progress": [],
    "result": None,
    "error": None,
    "started_at": None,
    "completed_at": None,
}

state_lock = threading.Lock()
progress_queue: Queue = Queue()


def add_progress(message: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = {"time": timestamp, "message": message}
    with state_lock:
        scraper_state["progress"].append(entry)
        if len(scraper_state["progress"]) > 100:
            scraper_state["progress"] = scraper_state["progress"][-100:]
    progress_queue.put(entry)


def run_scraper_task(max_pages: int, max_listings: int, fetch_contact_info: bool) -> None:
    global scraper_state
    try:
        with state_lock:
            scraper_state.update({
                "running": True, "phase": "scraping", "progress": [],
                "result": None, "error": None,
                "started_at": datetime.now().isoformat(), "completed_at": None,
            })
        
        add_progress(f"Starting: max_pages={max_pages}, max_listings={max_listings}")
        listings = scrape_listings(max_pages, max_listings, add_progress)
        
        if not listings:
            add_progress("No listings found.")
            with state_lock:
                scraper_state.update({"phase": "complete", "running": False, "completed_at": datetime.now().isoformat()})
            return
        
        add_progress(f"Scraped {len(listings)} listings.")
        
        if fetch_contact_info:
            with state_lock:
                scraper_state["phase"] = "fetching_contacts"
            add_progress("Fetching contact info...")
            listings = fetch_contacts(listings, add_progress)
        
        add_progress("Exporting to TSV...")
        filename = f"olx_lahore_{date.today().isoformat()}"
        tsv_path = export_to_tsv(listings, filename)
        json_path = export_to_json(listings, filename)
        
        # Auto-export to Google Sheets
        sheets_url = None
        try:
            from app.google_sheets import export_to_google_sheets, is_google_sheets_configured
            if is_google_sheets_configured():
                with state_lock:
                    scraper_state["phase"] = "exporting_sheets"
                add_progress("Exporting to Google Sheets...")
                sheets_url = export_to_google_sheets(
                    data=listings,
                    spreadsheet_id=OUTPUT_CONFIG.GOOGLE_SHEET_ID,
                    progress_callback=add_progress
                )
                add_progress(f"✅ Added to Google Sheets!")
            else:
                add_progress("Google Sheets not configured - skipping auto-export")
        except Exception as sheets_err:
            add_progress(f"Google Sheets export failed: {sheets_err}")
        
        with state_lock:
            scraper_state.update({
                "phase": "complete", "running": False,
                "completed_at": datetime.now().isoformat(),
                "result": {
                    "count": len(listings), 
                    "tsv_file": os.path.basename(tsv_path), 
                    "json_file": os.path.basename(json_path),
                    "sheets_url": sheets_url,
                },
            })
        add_progress(f"🎉 Complete! {len(listings)} listings exported to TSV + Google Sheets!")
        
    except Exception as e:
        add_progress(f"Error: {e}")
        with state_lock:
            scraper_state.update({"phase": "error", "running": False, "error": str(e), "completed_at": datetime.now().isoformat()})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    with state_lock:
        return jsonify(dict(scraper_state, progress=scraper_state["progress"][-20:]))


@app.route("/api/start", methods=["POST"])
def start_scraper():
    with state_lock:
        if scraper_state["running"]:
            return jsonify({"error": "Already running"}), 400
    
    data = request.get_json() or {}
    max_pages = max(1, min(50, int(data.get("max_pages", 5))))
    max_listings = max(1, min(500, int(data.get("max_listings", 100))))
    fetch_contact = bool(data.get("fetch_contact_info", True))
    
    threading.Thread(target=run_scraper_task, args=(max_pages, max_listings, fetch_contact), daemon=True).start()
    return jsonify({"message": "Started", "max_pages": max_pages, "max_listings": max_listings})


@app.route("/api/files")
def list_files():
    ensure_dir(OUTPUT_CONFIG.OUTPUT_DIR)
    files = []
    for name in os.listdir(OUTPUT_CONFIG.OUTPUT_DIR):
        if name.endswith((".tsv", ".json")):
            path = os.path.join(OUTPUT_CONFIG.OUTPUT_DIR, name)
            stat = os.stat(path)
            files.append({"name": name, "size": stat.st_size, "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()})
    files.sort(key=lambda x: x["modified"], reverse=True)
    return jsonify(files)


@app.route("/api/download/<filename>")
def download_file(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid"}), 400
    filepath = os.path.join(OUTPUT_CONFIG.OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Not found"}), 404
    return send_file(filepath, as_attachment=True)


@app.route("/api/stream")
def stream_progress():
    def generate():
        while True:
            try:
                entry = progress_queue.get(timeout=2.0)
                yield f"data: {json.dumps(entry)}\n\n"
            except:
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/google-sheets/status")
def google_sheets_status():
    """Check if Google Sheets integration is configured."""
    try:
        from app.google_sheets import is_google_sheets_configured, is_google_sheets_authenticated
        return jsonify({
            "configured": is_google_sheets_configured(),
            "authenticated": is_google_sheets_authenticated(),
        })
    except Exception as e:
        return jsonify({"configured": False, "authenticated": False, "error": str(e)})


@app.route("/api/google-sheets/export", methods=["POST"])
def export_to_sheets():
    """Export a file to Google Sheets."""
    try:
        from app.google_sheets import export_to_google_sheets, is_google_sheets_configured
        
        if not is_google_sheets_configured():
            return jsonify({"error": "Google Sheets not configured. See app/google_sheets.py for setup."}), 400
        
        data = request.get_json() or {}
        spreadsheet_id = data.get("spreadsheet_id", "").strip()
        filename = data.get("filename", "").strip()
        
        if not spreadsheet_id:
            return jsonify({"error": "spreadsheet_id is required"}), 400
        if not filename:
            return jsonify({"error": "filename is required"}), 400
        
        # Load the file
        filepath = os.path.join(OUTPUT_CONFIG.OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        # Load data from JSON file
        json_file = filename.replace(".tsv", ".json")
        json_path = os.path.join(OUTPUT_CONFIG.OUTPUT_DIR, json_file)
        
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                listings = json.load(f)
        else:
            return jsonify({"error": "JSON data file not found"}), 404
        
        # Export to Google Sheets
        sheet_url = export_to_google_sheets(
            data=listings,
            spreadsheet_id=spreadsheet_id,
            sheet_name=f"OLX {date.today().isoformat()}",
        )
        
        return jsonify({"success": True, "url": sheet_url})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_web_server(host="127.0.0.1", port=5000):
    ensure_dir(OUTPUT_CONFIG.OUTPUT_DIR)
    app.run(host=host, port=port, threaded=True)
