#!/bin/bash
# Check GitHub token permissions for a specific repo.
# Usage: check-token-permissions.sh <owner>/<repo>
# Requires GITHUB_TOKEN env var (or reads from ~/.hermes/.env)
#
# Exit codes:
#   0 = token has write access
#   1 = token is read-only or invalid
#   2 = token missing or not authenticated

set -euo pipefail

REPO="${1:-}"
if [ -z "$REPO" ]; then
  echo "Usage: $0 <owner>/<repo>"
  exit 2
fi

# Resolve token
if [ -z "${GITHUB_TOKEN:-}" ]; then
  ENV_FILE="${HERMES_HOME:-$HOME/.hermes}/.env"
  if [ -f "$ENV_FILE" ]; then
    GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2 | tr -d '\n\r')
  fi
fi

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "ERROR: No GITHUB_TOKEN found. Set it as env var or in ~/.hermes/.env"
  exit 2
fi

echo "Checking token permissions for $REPO..."
echo ""

# Check user authentication
USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin).get('login','UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
echo "Authenticated as: $USER"

# Check repo permissions
PERMS=$(curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$REPO" | python3 -c "
import sys, json
d = json.load(sys.stdin)
p = d.get('permissions', {})
if not p:
    print('ERROR: ' + d.get('message', 'Could not fetch repo info'))
else:
    print(f'admin={p.get(\"admin\")}, push={p.get(\"push\")}, pull={p.get(\"pull\")}')
" 2>/dev/null)
echo "Repo permissions: $PERMS"

# Test write via Contents API
echo ""
echo "Testing write access..."
WRITE_TEST=$(curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"permission test","content":"dGVzdA=="}' \
  "https://api.github.com/repos/$REPO/contents/_test_write.md")

if echo "$WRITE_TEST" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if 'content' in d else 1)" 2>/dev/null; then
  echo "Write access: YES"
  # Clean up test file
  SHA=$(echo "$WRITE_TEST" | python3 -c "import sys,json; print(json.load(sys.stdin)['content']['sha'])" 2>/dev/null)
  if [ -n "$SHA" ]; then
    curl -s -X DELETE \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"message\":\"cleanup\",\"sha\":\"$SHA\"}" \
      "https://api.github.com/repos/$REPO/contents/_test_write.md" > /dev/null 2>&1
    echo "Cleaned up test file."
  fi
  exit 0
else
  ERROR_MSG=$(echo "$WRITE_TEST" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message','unknown'))" 2>/dev/null || echo "unknown")
  echo "Write access: NO"
  echo "Error: $ERROR_MSG"
  echo ""
  echo "If 'Resource not accessible by personal access token':"
  echo "  → Fine-grained PAT lacks Contents: Write permission."
  echo "  → Edit at: https://github.com/settings/tokens"
  echo "  → Repository permissions → Contents → Read and Write"
  exit 1
fi