---
name: microsoft-365-brief
description: "Create automated daily briefings from Microsoft 365 data (Outlook emails, Calendar events, To Do tasks) plus external sources (Sage Intacct email reports, weather via Open-Meteo, market pre-open data) using the direct Microsoft Graph API (msgraph_api.py). No Zapier dependency. Covers cron job setup, exact terminal commands, delivery configuration, and email dispatch."
version: 2.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Microsoft 365, Outlook, To Do, Calendar, Graph API, Cron, Daily Brief, Productivity]
---

# Microsoft 365 Daily Brief (Direct Graph API)

Create automated briefings that aggregate Outlook emails, Calendar events, and Microsoft To Do tasks — plus Sage Intacct, weather, and market data — using the direct Microsoft Graph API via `msgraph_api.py`. Zero Zapier dependency. Delivered via email and all connected channels.

## When to use this skill

The user asks to:
- Create a daily morning brief / summary / digest from Microsoft 365 data
- Summarize unread emails, today's calendar, and/or To Do tasks on a schedule
- Set up a recurring automated report from Outlook or To Do
- Send a compiled briefing via email and/or Slack
- Add financial snapshots (Sage Intacct), weather forecasts, or market pre-open data to a brief

Trigger examples: "morning brief at 4 AM", "daily email summary", "summarize my unread emails and calendar every day", "daily digest of Outlook and To Do", "add weather and market data to my brief", "financial snapshot in the morning brief".

## Prerequisites

- **`microsoft-graph` skill** must be set up (device-code OAuth, `msgraph_api.py` working). See `productivity/microsoft-graph` SKILL.md.
- `msgraph_api.py` must be able to send email (`Mail.Send` scope granted in Azure AD).
- For Slack delivery: Slack must be connected as a messaging platform in Hermes.

## Critical: Cron job toolset configuration

The cron job uses `terminal` (for `msgraph_api.py` and curl), `web` (for market data web_search), and `file` (for any temp file needs). Set:

```
enabled_toolsets: ["terminal", "web", "file"]
```

Do NOT set `enabled_toolsets: []` — that was the old Zapier MCP pattern. The direct Graph API approach uses standard tools only.

## Step-by-step: Creating a daily brief cron job

### 1. Create the cron job

```
cronjob(action='create', schedule='0 4 * * *', name='Daily Morning Brief',
         enabled_toolsets=['terminal', 'web', 'file'], ...)
```

### 2. Configure delivery

Delivery options that work:
- `"all"` — fans out to every connected channel. Most reliable.
- `"origin,all"` — both origin and all channels.
- `"slack:<channel_id>"` — specific Slack channel.

### 3. Compose the prompt with exact terminal commands

The cron prompt must contain exact `msgraph_api.py` commands. Vague instructions like "fetch unread emails" do NOT work reliably — the agent in the cron session has no conversation context.

Set this shorthand at the start of the prompt:
```
MGAPI="python3 /home/hermeswebui/.hermes/skills/productivity/microsoft-graph/scripts/msgraph_api.py"
```

**Portability:** The path above is hardcoded to a specific install. When exporting the cron job to another Hermes instance, replace with the new system's path — typically `python3 ~/.hermes/skills/productivity/microsoft-graph/scripts/msgraph_api.py` (or the absolute path if `$HOME` resolves differently in the cron env). Use `$HERMES_HOME` if set: `python3 ${HERMES_HOME}/skills/productivity/microsoft-graph/scripts/msgraph_api.py`.

#### Unread Emails
```
$MGAPI mail search "isRead eq false" --top 20
```
Returns JSON with subject, from, receivedDateTime, bodyPreview, importance, isRead, hasAttachments.

#### Calendar Events
```
$MGAPI calendar list --start "YYYY-MM-DDT00:00:00" --end "YYYY-MM-DDT23:59:59"
```

#### To Do Tasks (two-step)
```
$MGAPI todo lists                          # Step 1: get all list IDs
$MGAPI todo tasks <list_id>                # Step 2: tasks per list
```
Parse JSON from each call. Group by list name. Graceful fallback: if a call fails, note "To Do unavailable for [list]" and continue.

