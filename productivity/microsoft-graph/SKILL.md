---
name: microsoft-graph
description: "Microsoft Graph API: To Do, Outlook Mail, Calendar, Contacts via device-code OAuth. Direct access — no Zapier dependency."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Microsoft 365, Outlook, To Do, Calendar, Contacts, Graph API, OAuth]
---

# Microsoft Graph API

Direct access to Microsoft 365 — To Do tasks, Outlook mail, Calendar, and Contacts — via the Microsoft Graph REST API with device-code OAuth. No third-party dependency, no browser redirects, fully headless.

## Setup

### 1. Register an Azure AD application (one-time, ~5 minutes)

1. Go to **https://portal.azure.com** → **App registrations** → **New registration**
2. **Name:** "Hermes Agent" (or anything you prefer)
3. **Supported account types:** "Accounts in any organizational directory (Any Microsoft Entra ID tenant — Multitenant) and personal Microsoft accounts"
4. **Redirect URI:** Leave blank — device code flow doesn't need one
5. Click **Register**
6. Copy the **Application (client) ID** (a UUID like `a1b2c3d4-...`)
7. Copy the **Directory (tenant) ID** (or use `common` for multi-tenant apps)
8. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**
9. Add these scopes:
   - `Tasks.ReadWrite` — To Do
   - `Mail.Read` — Read Outlook email
   - `Mail.Send` — Send Outlook email
   - `Calendars.ReadWrite` — Calendar
   - `Contacts.Read` — People/Contacts
   - `Files.ReadWrite` — OneDrive + SharePoint files (Excel, Word, PowerPoint, PDFs)
   - `Sites.Read.All` — SharePoint sites and document libraries
   - `Chat.ReadWrite` — Teams chat messages
   - `People.Read` — Org directory and colleague info
   - `User.Read` — Basic profile (default, already there)
   - **Do NOT add `offline_access`** — MSAL handles refresh tokens automatically. Including it causes `ValueError: You cannot use any scope value that is reserved`.
