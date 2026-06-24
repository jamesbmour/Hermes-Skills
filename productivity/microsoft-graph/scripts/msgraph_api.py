#!/usr/bin/env python3
"""Microsoft Graph API CLI wrapper for Hermes Agent.

Reads the token from ~/.hermes/msgraph_token.json and makes Graph API calls.
All commands return JSON to stdout for easy parsing.

Usage:
  msgraph_api.py todo lists
  msgraph_api.py todo tasks LIST_ID [--include-completed]
  msgraph_api.py todo create LIST_ID --title "Task name" [--due DATE] [--importance low|normal|high]
  msgraph_api.py todo update TASK_ID --status completed|notStarted|inProgress
  msgraph_api.py mail search "isRead eq false" [--top 20]
  msgraph_api.py mail get MESSAGE_ID
  msgraph_api.py mail send --to EMAIL --subject "..." --body "..."
  msgraph_api.py calendar list [--start ISO] [--end ISO]
  msgraph_api.py calendar create --summary "..." --start ISO --end ISO
  msgraph_api.py contacts list [--top 50]
  msgraph_api.py me
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Resolve Hermes home
HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
TOKEN_PATH = HERMES_HOME / "msgraph_token.json"
CONFIG_PATH = HERMES_HOME / "msgraph_config.json"

GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _load_token() -> dict:
    """Load and refresh token if needed."""
    if not TOKEN_PATH.exists():
        print(json.dumps({"error": "NOT_AUTHENTICATED", "message": "Run setup.py --auth first"}))
        sys.exit(1)

    token_data = json.loads(TOKEN_PATH.read_text())

    # Check if access token is expired
    import time
    now = int(time.time())
    expires_on = token_data.get("expires_in", 0)
    if "expires_at" in token_data:
        expires_at = token_data["expires_at"]
    else:
        expires_at = now + expires_on - 300  # 5 min buffer

    if now >= expires_at and token_data.get("refresh_token"):
        # Refresh
        config = json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}
        client_id = config.get("client_id", "")
        tenant = config.get("tenant", "common")

        import msal
        authority = f"https://login.microsoftonline.com/{tenant}"
        app = msal.PublicClientApplication(client_id, authority=authority)
        result = app.acquire_token_by_refresh_token(
            token_data["refresh_token"],
            scopes=["Tasks.ReadWrite", "Mail.Read", "Mail.Send", "Calendars.ReadWrite",
                    "Contacts.Read", "User.Read", "offline_access"],
        )
        if "access_token" in result:
            result["expires_at"] = int(time.time()) + result.get("expires_in", 3600) - 300
            TOKEN_PATH.write_text(json.dumps(result, indent=2))
            token_data = result
        else:
            print(json.dumps({"error": "REFRESH_FAILED", "message": "Run setup.py --auth to re-authenticate"}))
            sys.exit(1)

    return token_data


def _api_call(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    """Make a Microsoft Graph API call."""
    token_data = _load_token()
    access_token = token_data["access_token"]

    url = f"{GRAPH_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    data = None
    if body:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if not raw:
                return {"status": resp.status, "body": ""}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            error_json = json.loads(error_body)
        except json.JSONDecodeError:
            error_json = {"error": {"code": str(e.code), "message": error_body}}
        print(json.dumps({"error": "GRAPH_API_ERROR", "status": e.code, "detail": error_json}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": "NETWORK_ERROR", "message": str(e)}))
        sys.exit(1)


def _paginate(path: str, params: dict | None = None, max_results: int = 200) -> list:
    """Handle paginated Graph API responses."""
    all_results = []
    next_url = None

    while True:
        if next_url:
            # Follow @odata.nextLink
            token_data = _load_token()
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            req = urllib.request.Request(next_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        else:
            data = _api_call("GET", path, params=params)

        all_results.extend(data.get("value", []))

        next_url = data.get("@odata.nextLink")
        if not next_url or len(all_results) >= max_results:
            break

    return all_results[:max_results]


# ── Commands ──────────────────────────────────────────────────────────────


def cmd_me():
    """Get current user profile."""
    data = _api_call("GET", "/me")
    print(json.dumps(data, indent=2))


def cmd_todo_lists():
    """List all To Do task lists."""
    data = _api_call("GET", "/me/todo/lists")
    print(json.dumps(data, indent=2))


def cmd_todo_tasks(list_id: str, include_completed: bool = False):
    """List tasks in a To Do list."""
    encoded_id = urllib.parse.quote(list_id, safe='')
    params = {"$top": 100}
    if not include_completed:
        params["$filter"] = "status ne 'completed'"
    data = _api_call("GET", f"/me/todo/lists/{encoded_id}/tasks", params=params)
    print(json.dumps(data, indent=2))


def cmd_todo_create(list_id: str, title: str, due: str | None = None,
                    importance: str | None = None, body_text: str | None = None):
    """Create a new task in a To Do list."""
    task = {"title": title}
    if due:
        task["dueDateTime"] = {"dateTime": due, "timeZone": "America/New_York"}
    if importance:
        task["importance"] = importance
    if body_text:
        task["body"] = {"content": body_text, "contentType": "text"}

    data = _api_call("POST", f"/me/todo/lists/{list_id}/tasks", body=task)
    print(json.dumps(data, indent=2))


def cmd_todo_update(task_id: str, status: str | None = None,
                    title: str | None = None, importance: str | None = None):
    """Update a To Do task."""
    updates = {}
    if status:
        updates["status"] = status
    if title:
        updates["title"] = title
    if importance:
        updates["importance"] = importance

    data = _api_call("PATCH", f"/me/todo/lists/{task_id.split('/tasks/')[0]}/tasks/{task_id.split('/tasks/')[-1]}",
                     body=updates)
    print(json.dumps(data, indent=2))


def cmd_mail_search(query: str, top: int = 20):
    """Search Outlook emails using OData filter."""
    params = {
        "$filter": query,
        "$top": top,
        "$select": "id,subject,from,receivedDateTime,bodyPreview,importance,isRead,hasAttachments",
        "$orderby": "receivedDateTime desc",
    }
    data = _api_call("GET", "/me/messages", params=params)
    print(json.dumps(data, indent=2))


def cmd_mail_get(message_id: str):
    """Get a full email message."""
    data = _api_call("GET", f"/me/messages/{message_id}")
    print(json.dumps(data, indent=2))


def cmd_mail_send(to: str, subject: str, body: str, cc: str | None = None,
                  body_format: str = "Text"):
    """Send an email."""
    import base64

    recipients = [{"emailAddress": {"address": addr.strip()}} for addr in to.split(",")]
    message = {
        "subject": subject,
        "body": {
            "contentType": body_format,
            "content": body,
        },
        "toRecipients": recipients,
    }
    if cc:
        message["ccRecipients"] = [{"emailAddress": {"address": addr.strip()}} for addr in cc.split(",")]

    # Microsoft Graph sendMail requires the message in MIME or JSON with saveToSentItems
    payload = {
        "message": message,
        "saveToSentItems": "true",
    }

    _api_call("POST", "/me/sendMail", body=payload)
    print(json.dumps({"status": "sent"}))


def cmd_calendar_list(start: str | None = None, end: str | None = None):
    """List calendar events."""
    params = {
        "$top": 50,
        "$select": "id,subject,start,end,location,attendees,organizer,bodyPreview",
        "$orderby": "start/dateTime asc",
    }
    if start:
        params["startDateTime"] = start
    if end:
        params["endDateTime"] = end

    data = _api_call("GET", "/me/calendarView", params=params)
    print(json.dumps(data, indent=2))


def cmd_calendar_create(summary: str, start: str, end: str,
                        location: str | None = None, attendees: str | None = None,
                        body_text: str | None = None):
    """Create a calendar event."""
    event = {
        "subject": summary,
        "start": {"dateTime": start, "timeZone": "America/New_York"},
        "end": {"dateTime": end, "timeZone": "America/New_York"},
    }
    if location:
        event["location"] = {"displayName": location}
    if attendees:
        event["attendees"] = [
            {"emailAddress": {"address": addr.strip()}, "type": "required"}
            for addr in attendees.split(",")
        ]
    if body_text:
        event["body"] = {"content": body_text, "contentType": "text"}

    data = _api_call("POST", "/me/events", body=event)
    print(json.dumps(data, indent=2))


def cmd_contacts_list(top: int = 50):
    """List contacts."""
    params = {"$top": top, "$select": "id,displayName,emailAddresses,businessPhones,mobilePhone,companyName"}
    data = _api_call("GET", "/me/contacts", params=params)
    print(json.dumps(data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Microsoft Graph API CLI for Hermes")
    sub = parser.add_subparsers(dest="command", required=True)

    # me
    sub.add_parser("me", help="Get current user profile")

    # todo
    todo = sub.add_parser("todo", help="To Do tasks")
    todo_sub = todo.add_subparsers(dest="todo_action", required=True)

    todo_lists = todo_sub.add_parser("lists", help="List all task lists")

    todo_tasks = todo_sub.add_parser("tasks", help="List tasks in a list")
    todo_tasks.add_argument("list_id", help="Task list ID")
    todo_tasks.add_argument("--include-completed", action="store_true")

    todo_create = todo_sub.add_parser("create", help="Create a task")
    todo_create.add_argument("list_id", help="Task list ID")
    todo_create.add_argument("--title", required=True)
    todo_create.add_argument("--due")
    todo_create.add_argument("--importance", choices=["low", "normal", "high"])
    todo_create.add_argument("--body")

    todo_update = todo_sub.add_parser("update", help="Update a task")
    todo_update.add_argument("task_id", help="Task ID (or list_id/tasks/task_id)")
    todo_update.add_argument("--status", choices=["notStarted", "inProgress", "completed"])
    todo_update.add_argument("--title")
    todo_update.add_argument("--importance", choices=["low", "normal", "high"])

    # mail
    mail = sub.add_parser("mail", help="Outlook email")
    mail_sub = mail.add_subparsers(dest="mail_action", required=True)

    mail_search = mail_sub.add_parser("search", help="Search emails")
    mail_search.add_argument("query", help="OData filter (e.g. 'isRead eq false')")
    mail_search.add_argument("--top", type=int, default=20)

    mail_get = mail_sub.add_parser("get", help="Get a full email")
    mail_get.add_argument("message_id")

    mail_send = mail_sub.add_parser("send", help="Send an email")
    mail_send.add_argument("--to", required=True)
    mail_send.add_argument("--subject", required=True)
    mail_send.add_argument("--body", required=True)
    mail_send.add_argument("--cc")
    mail_send.add_argument("--body-format", choices=["Text", "HTML"], default="Text")

    # calendar
    cal = sub.add_parser("calendar", help="Calendar")
    cal_sub = cal.add_subparsers(dest="cal_action", required=True)

    cal_list = cal_sub.add_parser("list", help="List events")
    cal_list.add_argument("--start")
    cal_list.add_argument("--end")

    cal_create = cal_sub.add_parser("create", help="Create an event")
    cal_create.add_argument("--summary", required=True)
    cal_create.add_argument("--start", required=True)
    cal_create.add_argument("--end", required=True)
    cal_create.add_argument("--location")
    cal_create.add_argument("--attendees")
    cal_create.add_argument("--body")

    # contacts
    contacts = sub.add_parser("contacts", help="Contacts")
    contacts_sub = contacts.add_subparsers(dest="contacts_action", required=True)

    contacts_list = contacts_sub.add_parser("list", help="List contacts")
    contacts_list.add_argument("--top", type=int, default=50)

    args = parser.parse_args()

    if args.command == "me":
        cmd_me()
    elif args.command == "todo":
        if args.todo_action == "lists":
            cmd_todo_lists()
        elif args.todo_action == "tasks":
            cmd_todo_tasks(args.list_id, args.include_completed)
        elif args.todo_action == "create":
            cmd_todo_create(args.list_id, args.title, args.due, args.importance, args.body)
        elif args.todo_action == "update":
            cmd_todo_update(args.task_id, args.status, args.title, args.importance)
    elif args.command == "mail":
        if args.mail_action == "search":
            cmd_mail_search(args.query, args.top)
        elif args.mail_action == "get":
            cmd_mail_get(args.message_id)
        elif args.mail_action == "send":
            cmd_mail_send(args.to, args.subject, args.body, args.cc, args.body_format)
    elif args.command == "calendar":
        if args.cal_action == "list":
            cmd_calendar_list(args.start, args.end)
        elif args.cal_action == "create":
            cmd_calendar_create(args.summary, args.start, args.end, args.location, args.attendees, args.body)
    elif args.command == "contacts":
        if args.contacts_action == "list":
            cmd_contacts_list(args.top)


if __name__ == "__main__":
    main()