#### Sage Intacct (via email search)
```
$MGAPI mail search "receivedDateTime ge YYYY-MM-DD and (intacct OR balance_sheet OR income_statement OR remittance)" --top 15
```
Use a date 30 days ago. Look for Balance_Sheet-Detail, "Unsuccessful file delivery" (OneDrive connector failures), remittance advices from Paul Owens, Sage Developer API notifications.

#### Weather (via curl)
```bash
curl -s "https://api.open-meteo.com/v1/forecast?latitude=39.1031&longitude=-84.5120&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weathercode,windspeed_10m_max&hourly=temperature_2m,precipitation_probability,weathercode&timezone=America/New_York&forecast_days=1"
```
WMO codes: 0=Clear, 1-3=Partly cloudy, 45-48=Fog, 51-57=Drizzle, 61-67=Rain, 71-77=Snow, 80-82=Rain showers, 95=Thunderstorm. Convert °C to °F: `°F = °C × 9/5 + 32`.

#### Market Pre-Opening (via web_search)
Search for "S&P 500 futures Dow futures Nasdaq futures pre-market today" and "10 year treasury yield oil price gold price today". Extract levels and changes.

#### Email the Brief
```
$MGAPI mail send --to "james@bmours.com" --subject "☀️ Daily Morning Brief — [Date]" --body "[FULL BRIEF TEXT]"
```
Uses `--body-format Text` by default. Do NOT attach files.

### 4. Brief format

Use plain text (NOT markdown) since the brief goes to email. Structure:

```
☀️ Daily Morning Brief — [Day, Date]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📧 UNREAD EMAILS (X unread)
- Grouped by sender/topic
- ⚠️ Flag items needing action today

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📅 TODAY'S CALENDAR
- Time | Subject | Location (attendees)
- Note conflicts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### ✅ TO DO TASKS
- Due Today/Overdue: list with importance and list name
- Upcoming: list

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 💰 SAGE INTACCT FINANCIAL SNAPSHOT
- Recent reports and delivery status
- Remittance advices
- API/connector issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🌤️ WEATHER — CINCINNATI, OH
- Current conditions, today's forecast
- Hourly highlights
- Logistics/driving impact

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 📈 MARKET PRE-OPENING
- Index levels and changes
- Commodities and rates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### 🎯 PRIORITY FOCUS — TOP 5
- Top 5 things to tackle today synthesized from all sources
```

## Pitfalls

1. **`enabled_toolsets: []` is the OLD Zapier pattern.** The new direct Graph API approach uses `["terminal", "web", "file"]`. Setting `[]` still works but is unnecessary.
2. **`msgraph_api.py` path must be absolute.** The cron agent runs in a fresh session — relative paths won't resolve. Use the full path: `/home/hermeswebui/.hermes/skills/productivity/microsoft-graph/scripts/msgraph_api.py`. When exporting to another Hermes install, update this path to match the new `$HERMES_HOME` or home directory.
3. **To Do list IDs contain `=` signs.** `msgraph_api.py` handles URL-encoding internally — just pass the raw ID.
4. **`$search` and `$orderby` are mutually exclusive** in Microsoft Graph. For Intacct email search, use `$search` without `$orderby`.
5. **Email body must be plain text.** `msgraph_api.py mail send` defaults to Text format. Markdown doesn't render in all email clients.
6. **Vague prompts cause stalls.** The cron prompt must contain exact terminal commands — the agent has no conversation context and cannot guess commands.
7. **Token auto-refreshes.** `msgraph_api.py` handles token refresh automatically — no auth management needed in cron prompts.
8. **Weather temps are Celsius.** Always convert to Fahrenheit for US delivery.
9. **Yahoo Finance requires User-Agent.** If using execute_code for market data instead of web_search, set `{'User-Agent': 'Mozilla/5.0'}`.

## Verification

After creating or updating the job:
1. Run it manually with `cronjob(action='run', job_id=...)`
2. Wait 60-90 seconds for the agent to complete all terminal calls
3. Check `cronjob(action='list')` for `last_status: "ok"` and no `last_delivery_error`
4. Verify the brief was delivered to email (check inbox) and Slack

## References

- See `references/graph-api-endpoints.md` for the complete list of verified Microsoft Graph API endpoints and example responses.
- See `references/exporting-cron-jobs.md` for how to export brief cron jobs (and other cron jobs) for import into another Hermes install, including path portability guidance.
