import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Config
CONFIG_DIR = "config"
CLIENT_SECRET_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "google_token.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def regenerate():
    print("🔄 Starting Google Token Regeneration...")
    
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ Error: {CLIENT_SECRET_FILE} not found!")
        return

    # Force delete old token to ensure fresh login
    if os.path.exists(TOKEN_FILE):
        print("🗑️  Deleting old token file...")
        os.remove(TOKEN_FILE)

    # Start OAuth Flow
    print("🚀 Opening browser for login... Please sign in with your Google Account.")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save new token
    print("✅ Login successful!")
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())
    
    print(f"💾 New token saved to: {TOKEN_FILE}")
    print("\n" + "="*50)
    print("⚠️  ACTION REQUIRED: UPDATE GITHUB SECRET  ⚠️")
    print("="*50)
    print("1. Go to your GitHub Repository -> Settings -> Secrets and variables -> Actions")
    print("2. Find 'GOOGLE_TOKEN_JSON'")
    print("3. Click 'Edit' (Pencil Icon)")
    print("4. Delete everything there and PASTE the content below:")
    print("-" * 50)
    print(creds.to_json())
    print("-" * 50)
    print("5. Click 'Update Secret'")
    print("="*50)

if __name__ == "__main__":
    regenerate()
