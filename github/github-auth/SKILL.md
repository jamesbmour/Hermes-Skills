---
name: github-auth
description: "GitHub auth setup: HTTPS tokens, SSH keys, gh CLI login."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Authentication, Git, gh-cli, SSH, Setup]
    related_skills: [github-pr-workflow, github-code-review, github-issues, github-repo-management]
---

# GitHub Authentication Setup

This skill sets up authentication so the agent can work with GitHub repositories, PRs, issues, and CI. It covers two paths:

- **`git` (always available)** — uses HTTPS personal access tokens or SSH keys
- **`gh` CLI (if installed)** — richer GitHub API access with a simpler auth flow

## Detection Flow

When a user asks you to work with GitHub, run this check first:

```bash
# Check what's available
git --version
gh --version 2>/dev/null || echo "gh not installed"

# Check if already authenticated
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
```

**Decision tree:**
1. If `gh auth status` shows authenticated → you're good, use `gh` for everything
2. If `gh` is installed but not authenticated → use "gh auth" method below
3. If `gh` is not installed → use "git-only" method below (no sudo needed)

---

## Method 1: Git-Only Authentication (No gh, No sudo)

This works on any machine with `git` installed. No root access needed.

### Option A: HTTPS with Personal Access Token (Recommended)

This is the most portable method — works everywhere, no SSH config needed.

**Step 1: Create a personal access token**

Tell the user to go to: **https://github.com/settings/tokens**

- Click "Generate new token (classic)"
- Give it a name like "hermes-agent"
- Select scopes:
  - `repo` (full repository access — read, write, push, PRs)
  - `workflow` (trigger and manage GitHub Actions)
  - `read:org` (if working with organization repos)
- Set expiration (90 days is a good default)
- Copy the token — it won't be shown again

**Step 2: Configure git to store the token**

```bash
# Set up the credential helper to cache credentials
# "store" saves to ~/.git-credentials in plaintext (simple, persistent)
git config --global credential.helper store

# Now do a test operation that triggers auth — git will prompt for credentials
# Username: <their-github-username>
# Password: <paste the personal access token, NOT their GitHub password>
git ls-remote https://github.com/<their-username>/<any-repo>.git
```

After entering credentials once, they're saved and reused for all future operations.

**Alternative: cache helper (credentials expire from memory)**

```bash
# Cache in memory for 8 hours (28800 seconds) instead of saving to disk
git config --global credential.helper 'cache --timeout=28800'
```

**Alternative: set the token directly in the remote URL (per-repo)**

```bash
# Embed token in the remote URL (avoids credential prompts entirely)
git remote set-url origin https://<username>:<token>@github.com/<owner>/<repo>.git
```

**Step 3: Configure git identity**

```bash
# Required for commits — set name and email
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

**Step 4: Verify**

```bash
# Test push access (this should work without any prompts now)
git ls-remote https://github.com/<their-username>/<any-repo>.git

# Verify identity
git config --global user.name
git config --global user.email
```

### Option B: SSH Key Authentication

Good for users who prefer SSH or already have keys set up.

**Step 1: Check for existing SSH keys**

```bash
ls -la ~/.ssh/id_*.pub 2>/dev/null || echo "No SSH keys found"
```

**Step 2: Generate a key if needed**

```bash
# Generate an ed25519 key (modern, secure, fast)
ssh-keygen -t ed25519 -C "their-email@example.com" -f ~/.ssh/id_ed25519 -N ""

# Display the public key for them to add to GitHub
cat ~/.ssh/id_ed25519.pub
```

Tell the user to add the public key at: **https://github.com/settings/keys**
- Click "New SSH key"
- Paste the public key content
- Give it a title like "hermes-agent-<machine-name>"

**Step 3: Test the connection**

```bash
ssh -T git@github.com
# Expected: "Hi <username>! You've successfully authenticated..."
```

**Step 4: Configure git to use SSH for GitHub**

```bash
# Rewrite HTTPS GitHub URLs to SSH automatically
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**Step 5: Configure git identity**

```bash
git config --global user.name "Their Name"
git config --global user.email "their-email@example.com"
```

---

## Method 2: gh CLI Authentication

If `gh` is installed, it handles both API access and git credentials in one step.

### Interactive Browser Login (Desktop)

```bash
gh auth login
# Select: GitHub.com
# Select: HTTPS
# Authenticate via browser
```

### Token-Based Login (Headless / SSH Servers)

```bash
echo "<THEIR_TOKEN>" | gh auth login --with-token

# Set up git credentials through gh
gh auth setup-git
```

### Verify

```bash
gh auth status
```

---

## Using the GitHub API Without gh

When `gh` is not available, you can still access the full GitHub API using `curl` with a personal access token. This is how the other GitHub skills implement their fallbacks.

### Setting the Token for API Calls

```bash
# Option 1: Export as env var (preferred — keeps it out of commands)
export GITHUB_TOKEN="<token>"

# Then use in curl calls:
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user
```

### Extracting the Token from Git Credentials

If git credentials are already configured (via credential.helper store), the token can be extracted:

```bash
# Read from git credential store
grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|'
```

### Helper: Detect Auth Method

Use this pattern at the start of any GitHub workflow:

```bash
# Try gh first, fall back to git + curl
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  echo "AUTH_METHOD=gh"
elif [ -n "$GITHUB_TOKEN" ]; then
  echo "AUTH_METHOD=curl"
elif _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
  export GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
  echo "AUTH_METHOD=curl"
elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
  export GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
  echo "AUTH_METHOD=curl"
else
  echo "AUTH_METHOD=none"
  echo "Need to set up authentication first"
fi
```

