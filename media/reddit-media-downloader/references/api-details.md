# Reddit Media Downloader — API Reference

## Redgifs API v2

### Authentication
```
GET https://api.redgifs.com/v2/auth/temporary
Headers:
  User-Agent: Mozilla/5.0 ...
  Origin: https://www.redgifs.com
  Referer: https://www.redgifs.com/
```
Response:
```json
{"token": "eyJ0eX...o9TA", "addr": "74.134.74.177", "agent": "Mozilla/5.0", "session": "..."}
```
- Endpoint is `/v2/auth/temporary` — NOT `/v2/auth/temporary_token` (that returns 404).
- Token lasts approximately 1 day. Refresh hourly to be safe.
- No `expires` field in the response (unlike older API versions).

### Fetching GIF info
```
GET https://api.redgifs.com/v2/gifs/{gif_id}
Headers:
  Authorization: Bearer {token}
  User-Agent: Mozilla/5.0 ...
  Origin: https://www.redgifs.com
  Referer: https://www.redgifs.com/
```
Response `gif.urls` object:
```json
{
  "hd": "https://media.redgifs.com/SomeId.mp4",
  "sd": "https://media.redgifs.com/SomeId-mobile.mp4",
  "gif": "https://media.redgifs.com/SomeId.gif",
  "thumbnail": "https://media.redgifs.com/SomeId-mobile.jpg",
  "poster": "https://media.redgifs.com/SomeId-poster.jpg"
}
```
- Prefer `hd` quality. Fall back to `sd`, then `gif`.
- Download the video URL directly (no auth needed for media.redgifs.com downloads).

### Error codes
- 410 Gone: video deleted from redgifs. Unrecoverable.
- 401 Unauthorized: token expired. Re-fetch token and retry.
- 429 Too Many Requests: rate limited. Wait 5s and retry.

### URL ID extraction
URL variants seen in the wild:
- `https://www.redgifs.com/watch/{id}`
- `https://redgifs.com/watch/{id}`
- `https://v3.redgifs.com/watch/{id}`
- `https://v3.redgifs.com/ifr/{id}`
- `https://www.redgifs.com/ifr/{id}`
- With trailing `/?7/` suffix (IFTTT artifact)

Regex that handles all: `redgifs\.com/(?:watch|ifr)/([A-Za-z0-9]+)`

## Reddit JSON API (blocked for unauthenticated use)

### The problem
As of 2025+, Reddit aggressively blocks unauthenticated requests to:
- `https://www.reddit.com/comments/{id}.json`
- `https://www.reddit.com/api/info.json?id=t3_{id}`
- `https://old.reddit.com/...`

Returns 403 with HTML "You've been blocked by network security" page.
This happens for both curl and headless browsers (same IP block).
Block duration: 5+ minutes after hitting ~10 requests.

### Workaround: HTML scraping of api/info
```
GET https://www.reddit.com/api/info?id=t3_{post_id}
Headers:
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36
  Accept: text/html,...
```
This returns the old-reddit HTML page (not JSON), which contains embedded media URLs.

### Extracting gallery image IDs from HTML
The HTML contains `preview.redd.it/{media_id}.{ext}` URLs.
Regex: `preview\.redd\.it/(\w+)\.\w+`
Deduplicate the list, then download each from `https://i.redd.it/{media_id}.jpg`.

### Extracting v.redd.it video URLs from HTML
The HTML contains `CMAF_{resolution}.mp4` URLs.
Regex: `https?://v\.redd\.it/\w+/CMAF_\d+\.mp4`
Also try DASH format: `https?://v\.redd\.it/\w+/DASH_\d+\.mp4`

CMAF URLs are unsigned and work directly. DASH URLs may require signed parameters.
Available CMAF resolutions: typically 480, 360 (higher res like 720/1080 returns 403).

### Post ID extraction
From reddit comments URL: `/comments/(\w+)/`
From gallery URL: `reddit\.com/gallery/(\w+)`
The CSV's `url` column contains the full reddit comments URL which has the post ID.

## Imgchest

### URL pattern
`https://imgchest.com/p/{page_id}`
Page IDs are lowercase alphanumeric, 10-15 chars.

### Parsing concatenated URLs
IFTTT exports sometimes concatenate URLs with surrounding text:
```
Chapter 1: https://imgchest.com/p/ne7bw3nkg75Chapter 2: https://imgchest.com/p/na7kprpdb48
```
Correct regex: `imgchest\.com/p/([a-z0-9]{10,15})`
Wrong regex: `https://imgchest\.com/p/\w+` (captures trailing "Chapter" text)

### Image extraction from gallery page
Fetch the gallery page HTML and extract image URLs:
- `file_url` in embedded JSON: `"file_url"\s*:\s*"(https?://[^"]+)"`
- `src` attributes: `src="(https://(?:cdn|media|images?)\.imgchest\.com/[^"]+)"`
- `og:image` meta: `og:image"\s*content="(https://[^"]+)"`
- Lazy-loaded: `data-src="(https://[^"]+)"` (filter for image extensions)

## IFTTT CSV Export Format

Columns: `Date, Title, Source, comunity, url`
- `Source` column: the direct media URL (redgifs, i.redd.it, etc.) or text content
- `comunity` is misspelled (not "community")
- `url` column: the reddit comments URL (useful for extracting post IDs)
- Text-only posts have "No text found" in the Source column
- Some Source fields contain multiple URLs concatenated without spaces