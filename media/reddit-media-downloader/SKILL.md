---
name: reddit-media-downloader
description: >
  Download all pictures and videos from a CSV of Reddit saved/upvoted posts.
  Handles redgifs (API v2), i.redd.it (direct), v.redd.it (reddit-hosted video),
  reddit.com/gallery (image galleries via HTML scraping), and imgchest.com (gallery scrape).
  Use when the user has a CSV/list of Reddit post URLs and wants to download all
  associated media files. Triggers: "download from reddit CSV", "save reddit posts",
  "download redgifs videos", "bulk download reddit media", "download saved reddit posts".
---

# Reddit Media Downloader

Download all pics and videos from a CSV (or list) of Reddit posts, handling every
major media host that appears in saved/upvoted Reddit exports.

## Source Types & Handlers

| Source | Host Pattern | Media Type | Handler |
|--------|-------------|------------|---------|
| redgifs | `*.redgifs.com` | video (mp4) | API v2 → direct download |
| i.redd.it | `i.redd.it` | image/gif | direct download |
| v.redd.it | `v.redd.it` | video (mp4) | HTML scrape → CMAF/DASH download |
| reddit gallery | `reddit.com/gallery/*` | images | HTML scrape → i.redd.it download |
| imgchest | `imgchest.com/p/*` | images | gallery page scrape |
| text-only | "No text found" | none | skip |

## Quick Start

```bash
# The script is a self-contained Python file. Copy it and run:
python3 download_reddit_media.py --csv "path/to/posts.csv" --out ~/Downloads/reddit_media --workers 4

# Dry run (classify sources without downloading):
python3 download_reddit_media.py --csv posts.csv --dry-run

# Limit to N rows for testing:
python3 download_reddit_media.py --csv posts.csv --limit 10
```

The script skips files that already exist (resume-safe). Re-run anytime to
retry failures or pick up entries that were temporarily blocked.

## Key API Details (see references/ for full detail)

### Redgifs API v2
- Auth: `GET https://api.redgifs.com/v2/auth/temporary` (NOT `/temporary_token`)
- Must include `Origin: https://www.redgifs.com` and `Referer: https://www.redgifs.com/`
- Token lasts ~1 day; refresh hourly to be safe
- GIF info: `GET https://api.redgifs.com/v2/gifs/{id}` with `Authorization: Bearer {token}`
- Quality: `urls.hd` > `urls.sd` > `urls.gif`
- 410 Gone = video deleted (unrecoverable)

### Reddit (galleries + v.redd.it)
- Reddit's JSON API (`.json` endpoints) is aggressively blocked (403) for unauthenticated requests
- Workaround: scrape `https://www.reddit.com/api/info?id=t3_{post_id}` HTML for `preview.redd.it/{media_id}.{ext}` URLs
- Gallery images: extract media IDs from `preview.redd.it` URLs → download from `https://i.redd.it/{media_id}.jpg`
- v.redd.it videos: extract `CMAF_{res}.mp4` URLs from HTML → download highest available resolution
- Post ID: extract from reddit comments URL via `/comments/(\w+)/` regex

### Imgchest
- Gallery page HTML contains image URLs in `file_url` JSON or `src` attributes
- URLs may be concatenated with text (e.g., "Chapter 1: https://imgchest.com/p/ID123Chapter 2: ...")
- Use regex `imgchest\.com/p/([a-z0-9]{10,15})` to extract IDs (NOT `\w+` which captures trailing text)

## Pitfalls

1. **Reddit IP blocking**: Running 4+ parallel threads against Reddit's API triggers a 403 IP block lasting 5+ minutes. Add retry with exponential backoff (10s, 20s, 30s). Consider serial processing for Reddit-only entries.

2. **Redgifs token thread-safety**: When using multiple workers, protect the shared token with a threading.Lock. Multiple threads fetching tokens simultaneously causes auth failures.

3. **Imgchest URL concatenation**: IFTTT-style CSV exports sometimes concatenate multiple imgchest URLs with surrounding text. The greedy `\w+` regex captures trailing words like "Chapter". Use `[a-z0-9]{10,15}` instead.

4. **v.redd.it video quality**: DASH format URLs require signed parameters from the DASH playlist. CMAF URLs are unsigned but limited to 480p/360p. Prefer DASH if available, fall back to CMAF.

5. **Redgifs URL variants**: URLs come as `redgifs.com/watch/{id}`, `v3.redgifs.com/watch/{id}`, `v3.redgifs.com/ifr/{id}`, and with trailing `/?7/` suffixes. The regex `redgifs\.com/(?:watch|ifr)/([A-Za-z0-9]+)` handles all variants.

6. **CSV column misspelling**: The IFTTT export uses "comunity" (not "community") as a column header. Don't rely on correct spelling.

## File Structure

```
reddit-media-downloader/
├── SKILL.md                         (this file)
├── templates/
│   └── download_reddit_media.py     (ready-to-run script)
└── references/
    └── api-details.md               (per-host API notes, rate limits, auth flows)
```

## Output

Files are named by the post title (sanitized, max 120 chars), with `_{N}` suffix for multi-image galleries. All files go to a single flat output directory.