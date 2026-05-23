"""
Google Sheets integration.

Supported auth modes:
1. Service account for unattended automation
2. OAuth desktop login for local interactive use
"""

import json
import os
import re
from datetime import date
from typing import Dict, List, Optional, Set

from app.config import OUTPUT_CONFIG, CONFIG_DIR


# File paths (in config/ directory)
CLIENT_SECRET_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
SERVICE_ACCOUNT_FILE = os.path.join(CONFIG_DIR, "service_account.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "google_token.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_ENV = "GOOGLE_SERVICE_ACCOUNT_JSON"
HISTORY_EXCLUDED_SHEETS = {"readme", "summary", "dashboard"}


def _load_service_account_info():
    """Load service account JSON from env or file, if configured."""
    raw = os.environ.get(SERVICE_ACCOUNT_ENV, "").strip()
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"{SERVICE_ACCOUNT_ENV} is set but is not valid JSON: {exc}"
            ) from exc

    if os.path.exists(SERVICE_ACCOUNT_FILE):
        try:
            with open(SERVICE_ACCOUNT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            raise RuntimeError(
                f"Service account credentials could not be loaded from {SERVICE_ACCOUNT_FILE}: {exc}"
            ) from exc

    return None


def get_google_auth_mode() -> str:
    """Return the configured Google auth mode."""
    if os.environ.get(SERVICE_ACCOUNT_ENV, "").strip() or os.path.exists(SERVICE_ACCOUNT_FILE):
        return "service_account"
    if os.path.exists(CLIENT_SECRET_FILE):
        return "oauth"
    return "none"


def is_google_sheets_configured() -> bool:
    """Check if Google Sheets auth is configured."""
    return get_google_auth_mode() != "none"


def is_google_sheets_authenticated() -> bool:
    """Check if the configured auth mode is ready to use."""
    auth_mode = get_google_auth_mode()
    if auth_mode == "service_account":
        return True
    if auth_mode == "oauth":
        return os.path.exists(TOKEN_FILE)
    return False


def get_google_credentials():
    """Get Google Sheets credentials for the configured auth mode."""
    try:
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        raise RuntimeError(
            "Required packages not installed. Run:\n"
            "pip install google-auth google-auth-oauthlib google-auth-httplib2"
        )
    
    service_account_info = _load_service_account_info()
    if service_account_info:
        try:
            return service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=SCOPES,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Service account credentials could not be initialized: {exc}"
            ) from exc

    if not os.path.exists(CLIENT_SECRET_FILE):
        raise FileNotFoundError(
            "Google Sheets auth is not configured.\n"
            f"Preferred for automation: set {SERVICE_ACCOUNT_ENV} or add {SERVICE_ACCOUNT_FILE}.\n"
            f"Local fallback: add OAuth client file at {CLIENT_SECRET_FILE}."
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
            # Check if running in CI/Headless environment
            if os.environ.get("CI") or os.environ.get("HEADLESS"):
                raise RuntimeError(
                    "Google OAuth token is missing or invalid in CI/headless mode.\n"
                    "Preferred fix: configure GOOGLE_SERVICE_ACCOUNT_JSON and share the sheet with that service account.\n"
                    "Legacy fallback: refresh GOOGLE_TOKEN_JSON with a new browser login."
                )

            # Need fresh login via browser (Local Machine Only)
            print("Initiating Google login via browser...")
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


def extract_lead_key(row: Dict) -> str:
    """Build a stable lead key from OLX Ad ID, falling back to iid in the URL."""
    ad_id = clean_value(row.get("Ad ID") or row.get("ad_id") or row.get("id"))
    ad_id = ad_id.replace("Ad ID", "").replace(":", "").strip()
    if ad_id:
        return f"ad:{ad_id.lower()}"

    link = clean_value(row.get("Link") or row.get("link") or row.get("URL") or row.get("url"))
    match = re.search(r"iid-([A-Za-z0-9_-]+)", link)
    if match:
        return f"iid:{match.group(1).lower()}"

    return ""


def extract_link_from_formula(value: str) -> str:
    """Extract URL from a Sheets HYPERLINK formula if the cell is formula-rendered."""
    text = str(value or "").strip()
    match = re.match(r'=HYPERLINK\("([^"]+)"\s*,', text, flags=re.I)
    return match.group(1) if match else text


def _row_dict_from_values(headers: List[str], values: List[str]) -> Dict:
    row: Dict[str, str] = {}
    for index, header in enumerate(headers):
        if not header:
            continue
        value = values[index] if index < len(values) else ""
        if header == "Link":
            value = extract_link_from_formula(value)
        row[header] = value
    return row


def get_existing_lead_keys(
    spreadsheet_id: str,
    exclude_sheet_name: Optional[str] = None,
    service=None,
    progress_callback=None,
) -> Set[str]:
    """Read historical daily tabs and return known OLX lead keys."""
    service = service or get_sheets_service()
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    excluded = {name.lower() for name in HISTORY_EXCLUDED_SHEETS}
    if exclude_sheet_name:
        excluded.add(exclude_sheet_name.lower())

    keys: Set[str] = set()
    sheet_count = 0

    for sheet in spreadsheet.get("sheets", []):
        title = sheet.get("properties", {}).get("title", "")
        if not title or title.lower() in excluded:
            continue

        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{title}'!A:ZZ",
            valueRenderOption="FORMULA",
        ).execute().get("values", [])

        if not values:
            continue

        headers = [str(header).strip() for header in values[0]]
        if "Ad ID" not in headers and "Link" not in headers:
            continue

        sheet_count += 1
        for values_row in values[1:]:
            key = extract_lead_key(_row_dict_from_values(headers, values_row))
            if key:
                keys.add(key)

    if progress_callback:
        progress_callback(f"Loaded {len(keys)} historical lead keys from {sheet_count} previous sheet tab(s).")

    return keys