10. Click **Grant admin consent** (if you're the admin) or skip if your org auto-grants

### 2. Configure Hermes

```bash
# Set up the shorthand
MSETUP="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/microsoft-graph/scripts/setup.py"
MGAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/microsoft-graph/scripts/msgraph_api.py"

# Install dependencies
$MSETUP --install-deps

# Store your Azure AD credentials
$MSETUP --configure <tenant> <client_id>
# Example: $MSETUP --configure common a1b2c3d4-5678-90ab-cdef-1234567890ab
```

### 3. Authenticate (two-step device code flow)

**Step A — Get the code:**
```bash
$MSETUP --auth-start
```

This prints a JSON object with:
- `user_code` — a short code like `ABCD1234`
- `verification_uri` — the URL to visit (usually `https://login.microsoft.com/device`)
- `expires_in` — 900 seconds (15 minutes)

**Send the user the code and URL.** They:
1. Visit the URL in any browser (phone, desktop, anything)
2. Enter the code
3. Sign in with their Microsoft 365 account
4. See "You're signed in" — close the browser
5. Tell you "done"

**Step B — Poll for completion (only after user confirms):**
```bash
$MSETUP --auth-poll
```

This polls for up to 120 seconds and saves the token. The two-step split prevents terminal timeouts while the user is entering the code. The single `--auth` command exists but polls immediately and will time out before the user acts — prefer `--auth-start` + `--auth-poll`.

### 4. Verify

```bash
$MSETUP --check
# Should print: AUTHENTICATED: Token valid at ~/.hermes/msgraph_token.json

$MGAPI me
# Should return your Microsoft 365 profile
```

## Usage

All commands return JSON. Set `MGAPI` as a shorthand:

```bash
MGAPI="python ${HERMES_HOME:-$HOME/.hermes}/skills/productivity/microsoft-graph/scripts/msgraph_api.py"
```

### To Do Tasks

```bash
# List all task lists
$MGAPI todo lists

# List tasks in a list (incomplete only by default)
$MGAPI todo tasks <list_id>
$MGAPI todo tasks <list_id> --include-completed

# Create a task
$MGAPI todo create <list_id> --title "Review Q3 report" --importance high --due "2026-07-15T17:00:00"

# Update a task
$MGAPI todo update <task_id> --status completed
$MGAPI todo update <task_id> --title "New title" --importance low
```

### Outlook Mail

```bash
# Search unread emails
$MGAPI mail search "isRead eq false" --top 20

# Search by sender
$MGAPI mail search "from/emailAddress/address eq 'boss@company.com'"

# Search with date
$MGAPI mail search "receivedDateTime ge 2026-06-01 and isRead eq false"

# Get full email body
$MGAPI mail get <message_id>

# Send email
$MGAPI mail send --to "james@bmours.com" --subject "Test" --body "Hello from Hermes"
$MGAPI mail send --to "team@company.com" --cc "boss@company.com" --subject "Update" --body "<h1>Report</h1>" --body-format HTML
```

### Calendar

```bash
# List today's events
$MGAPI calendar list --start "2026-06-24T00:00:00" --end "2026-06-24T23:59:59"

# List next 7 days (default)
$MGAPI calendar list

# Create an event
$MGAPI calendar create --summary "Team Standup" --start "2026-06-25T10:00:00" --end "2026-06-25T10:30:00"
$MGAPI calendar create --summary "Lunch" --start "2026-06-25T12:00:00" --end "2026-06-25T13:00:00" --location "Cafe" --attendees "alice@co.com,bob@co.com"
```

### Contacts

```bash
$MGAPI contacts list --top 50
```

## Output Format

All commands return JSON. Key fields:

- **todo lists**: `{value: [{id, displayName, wellknownListName}]}`
- **todo tasks**: `{value: [{id, title, status, importance, dueDateTime, body, createdDateTime}]}`
- **mail search**: `{value: [{id, subject, from, receivedDateTime, bodyPreview, importance, isRead, hasAttachments}]}`
- **mail get**: `{id, subject, from, toRecipients, receivedDateTime, body, ...}`
- **calendar list**: `{value: [{id, subject, start, end, location, attendees, organizer}]}`
- **contacts list**: `{value: [{id, displayName, emailAddresses, businessPhones, mobilePhone, companyName}]}`

## Token Management

- Token stored at `~/.hermes/msgraph_token.json`
- Auto-refreshes on each API call — no manual intervention needed
- Refresh tokens last 90 days by default (Microsoft policy)
- To revoke: `$MSETUP --revoke`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `NOT_AUTHENTICATED` | Run `$MSETUP --auth-start` then `$MSETUP --auth-poll` after entering the code |
| `REFRESH_FAILED` | Token expired beyond 90 days — run `$MSETUP --auth-start` again |
| `NOT_CONFIGURED` | Run `$MSETUP --configure <tenant> <client_id>` |
| `403 Forbidden` | Missing API permission — add scopes in Azure portal and re-auth |
| `ModuleNotFoundError: msal` | Run `$MSETUP --install-deps` |
| Device code expired | Codes last 15 min — run `$MSETUP --auth-start` for a fresh code |
| `AADSTS7000218: client_assertion or client_secret required` | Azure AD app has "Allow public client flows" set to **No**. Go to Azure Portal → App registrations → Hermes Agent → Authentication → toggle "Allow public client flows" to **Yes** → Save. Then re-auth. |
| `ValueError: reserved scope` | `offline_access` is handled automatically by MSAL — remove it from the SCOPES list |
| Admin consent required | Your org may require an admin to grant consent. In Azure portal → API permissions → Grant admin consent |
| Polling times out before user enters code | Use the two-step flow: `--auth-start` to get the code, then `--auth-poll` after the user confirms they've entered it. The single `--auth` command polls immediately and times out in 120s. |
| `$select` parameter causes 400 error on some lists | Some To Do list IDs (especially custom lists) reject `$select` in the query parameters. Remove `$select` and fetch full task objects instead — the response is small enough that filtering client-side is fine. |

## Pitfalls

### Device code flow: use two-step, not single `--auth`

`$MSETUP --auth` polls for token completion immediately and will time out (120s) before the user enters the code. **Always use the two-step flow:** `$MSETUP --auth-start` to get the code and present it to the user, then `$MSETUP --auth-poll` only after the user confirms they've entered it. The pending auth state is saved to `~/.hermes/msgraph_pending.json` so the poll can happen in a separate terminal call.

### `$select` parameter breaks on some To Do lists

Custom To Do lists (like "Hermes", "YouTube") may return HTTP 400 when `$select` is included in query parameters. The default Tasks list works fine with `$select`. The `msgraph_api.py` wrapper omits `$select` by default to avoid this — it fetches full task objects. If you need `$select`, test it on the specific list first.

### `offline_access` scope causes ValueError in MSAL

MSAL handles refresh tokens automatically. Including `offline_access` in the SCOPES list causes `ValueError: You cannot use any scope value that is reserved`. Remove it — the token will still have refresh capability.

### Azure AD app must allow public client flows

Device code flow requires the app registration to have "Allow public client flows" set to **Yes**. If you get `AADSTS7000218: client_assertion or client_secret required`, go to Azure Portal → App registrations → your app → Authentication → toggle it on → Save.

## Comparison with Zapier MCP

| | Direct Graph API (this skill) | Zapier MCP |
|---|---|---|
| **Uptime** | You control it | Depends on Zapier's servers |
| **To Do support** | ✅ Full | ⚠️ Unreliable (400 errors common) |
| **Auth** | Device code — headless | Browser OAuth via Zapier |
| **Rate limits** | Standard Graph limits | Extra hop + Zapier limits |
| **API coverage** | Full Microsoft Graph | Limited to Zapier's integrations |
