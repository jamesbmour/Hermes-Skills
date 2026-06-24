# Microsoft Graph API — Verified Endpoints

All endpoints tested against v1.0 Graph API with delegated permissions.

## To Do

| Endpoint | Method | Notes |
|---|---|---|
| `/me/todo/lists` | GET | Returns `{value: [{id, displayName, wellknownListName}]}` |
| `/me/todo/lists/{id}/tasks` | GET | Params: `$filter=status ne 'completed'`, `$top`, `$select` |
| `/me/todo/lists/{id}/tasks` | POST | Body: `{title, dueDateTime, importance, body}` |
| `/me/todo/lists/{listId}/tasks/{taskId}` | PATCH | Body: `{status}` — values: `notStarted`, `inProgress`, `completed` |

## Mail

| Endpoint | Method | Notes |
|---|---|---|
| `/me/messages` | GET | Params: `$filter`, `$top`, `$select`, `$orderby`. `$search` and `$orderby` are mutually exclusive. |
| `/me/messages/{id}` | GET | Full message with body |
| `/me/sendMail` | POST | Body: `{message: {...}, saveToSentItems: "true"}` |

## Calendar

| Endpoint | Method | Notes |
|---|---|---|
| `/me/calendarView` | GET | Params: `startDateTime`, `endDateTime`, `$top`, `$select`, `$orderby` |
| `/me/events` | POST | Body: `{subject, start, end, location, attendees, body}` |

## Contacts

| Endpoint | Method | Notes |
|---|---|---|
| `/me/contacts` | GET | Params: `$top`, `$select` |

## OneDrive / SharePoint

| Endpoint | Method | Notes |
|---|---|---|
| `/me/drive/root/children` | GET | List root OneDrive files |
| `/me/drive/root:/{path}` | GET | Get file/folder by path |
| `/me/drive/items/{id}/content` | GET | Download file content |
| `/me/drive/items/{id}` | PATCH | Update file metadata |
| `/sites/{siteId}/drive/root/children` | GET | SharePoint document library |

## Teams Chat

| Endpoint | Method | Notes |
|---|---|---|
| `/me/chats` | GET | List chats |
| `/me/chats/{id}/messages` | GET | Messages in a chat |
| `/me/chats/{id}/messages` | POST | Send message to chat |

## Profile / Directory

| Endpoint | Method | Notes |
|---|---|---|
| `/me` | GET | Current user profile |
| `/me/people` | GET | Relevant people |
| `/users` | GET | Org directory (needs Directory.Read.All) |

## Common OData Parameters

- `$filter` — e.g., `isRead eq false`, `status ne 'completed'`
- `$top` — max results per page (default 10, max varies)
- `$select` — comma-separated field list
- `$orderby` — e.g., `receivedDateTime desc`
- `$search` — keyword search (not compatible with `$orderby`)
- `$skip` — pagination offset

## Pitfalls

1. **`$search` + `$orderby` are mutually exclusive.** Microsoft Graph rejects requests with both.
2. **Device code flow requires "Allow public client flows" = Yes** in Azure AD app Authentication settings.
3. **`offline_access` scope is reserved** — MSAL handles it automatically. Don't include it in explicit scopes.
4. **Token refresh is automatic** — `msgraph_api.py` handles it. Tokens last 90 days by default.
5. **Rate limits** — Graph API has per-app and per-user limits. Space out rapid calls.
