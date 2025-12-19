"""
Google Sheets Integration with OAuth2.
Login once via browser, then fully automated!

Setup (One-time, FREE):
1. Go to https://console.cloud.google.com/
2. Create a project (or use existing)
3. Go to APIs & Services > Enable APIs > Enable "Google Sheets API"
4. Go to APIs & Services > Credentials > Create Credentials > OAuth client ID
5. Select "Desktop app" as application type
6. Download the JSON and save as "client_secret.json" in project folder
7. Run the script - it will open browser for login ONCE
8. After that, it's fully automated!
"""

import json
import os
from datetime import date
from typing import Dict, List, Optional

from app.config import OUTPUT_CONFIG


# File paths
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "google_token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def is_google_sheets_configured() -> bool:
    """Check if Google Sheets OAuth is configured."""
    return os.path.exists(CLIENT_SECRET_FILE)


def is_google_sheets_authenticated() -> bool:
    """Check if we have valid saved tokens."""
    return os.path.exists(TOKEN_FILE)


def get_google_credentials():
    """Get or refresh Google OAuth credentials."""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise RuntimeError(
            "Required packages not installed. Run:\n"
            "pip install google-auth google-auth-oauthlib google-auth-httplib2"
        )
    
    if not os.path.exists(CLIENT_SECRET_FILE):
        raise FileNotFoundError(
            f"OAuth client file not found: {CLIENT_SECRET_FILE}\n"
            "Please download it from Google Cloud Console > Credentials > OAuth 2.0 Client IDs"
        )
    
    creds = None
    
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception:
            creds = None
    
    # If no valid creds, do OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        
        if not creds:
            # Need fresh login via browser
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        
        # Save token for next time
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    
    return creds


def get_sheets_service():
    """Get authenticated Google Sheets service."""
    try:
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "Required package not installed. Run:\n"
            "pip install google-api-python-client"
        )
    
    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)
    return service


def get_ordered_columns(data: List[Dict]) -> List[str]:
    """Get columns in preferred order, excluding unwanted ones."""
    all_keys: set = set()
    for row in data:
        all_keys.update(row.keys())
    
    all_keys -= set(OUTPUT_CONFIG.EXCLUDED_COLUMNS)
    
    ordered: List[str] = []
    for col in OUTPUT_CONFIG.COLUMN_ORDER:
        if col in all_keys:
            ordered.append(col)
            all_keys.remove(col)
    
    ordered.extend(sorted(all_keys))
    return ordered


def clean_value(v) -> str:
    """Clean a value for Google Sheets."""
    if v is None:
        return ""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    if isinstance(v, str):
        v = v.strip()
        if v.upper() == "N/A":
            return ""
        return v
    return str(v)


def export_to_google_sheets(
    data: List[Dict],
    spreadsheet_id: str,
    sheet_name: str = None,
    progress_callback=None,
) -> str:
    """
    Export data directly to Google Sheets.
    First time: Opens browser for Google login.
    After that: Fully automated!
    
    Args:
        data: List of dictionaries to export
        spreadsheet_id: The Google Sheet ID (from URL)
        sheet_name: Name of the worksheet (auto-generated if None)
        progress_callback: Optional callback for progress updates
        
    Returns:
        URL to the Google Sheet
    """
    if not sheet_name:
        # Format: "19-12-2025"
        sheet_name = date.today().strftime("%d-%m-%Y")
    
    if progress_callback:
        progress_callback("Connecting to Google Sheets...")
    
    service = get_sheets_service()
    
    # Check if sheet exists, create if not
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_names = [s["properties"]["title"] for s in spreadsheet.get("sheets", [])]
        
        if sheet_name not in sheet_names:
            # Create new sheet
            request = {
                "requests": [{
                    "addSheet": {
                        "properties": {"title": sheet_name}
                    }
                }]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request).execute()
            if progress_callback:
                progress_callback(f"Created new sheet: {sheet_name}")
        else:
            # Clear existing sheet
            range_name = f"'{sheet_name}'!A:ZZ"
            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id, range=range_name
            ).execute()
            if progress_callback:
                progress_callback(f"Cleared existing sheet: {sheet_name}")
                
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error accessing sheet: {e}")
        raise
    
    if not data:
        if progress_callback:
            progress_callback("No data to export")
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    
    # Get columns
    columns = get_ordered_columns(data)
    
    if progress_callback:
        progress_callback(f"Preparing {len(data)} rows with {len(columns)} columns...")
    
    # Build rows
    rows = [columns]  # Header row
    for item in data:
        row = []
        for col in columns:
            if col in OUTPUT_CONFIG.EXCLUDED_COLUMNS:
                continue
            val = item.get(col, "")
            row.append(clean_value(val))
        rows.append(row)
    
    # Write data
    if progress_callback:
        progress_callback(f"Uploading {len(rows)} rows...")
    
    range_name = f"'{sheet_name}'!A1"
    body = {"values": rows}
    
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    # Format header row (bold)
    try:
        # Get sheet ID
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        for s in spreadsheet.get("sheets", []):
            if s["properties"]["title"] == sheet_name:
                sheet_id = s["properties"]["sheetId"]
                break
        
        if sheet_id is not None:
            request = {
                "requests": [{
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {"bold": True}
                            }
                        },
                        "fields": "userEnteredFormat.textFormat.bold"
                    }
                }]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request).execute()
    except Exception:
        pass  # Formatting is optional
    
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    
    if progress_callback:
        progress_callback(f"✅ Exported {len(data)} rows to Google Sheets!")
    
    return url


def delete_google_token():
    """Delete saved Google token (for re-authentication)."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
