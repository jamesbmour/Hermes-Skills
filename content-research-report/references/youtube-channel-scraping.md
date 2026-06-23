# YouTube Channel Scraping via ytInitialData

When `yt-dlp` is slow, unavailable, or returns incomplete metadata, scrape the
channel's `/videos` page directly and parse the embedded `ytInitialData` JSON.

## When to Use This Instead of yt-dlp

- `yt-dlp --flat-playlist --dump-single-json` times out or returns empty
- You need video titles + IDs quickly without a 30s+ wait
- `yt-dlp` is not installed and installing it would break flow
- You need the channel description/keywords (available in `channelMetadataRenderer`)

## Step-by-Step Technique

### 1. Fetch the channel videos page

```bash
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' \
  'https://www.youtube.com/@CHANNELNAME/videos' > /tmp/channel.html
```

The page is ~1MB. Save to a file rather than piping — you'll parse it in Python.

### 2. Extract ytInitialData

The page contains a `<script>` tag with `ytInitialData = {...};`. Extract it:

```python
import re
html = open('/tmp/channel.html').read()
m = re.search(r'ytInitialData\s*=\s*(\{.*?\})\s*;', html)
raw = m.group(1)  # ~400KB JSON
```

**Use `json_parse()` from `hermes_tools`** — not `json.loads()`. The raw JSON
contains control characters that strict `json.loads` rejects.

### 3. Navigate to video data

YouTube's structure has changed (2025+). The video entries are inside
`richItemRenderer` nodes, NOT the older `gridVideoRenderer` or `videoRenderer`.

```
richItemRenderer
  └─ content
     └─ lockupViewModel
        ├─ contentImage.thumbnailViewModel.image.sources[0].url  → video ID
        └─ metadata
           └─ lockupMetadataViewModel
              └─ title.content  → video title
```

Full extraction code:

```python
import re
from hermes_tools import json_parse

html = open('/tmp/channel.html').read()
m = re.search(r'ytInitialData\s*=\s*(\{.*?\})\s*;', html)
data = json_parse(m.group(1))

def find_keys(obj, key):
    """Recursively find all values for a given key."""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                found.append(v)
            found += find_keys(v, key)
    elif isinstance(obj, list):
        for v in obj:
            found += find_keys(v, key)
    return found

rich_items = find_keys(data, 'richItemRenderer')

for ri in rich_items:
    content = ri.get('content', {})
    lvm = content.get('lockupViewModel', {})
    md = lvm.get('metadata', {})
    tm = md.get('lockupMetadataViewModel', {})

    # Title
    title_obj = tm.get('title', {})
    title = title_obj.get('content', '') if isinstance(title_obj, dict) else ''

    # Video ID — extract from thumbnail URL
    srcs = lvm.get('contentImage', {}).get('thumbnailViewModel', {}) \
              .get('image', {}).get('sources', [])
    vid = ''
    if srcs:
        vm = re.search(r'/vi/([a-zA-Z0-9_-]{11})/', srcs[0].get('url', ''))
        if vm:
            vid = vm.group(1)

    # Views / publish date — in metadataRows
    views = pub = ''
    for row in md.get('metadataRows', []):
        for cell in row.get('metadataParts', []):
            txt = cell.get('text', {}).get('content', '')
            if 'view' in txt.lower():
                views = txt
            elif any(w in txt.lower() for w in ['ago', 'streamed', 'premiere']):
                pub = txt

    print(f"[{vid}] {title}  |  {views}  |  {pub}")
```

### 4. Extract channel metadata

Channel description, title, and keywords are in `channelMetadataRenderer`:

```python
def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r:
                return r
    return None

meta = find_key(data, 'channelMetadataRenderer')
print("Title:", meta.get('title', ''))
print("Description:", meta.get('description', ''))
print("Keywords:", meta.get('keywords', ''))
print("External ID:", meta.get('externalId', ''))
```

## Gotchas

1. **Renderer key names change** — YouTube updates their internal JSON structure.
   If `richItemRenderer` or `lockupViewModel` disappears, inspect the JSON
   structure: dump `find_keys(data, key)` for any key containing `Renderer` and
   look for where `videoId` or thumbnail URLs appear.

2. **Subscriber count often missing** — the `pageHeaderRenderer` structure
   doesn't reliably include subscriber count in the scrape. Use `yt-dlp` for
   this if needed, or skip it.

3. **30 videos per page** — the initial page load includes ~30 videos. For more,
   you'd need to follow `continuationItemRenderer` tokens (complex; consider
   `yt-dlp` for large catalogs).

4. **Regex on huge JSON** — the `.*?` in the ytInitialData regex is non-greedy
   and works because YouTube's JS has the `;` terminator. If this breaks, try
   matching to the `</script>` tag instead.