def remove_duplicate_leads(
    data: List[Dict],
    existing_keys: Optional[Set[str]] = None,
) -> List[Dict]:
    """Remove leads already seen historically and duplicates inside the current batch."""
    seen = set(existing_keys or set())
    output: List[Dict] = []

    for row in data:
        key = extract_lead_key(row)
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        output.append(row)

    return output


def export_to_google_sheets(
    data: List[Dict],
    spreadsheet_id: str,
    sheet_name: str = None,
    progress_callback=None,
) -> str:
    """
    Export data directly to Google Sheets.
    Service account auth is preferred for unattended automation.
    OAuth desktop auth is retained for local interactive use.
    
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
            cleaned_val = clean_value(val)
            
            # Make Link clickable
            if col == "Link" and cleaned_val and cleaned_val.startswith("http"):
                # Use "View Ad" as label to keep cell content clean and formula short
                cleaned_val = f'=HYPERLINK("{cleaned_val}", "View Ad")'
            
            row.append(cleaned_val)
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
    
    # Apply premium formatting
    try:
        # Get sheet ID
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_id = None
        for s in spreadsheet.get("sheets", []):
            if s["properties"]["title"] == sheet_name:
                sheet_id = s["properties"]["sheetId"]
                break
        
        if sheet_id is not None and progress_callback:
            progress_callback("Applying premium formatting...")
        
        if sheet_id is not None:
            num_rows = len(rows)
            num_cols = len(columns)
            
            requests = [
                # 1. Set Merriweather font + center align + middle align + wrap for ALL cells
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": num_rows,
                            "startColumnIndex": 0,
                            "endColumnIndex": num_cols
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "fontFamily": "Merriweather",
                                    "fontSize": 10
                                },
                                "horizontalAlignment": "CENTER",
                                "verticalAlignment": "MIDDLE",
                                "wrapStrategy": "WRAP"
                            }
                        },
                        "fields": "userEnteredFormat"
                    }
                },
                # 2. Header row: Bold + Background color
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": num_cols
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "textFormat": {
                                    "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                    "bold": True,
                                    "fontFamily": "Merriweather",
                                    "fontSize": 11
                                },
                                "backgroundColor": {
                                    "red": 0.2, "green": 0.4, "blue": 0.6
                                },
                                "horizontalAlignment": "CENTER",
                                "verticalAlignment": "MIDDLE"
                            }
                        },
                        "fields": "userEnteredFormat"
                    }
                },
                # 3. Freeze header row
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": sheet_id,
                            "gridProperties": {
                                "frozenRowCount": 1
                            }
                        },
                        "fields": "gridProperties.frozenRowCount"
                    }
                },
                # 4. Auto-resize columns to fit content
                {
                    "autoResizeDimensions": {
                        "dimensions": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,
                            "endIndex": num_cols
                        }
                    }
                }
            ]
            
            # Execute formatting
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, 
                body={"requests": requests}
            ).execute()
            
    except Exception as fmt_err:
        if progress_callback:
            progress_callback(f"Formatting applied (some features may vary): {fmt_err}")
    
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
    
    if progress_callback:
        progress_callback(f"✅ Exported {len(data)} rows with premium formatting!")
    
    return url


def delete_google_token():
    """Delete saved Google token (for re-authentication)."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
