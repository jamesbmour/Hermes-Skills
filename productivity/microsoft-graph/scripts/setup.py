#!/usr/bin/env python3
"""Microsoft Graph API OAuth2 setup for Hermes Agent.

Uses the device code flow — fully headless, no browser redirects needed.
The user registers an Azure AD app, provides tenant + client ID, then enters
a short code at aka.ms/devicelogin. Token auto-refreshes thereafter.

Commands:
  setup.py --check                          # Is auth valid? Exit 0 = yes, 1 = no
  setup.py --configure TENANT CLIENT_ID     # Store Azure AD app credentials
  setup.py --auth                           # Start device code flow
  setup.py --revoke                         # Delete stored token
  setup.py --install-deps                   # Install Python dependencies

Agent workflow:
  1. Run --check. If exit 0, auth is good — skip setup.
  2. Ask user for tenant ID and client ID. Run --configure TENANT CLIENT_ID.
  3. Run --auth. Send the device code + URL to the user.
  4. User visits aka.ms/devicelogin, enters the code.
  5. Script polls and saves the token automatically.
  6. Run --check to verify. Done.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Ensure sibling modules (_hermes_home) are importable when run standalone.
_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

# Try to import _hermes_home; if not available, use a fallback
try:
    from _hermes_home import display_hermes_home, get_hermes_home
    HERMES_HOME = get_hermes_home()
except ImportError:
    HERMES_HOME = Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))
    def display_hermes_home():
        return str(HERMES_HOME)

TOKEN_PATH = HERMES_HOME / "msgraph_token.json"
CONFIG_PATH = HERMES_HOME / "msgraph_config.json"

# Microsoft Graph scopes
SCOPES = [
    "Tasks.ReadWrite",       # To Do
    "Mail.Read",             # Outlook read
    "Mail.Send",             # Outlook send
    "Calendars.ReadWrite",   # Calendar
    "Contacts.Read",         # People/Contacts
    "User.Read",             # Basic profile
    "Files.ReadWrite",       # OneDrive + SharePoint files
    "Sites.Read.All",        # SharePoint sites
    "Chat.ReadWrite",        # Teams chat
    "People.Read",           # Org directory
]

REQUIRED_PACKAGES = ["msal"]

# Microsoft device code endpoints
TENANT = "common"  # default, overridden by config
AUTHORITY_URL = "https://login.microsoftonline.com/{tenant}"
DEVICE_CODE_URL = "/oauth2/v2.0/devicecode"
TOKEN_URL = "/oauth2/v2.0/token"


def _load_config() -> dict:
    """Load stored Azure AD config."""
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_config(tenant: str, client_id: str):
    """Save Azure AD app credentials."""
    CONFIG_PATH.write_text(json.dumps({
        "tenant": tenant,
        "client_id": client_id,
    }, indent=2))


def _load_token() -> dict:
    """Load stored token."""
    if TOKEN_PATH.exists():
        try:
            return json.loads(TOKEN_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_token(token_data: dict):
    """Save token to disk."""
    TOKEN_PATH.write_text(json.dumps(token_data, indent=2))


def install_deps():
    """Install msal if missing. Returns True on success."""
    try:
        import msal  # noqa: F401
        print("Dependencies already installed.")
        return True
    except ImportError:
        pass

    print("Installing msal...")

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet"] + REQUIRED_PACKAGES,
            stdout=subprocess.DEVNULL,
        )
        print("Dependencies installed.")
        return True
    except subprocess.CalledProcessError:
        pass

    # Fallback: uv
    import shutil
    uv = shutil.which("uv")
    if uv:
        try:
            subprocess.check_call(
                [uv, "pip", "install", "--python", sys.executable, "--quiet"]
                + REQUIRED_PACKAGES,
                stdout=subprocess.DEVNULL,
            )
            print("Dependencies installed.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install via uv: {e}")
            return False

    print("ERROR: Could not install msal. Install manually: pip install msal")
    return False


def _ensure_deps():
    """Check deps, install if not, exit on failure."""
    try:
        import msal  # noqa: F401
    except ImportError:
        if not install_deps():
            sys.exit(1)


def check_auth(quiet: bool = False):
    """Check if stored credentials are valid. Returns True/False."""
    if not TOKEN_PATH.exists():
        if not quiet:
            print(f"NOT_AUTHENTICATED: No token at {TOKEN_PATH}")
        return False

    config = _load_config()
    if not config.get("client_id"):
        if not quiet:
            print("NOT_CONFIGURED: No Azure AD app configured. Run --configure first.")
        return False

    _ensure_deps()
    import msal

    token_data = _load_token()
    client_id = config["client_id"]
    tenant = config.get("tenant", "common")
    authority = AUTHORITY_URL.format(tenant=tenant)

    app = msal.PublicClientApplication(
        client_id,
        authority=authority,
        token_cache=msal.SerializableTokenCache(),
    )

    # Check if we have accounts in the cache
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            _save_token(result)
            if not quiet:
                print(f"AUTHENTICATED: Token valid at {TOKEN_PATH}")
            return True

    # Try refresh if we have a refresh token
    if token_data.get("refresh_token"):
        result = app.acquire_token_by_refresh_token(
            token_data["refresh_token"],
            SCOPES,
        )
        if result and "access_token" in result:
            _save_token(result)
            if not quiet:
                print(f"AUTHENTICATED: Token refreshed at {TOKEN_PATH}")
            return True

    if not quiet:
        print("TOKEN_INVALID: Re-run setup with --auth.")
    return False


def configure(tenant: str, client_id: str):
    """Store Azure AD app credentials."""
    _save_config(tenant, client_id)
    print(f"OK: Configuration saved to {CONFIG_PATH}")
    print(f"  Tenant: {tenant}")
    print(f"  Client ID: {client_id}")


PENDING_AUTH_PATH = HERMES_HOME / "msgraph_pending.json"


def start_device_flow():
    """Start device code flow. Prints code + URL, polls for completion."""
    config = _load_config()
    if not config.get("client_id"):
        print("ERROR: No Azure AD app configured. Run --configure TENANT CLIENT_ID first.")
        print("")
        print("To get these values:")
        print("  1. Go to https://portal.azure.com → App registrations → New registration")
        print("  2. Name: 'Hermes Agent' (or anything)")
        print("  3. Supported account types: 'Accounts in any organizational directory'")
        print("  4. Redirect URI: leave blank (device code flow doesn't need it)")
        print("  5. Click Register")
        print("  6. Copy the Application (client) ID")
        print("  7. Copy the Directory (tenant) ID (or use 'common' for multi-tenant)")
        print("")
        print("  Then run: setup.py --configure <tenant> <client_id>")
        sys.exit(1)

    _ensure_deps()
    import msal

    tenant = config.get("tenant", "common")
    client_id = config["client_id"]
    authority = AUTHORITY_URL.format(tenant=tenant)

    app = msal.PublicClientApplication(client_id, authority=authority)

    # Start device flow
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "error" in flow:
        print(f"ERROR: {flow.get('error_description', flow['error'])}")
        sys.exit(1)

    # Print the instructions for the user
    print(json.dumps({
        "user_code": flow["user_code"],
        "verification_uri": flow["verification_uri"],
        "message": flow.get("message", ""),
        "expires_in": flow.get("expires_in", 900),
    }))

    # Poll for token
    print("Waiting for authentication...", file=sys.stderr)
    result = app.acquire_token_by_device_flow(flow)

    if "error" in result:
        print(f"ERROR: Authentication failed: {result.get('error_description', result['error'])}")
        sys.exit(1)

    _save_token(result)
    PENDING_AUTH_PATH.unlink(missing_ok=True)
    print(f"OK: Authenticated. Token saved to {TOKEN_PATH}")
    print(f"Profile-scoped token location: {display_hermes_home()}/msgraph_token.json")


def auth_start():
    """Initiate device code flow and save state for later polling."""
    config = _load_config()
    if not config.get("client_id"):
        print("ERROR: No Azure AD app configured. Run --configure TENANT CLIENT_ID first.")
        sys.exit(1)

    _ensure_deps()
    import msal

    tenant = config.get("tenant", "common")
    client_id = config["client_id"]
    authority = AUTHORITY_URL.format(tenant=tenant)

    app = msal.PublicClientApplication(client_id, authority=authority)

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "error" in flow:
        print(f"ERROR: {flow.get('error_description', flow['error'])}")
        sys.exit(1)

    # Save flow state for later polling
    PENDING_AUTH_PATH.write_text(json.dumps({
        "device_code": flow["device_code"],
        "interval": flow.get("interval", 5),
        "expires_at": int(time.time()) + flow.get("expires_in", 900),
        "user_code": flow["user_code"],
        "verification_uri": flow["verification_uri"],
        "message": flow.get("message", ""),
    }, indent=2))

    print(json.dumps({
        "user_code": flow["user_code"],
        "verification_uri": flow["verification_uri"],
        "message": flow.get("message", ""),
        "expires_in": flow.get("expires_in", 900),
    }))


def auth_poll():
    """Poll for device code completion using saved state."""
    if not PENDING_AUTH_PATH.exists():
        print("ERROR: No pending auth session. Run --auth-start first.")
        sys.exit(1)

    pending = json.loads(PENDING_AUTH_PATH.read_text())
    device_code = pending["device_code"]
    interval = pending.get("interval", 5)
    expires_at = pending.get("expires_at", 0)

    if time.time() > expires_at:
        print("ERROR: Device code expired. Run --auth-start for a new code.")
        PENDING_AUTH_PATH.unlink(missing_ok=True)
        sys.exit(1)

    config = _load_config()
    _ensure_deps()
    import msal

    tenant = config.get("tenant", "common")
    client_id = config["client_id"]
    authority = AUTHORITY_URL.format(tenant=tenant)

    app = msal.PublicClientApplication(client_id, authority=authority)

    # Poll with timeout
    deadline = time.time() + 120  # 2 minute max poll
    while time.time() < deadline and time.time() < expires_at:
        result = app.acquire_token_by_device_flow({
            "device_code": device_code,
            "interval": interval,
            "expires_in": int(expires_at - time.time()),
        })

        if "access_token" in result:
            _save_token(result)
            PENDING_AUTH_PATH.unlink(missing_ok=True)
            print(f"OK: Authenticated. Token saved to {TOKEN_PATH}")
            print(f"Profile-scoped token location: {display_hermes_home()}/msgraph_token.json")
            return

        error = result.get("error", "")
        if error == "authorization_pending":
            time.sleep(interval)
            continue
        elif error == "slow_down":
            interval += 1
            time.sleep(interval)
            continue
        elif error == "expired_token":
            print("ERROR: Code expired. Run --auth-start for a new code.")
            PENDING_AUTH_PATH.unlink(missing_ok=True)
            sys.exit(1)
        else:
            print(f"ERROR: {result.get('error_description', error)}")
            PENDING_AUTH_PATH.unlink(missing_ok=True)
            sys.exit(1)

    print("ERROR: Polling timed out. The code may still be valid — run --auth-poll again.")
    sys.exit(1)


def revoke():
    """Delete stored token and config."""
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
        print(f"Deleted {TOKEN_PATH}")
    else:
        print("No token to delete.")

    # Don't delete config — it's harmless and saves re-entry


def main():
    parser = argparse.ArgumentParser(description="Microsoft Graph OAuth setup for Hermes")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check if auth is valid (exit 0=yes, 1=no)")
    group.add_argument("--configure", nargs=2, metavar=("TENANT", "CLIENT_ID"),
                       help="Store Azure AD app credentials")
    group.add_argument("--auth", action="store_true", help="Start device code authentication flow")
    group.add_argument("--auth-start", action="store_true", help="Initiate device code flow (prints code + URL, saves state)")
    group.add_argument("--auth-poll", action="store_true", help="Poll for token completion (run after user enters the code)")
    group.add_argument("--revoke", action="store_true", help="Delete stored token")
    group.add_argument("--install-deps", action="store_true", help="Install Python dependencies")
    args = parser.parse_args()

    if args.check:
        sys.exit(0 if check_auth() else 1)
    elif args.configure:
        configure(args.configure[0], args.configure[1])
    elif args.auth:
        start_device_flow()
    elif args.auth_start:
        auth_start()
    elif args.auth_poll:
        auth_poll()
    elif args.revoke:
        revoke()
    elif args.install_deps:
        sys.exit(0 if install_deps() else 1)


if __name__ == "__main__":
    main()
