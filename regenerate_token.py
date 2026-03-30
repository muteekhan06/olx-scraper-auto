import os

from google_auth_oauthlib.flow import InstalledAppFlow


CONFIG_DIR = "config"
CLIENT_SECRET_FILE = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_FILE = os.path.join(CONFIG_DIR, "google_token.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def regenerate():
    print("Starting Google token regeneration...")

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"Error: {CLIENT_SECRET_FILE} not found.")
        return

    if os.path.exists(TOKEN_FILE):
        print("Deleting old token file...")
        os.remove(TOKEN_FILE)

    print("Opening browser for login. Please sign in with your Google Account.")
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    print(f"New token saved to: {TOKEN_FILE}")
    print("\n" + "=" * 60)
    print("LEGACY OAUTH TOKEN REGENERATED")
    print("=" * 60)
    print("Local OAuth login is still supported, but GitHub Actions should use")
    print("GOOGLE_SERVICE_ACCOUNT_JSON for unattended automation.")
    print("")
    print("Only if you are still using the legacy OAuth secret flow in GitHub")
    print("Actions, update GOOGLE_TOKEN_JSON with the content below:")
    print("-" * 60)
    print(creds.to_json())
    print("-" * 60)


if __name__ == "__main__":
    regenerate()
