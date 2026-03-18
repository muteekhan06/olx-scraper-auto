# Vercel Karachi Dashboard (Secure, Single Admin, No DB)

This dashboard is only for manually running the **Karachi** workflow.
Lahore automation remains unchanged.

## What Changed

- Karachi GitHub workflow is now manual-only (`workflow_dispatch` only).
- Karachi workflow accepts manual inputs:
  - `areas` (comma-separated Karachi keys, or `all`)
  - `max_pages`
  - `max_listings`
- New Vercel dashboard:
  - Single-admin login (no database)
  - Karachi area selection
  - Manual dispatch to Karachi GitHub workflow
  - Recent run status view

## 1) Deploy This Repo to Vercel

1. Import this GitHub repository in Vercel.
2. Framework preset: `Other`.
3. Keep root as project root.
4. Deploy.

`vercel.json` already routes:
- `/` -> `dashboard/index.html`
- `/api/*` -> serverless API routes

## 2) Required Vercel Environment Variables

Set these in Vercel Project Settings -> Environment Variables:

- `SESSION_SECRET`
  - Long random secret, at least 32 characters.
- `DASHBOARD_ADMIN_USERNAME`
  - Single admin username.
- One of these password methods:
  - `DASHBOARD_ADMIN_PASSWORD` (simple mode), or
  - `DASHBOARD_ADMIN_SALT` + `DASHBOARD_ADMIN_PASSWORD_HASH` (recommended mode).
- `GITHUB_PAT`
  - GitHub personal access token with permissions:
    - Actions: Read and write
    - Contents: Read
    - Metadata: Read
- `GITHUB_OWNER`
  - Example: `muteekhan06`
- `GITHUB_REPO`
  - Example: `olx-scraper-auto`
- `KARACHI_WORKFLOW_REF`
  - `main`

## 3) Recommended Password Hash Mode

Use PBKDF2 hash instead of plain password env.

Node command to generate values:

```bash
node -e "const c=require('crypto');const p=process.argv[1];const s=c.randomBytes(16).toString('hex');const h=c.pbkdf2Sync(p,s,120000,32,'sha256').toString('hex');console.log('DASHBOARD_ADMIN_SALT='+s);console.log('DASHBOARD_ADMIN_PASSWORD_HASH='+h);" "YourStrongPasswordHere"
```

Then set:
- `DASHBOARD_ADMIN_SALT`
- `DASHBOARD_ADMIN_PASSWORD_HASH`

Do not set `DASHBOARD_ADMIN_PASSWORD` when using hash mode.

## 4) How Manual Karachi Run Works

1. Login to Vercel dashboard.
2. Select Karachi areas.
3. Click `Run Karachi Workflow`.
4. Dashboard calls GitHub Actions `workflow_dispatch` for `karachi_daily_scrape.yml`.
5. Workflow validates all input area keys are Karachi-only.

## Karachi Area Keys

- `gulshan_iqbal`
- `gulistan_jauhar`
- `fb_area`
- `north_nazimabad`
- `nazimabad`
- `naya_nazimabad`
- `north_karachi`
- `new_karachi`
- `saddar_town`
- `dha_defence_karachi`
- `clifton`
- `buffer_zone_north`
- `buffer_zone_2`
- `khalid_bin_walid`

## Security Notes

- Dashboard uses secure, HTTP-only session cookie.
- Login has basic IP-based lockout after repeated failures.
- Use a strong `SESSION_SECRET`.
- Use least-privilege GitHub token.
- Keep all secrets only in Vercel env vars.
