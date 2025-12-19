"""
OLXify - Main Entry Point
Run this file to start the web interface.
"""

import sys
import webbrowser
import time
import threading

from app.web import run_web_server


def open_browser():
    """Open browser after a short delay."""
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")


def main():
    print("\n" + "=" * 50)
    print("  OLXify - Lahore Car Listings")
    print("=" * 50)
    print("\n🚀 Starting web server...")
    print("📍 URL: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server.\n")
    
    # Open browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start server
    try:
        run_web_server(host="127.0.0.1", port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
