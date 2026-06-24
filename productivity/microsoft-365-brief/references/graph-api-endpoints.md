# Microsoft Graph API Endpoints for Zapier MCP

All endpoints verified working through Zapier MCP tools on 2026-06-24.
Base: `https://graph.microsoft.com/v1.0`

## Outlook — Unread Emails

**Tool:** `mcp_zapier_microsoft_outlook_make_api_get_request`

```
GET /me/messages?$filter=isRead eq false&$top=20&$select=subject,from,receivedDateTime,bodyPreview,importance&$orderby=receivedDateTime desc
```

Returns: `subject`, `from.emailAddress.address` (mapped to `from_address`), `receivedDateTime`, `bodyPreview`, `importance`.

**Pitfall:** `mcp_zapier_microsoft_outlook_find_emails` with `searchValue: "is:unread"` does NOT reliably filter unread emails — it returns a mix of read and unread. Always use the raw Graph API with `$filter=isRead eq false`.

**Pitfall:** The full response can be very large (130KB+ for 20 emails). The Zapier MCP tool may persist large outputs to a temp file. The cron agent should use `output_hint` to request only the fields it needs, which triggers Zapier's jq filter to slim the response.

Example `output_hint`: `"subject, from_address, receivedDateTime, bodyPreview, importance for each unread email"`

## Outlook — Calendar Events

**Tool:** `mcp_zapier_microsoft_outlook_get_calendar_events_in_date_rang`

```
startDateTime: 2026-06-24T00:00:00
endDateTime:   2026-06-24T23:59:59
```

Returns: `subject`, `start` (ISO datetime), `end` (ISO datetime), `location` (display name string), `attendees` (array of email addresses).

Times are returned in UTC. Convert to user's local timezone (ET for James in Cincinnati, OH) when displaying.

## Outlook — Send Email

**Tool:** `mcp_zapier_microsoft_outlook_send_email`

```
recipients: ["james@bmours.com"]
subject: "☀️ Daily Morning Brief — 2026-06-24"
body: <plain text brief>
bodyFormat: "Text"
```

No file attachments needed for the brief — just the text body.

## Microsoft To Do — Task Lists

**Tool:** `mcp_zapier_microsoft_to_do_make_api_get_request`

```
GET /me/todo/lists
```

Returns: `id` (GUID), `displayName` (list name).

**Pitfall:** Must use `v1.0` endpoint, NOT `beta`. The beta endpoint returns 400 errors through Zapier MCP.

**Pitfall:** `mcp_zapier_microsoft_to_do_find_a_task` requires `list_id` — cannot search across all lists. Must fetch lists first, then query each.

## Microsoft To Do — Tasks per List

**Tool:** `mcp_zapier_microsoft_to_do_make_api_get_request`

```
GET /me/todo/lists/{list-id}/tasks?$filter=status ne 'completed'&$top=50&$select=title,importance,status,dueDateTime,bodyPreview
```

Returns: `title`, `importance` (low/normal/high), `status`, `dueDateTime` (may be null), `bodyPreview`.

## Rate Limiting

Zapier MCP has a billing/task counter — each API call consumes "billing tasks". Batching is not supported through the MCP interface. If you make many rapid calls (e.g., querying tasks for 5+ lists), you may hit the rate limiter ("MCP server is unreachable after 3 consecutive failures"). Space out calls or reduce the number of lists queried.

## Token Efficiency

For cron jobs, use `output_hint` on every Zapier MCP call to trigger Zapier's jq filter. This dramatically reduces the response size by stripping metadata, execution traces, and feedback URLs. Without `output_hint`, responses can be 100KB+ and may exceed the cron agent's context budget.