---

## Fine-Grained Personal Access Tokens

Fine-grained PATs (prefix `github_pat_`) are GitHub's recommended token type. They differ from classic tokens (prefix `ghp_`) in important ways:

- **Repository-scoped**: You must explicitly select which repos the token can access
- **Permission-based**: Instead of broad scopes like `repo`, you grant individual permissions (Contents, Issues, Pull requests, Metadata, etc.) per repo
- **Read/write granularity**: Each permission can be Read-only or Read and Write

### Creating a Fine-Grained PAT

Tell the user to go to: **https://github.com/settings/tokens?type=beta**

- Under **Repository access**, select **Only select repositories** → choose the target repo(s)
- Under **Repository permissions**:
  - **Contents**: Read and Write (required for git push)
  - **Metadata**: Read (automatically required, always grant)
  - **Pull requests**: Read and Write (if the workflow involves PRs)
  - **Workflows**: Read and Write (if touching GitHub Actions files)

### Diagnosing Fine-Grained PAT Permission Issues

**Symptom**: Token authenticates via API (`/user` returns correct login, `/repos/{owner}/{repo}` returns repo details) but `git push` returns 403 "Permission denied" or "Resource not accessible by personal access token."

**Root cause**: The token was created without `Contents: Write` permission for the target repository.

**Diagnostic command** — check token permissions BEFORE attempting push:

```bash
# Check if token can write to the repo
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO | python3 -c "
import sys, json
d = json.load(sys.stdin)
p = d.get('permissions', {})
print(f'admin={p.get(\"admin\")}, push={p.get(\"push\")}, pull={p.get(\"pull\")}')
"

# Test write access via the Contents API (creates then we can delete)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"test write","content":"dGVzdA=="}' \
  https://api.github.com/repos/$OWNER/$REPO/contents/_test_write.md
# If response contains "content" → write works. Clean up with a DELETE.
# If response contains "Resource not accessible" → token lacks Contents: Write permission
```

**Fix**: Have the user edit the token at https://github.com/settings/tokens (find the fine-grained token → Edit → Repository permissions → Contents → Read and Write) or create a new one.

### Git Credential Helper with Fine-Grained PATs

Fine-grained PATs work with the standard `credential.helper store` method, but the credential URL format matters:

```bash
# ✅ Correct — use x-access-token as the "username" (works for fine-grained PATs)
echo "https://x-access-token:$TOKEN@github.com" > ~/.git-credentials

# ❌ May fail — using the GitHub username can cause auth confusion with fine-grained PATs
echo "https://jamesbmour:$TOKEN@github.com" > ~/.git-credentials
```

**Alternative**: Embed token directly in the remote URL (per-repo, avoids credential helper issues):

```bash
git remote set-url origin https://x-access-token:$TOKEN@github.com/$OWNER/$REPO.git
```

## Installing gh CLI Without Sudo

When `gh` is not installed and you don't have root access, install it as a local binary:

```bash
GH_VERSION="2.65.0"
ARCH=$(dpkg --print-architecture 2>/dev/null || echo "amd64")
case "$ARCH" in
  amd64) GH_ARCH="linux_amd64" ;;
  arm64) GH_ARCH="linux_arm64" ;;
  *) GH_ARCH="linux_${ARCH}" ;;
esac
curl -fsSL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_${GH_ARCH}.tar.gz" -o /tmp/gh.tar.gz
tar -xzf /tmp/gh.tar.gz -C /tmp
mkdir -p ~/.local/bin
cp /tmp/gh_${GH_VERSION}_${GH_ARCH}/bin/gh ~/.local/bin/gh
chmod +x ~/.local/bin/gh
export PATH="$HOME/.local/bin:$PATH"
gh --version
```

Then authenticate with: `echo "<TOKEN>" | gh auth login --with-token && gh auth setup-git`

**Helper script**: `scripts/check-token-permissions.sh` — runs the full diagnostic flow (auth check, permission check, write test) for any repo. Usage: `bash scripts/check-token-permissions.sh <owner>/<repo>`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `git push` asks for password | GitHub disabled password auth. Use a personal access token as the password, or switch to SSH |
| `remote: Permission to X denied` (classic token) | Token may lack `repo` scope — regenerate with correct scopes |
| `remote: Permission to X denied` (fine-grained PAT, `github_pat_` prefix) | Token has `Contents: Read` but not `Contents: Write` — edit token at https://github.com/settings/tokens and grant Write permission for the target repo |
| `Resource not accessible by personal access token` | Same as above — fine-grained PAT lacks the specific write permission. Run the diagnostic curl above to confirm |
| Token works via API but push returns 403 | Fine-grained PAT authenticates but lacks repo-level write permission. Check `permissions.push` in the API response — if `false`, the token needs to be recreated with `Contents: Read and Write` |
| `fatal: Authentication failed` | Cached credentials may be stale — run `git credential reject` then re-authenticate |
| `ssh: connect to host github.com port 22: Connection refused` | Try SSH over HTTPS port: add `Host github.com` with `Port 443` and `Hostname ssh.github.com` to `~/.ssh/config` |
| Credentials not persisting | Check `git config --global credential.helper` — must be `store` or `cache` |
| Multiple GitHub accounts | Use SSH with different keys per host alias in `~/.ssh/config`, or per-repo credential URLs |
| `gh: command not found` + no sudo | Install gh locally (see "Installing gh CLI Without Sudo" above) or use git-only Method 1 |
