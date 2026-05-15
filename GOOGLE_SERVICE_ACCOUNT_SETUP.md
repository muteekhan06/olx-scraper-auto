# Google Sheets Service Account Setup

Use this for GitHub Actions and any unattended run. It replaces the weekly `GOOGLE_TOKEN_JSON` refresh flow.

## Why

- User OAuth tokens are for interactive logins.
- Service accounts are for server-to-server automation.
- This project now supports both, but GitHub Actions should use the service account path.

## One-Time Setup

1. Open Google Cloud Console and select the same project that has the Sheets API enabled.
2. Go to `IAM & Admin` -> `Service Accounts`.
3. Create a new service account for this project.
4. Open that service account and create a new JSON key.
5. Copy the entire JSON file content.
6. In GitHub, open the repository:
   `Settings` -> `Secrets and variables` -> `Actions`
7. Add a new repository secret named `GOOGLE_SERVICE_ACCOUNT_JSON`.
8. Paste the full JSON key into that secret.
9. Open your target Google Sheet.
10. Share the sheet with the service account email from the JSON file (`client_email`) as `Editor`.

## After Setup

- Lahore daily workflow will use the service account automatically.
- Karachi manual workflow will use the service account automatically.
- `GOOGLE_CLIENT_SECRET` and `GOOGLE_TOKEN_JSON` become legacy fallback only.
- Local/server runs can use either `config/service_account.json` or a `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable containing the full service account JSON.
- You do not need to regenerate `config/google_token.json` weekly after the workflow secret is configured.

## Important

- Keep the JSON key private.
- If a key is exposed, delete that key in Google Cloud and create a new one.
- If you previously pasted live OAuth tokens anywhere public or into chat, rotate them.
