---
name: youtube-ideas
description: "Analyze a YouTube channel, research current trends, and generate fresh video ideas with titles, outlines, audience, and SEO keywords."
platforms: [linux, macos, windows]
---

# YouTube Video Ideas Generator

## When to Use

Use when the user asks to:
- Analyze a YouTube channel and generate new video ideas
- Research what content a channel should make next
- Create a content strategy report for a YouTube channel
- Generate trend-aligned video ideas with SEO keywords

## Prerequisites

This skill depends on `youtube-content` for transcript fetching. Load it first:

```
skill_view(name='youtube-content')
```

Ensure `youtube-transcript-api` is installed:
```bash
uv pip install youtube-transcript-api
```

## Workflow

### Phase 1: Channel Analysis

#### 1.1 Scrape the Channel's Videos Page

Fetch the channel's `/videos` page and extract `ytInitialData`:

```bash
curl -s -L -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36' 'https://www.youtube.com/@CHANNEL_HANDLE/videos' > /tmp/channel.html
```

Use `execute_code` with Python to parse `ytInitialData`:

```python
import re
from hermes_tools import json_parse

html = open('/tmp/channel.html').read()
m = re.search(r'ytInitialData\s*=\s*(\{.*?\})\s*;', html)
data = json_parse(m.group(1))
```

**Key insight:** YouTube's page structure changed in 2025-2026. Videos are now inside `richItemRenderer` → `content` → `lockupViewModel`. The old `gridVideoRenderer` / `videoRenderer` pattern no longer works. Navigate like this:

```python
def find_keys(obj, key):
    found = []
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k == key: found.append(v)
            found += find_keys(v, key)
    elif isinstance(obj, list):
        for v in obj: found += find_keys(v, key)
    return found

rich_items = find_keys(data, 'richItemRenderer')

for ri in rich_items:
    lvm = ri.get('content',{}).get('lockupViewModel',{})
    md = lvm.get('metadata',{}).get('lockupMetadataViewModel',{})
    title = md.get('title',{}).get('content','')
    # Extract video ID from thumbnail URL
    img = lvm.get('contentImage',{}).get('thumbnailViewModel',{}).get('image',{})
    srcs = img.get('sources',[])
    if srcs:
        vm = re.search(r'/vi/([a-zA-Z0-9_-]{11})/', srcs[0].get('url',''))
        vid = vm.group(1) if vm else ""
    # metadata rows for views/date
    rows = md.get('metadataRows',[])
    for row in rows:
        for cell in row.get('metadataParts',[]):
            txt = cell.get('text',{}).get('content','')
```

**Pitfall:** The `ytInitialData` regex `\{.*?\}` uses a non-greedy match. If the JSON is large (400K+ chars), the non-greedy match may stop too early. The regex `ytInitialData\s*=\s*(\{.*?\})\s*;` works reliably for channel pages but may need adjustment for other page types.

#### 1.2 Extract Channel Metadata

From the same `ytInitialData`, find `channelMetadataRenderer`:

```python
def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj: return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r: return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r: return r
    return None

meta = find_key(data, 'channelMetadataRenderer')
# meta['title'] — channel name
# meta['description'] — full channel description
# meta['keywords'] — channel's SEO keywords
# meta['externalId'] — UC... channel ID
```

#### 1.3 Fetch Representative Transcripts

Pick 2-3 videos spanning different content types (e.g., a tutorial, a project build, a tool intro). Use the `youtube-content` skill's fetch script:

```bash
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID" --text-only
```

Analyze transcripts for:
- **Opening style** — how does the host start videos?
- **Pacing** — dense/fast vs. relaxed/slow
- **Structure** — series-based? standalone? code-walkthrough?
- **Visual style** — IDE screen capture? slides? face cam?
- **Code sharing** — GitHub repos linked?
- **Voice** — conversational technical? formal lecture?

#### 1.4 Categorize Videos into Themes

Group the scraped video titles into thematic clusters. This reveals:
- What the channel currently covers
- What content gaps exist
- Which series are active

### Phase 2: Trend Research

#### 2.1 Hacker News Front Page

HN is the best real-time signal of developer interests:

```bash
curl -s 'https://news.ycombinator.com/' -A 'Mozilla/5.0'
```

Extract titles with regex: `class="titleline"><a href="[^"]*"[^>]*>([^<]+)</a>`

Also fetch Show HN for what people are building:
```bash
curl -s 'https://news.ycombinator.com/show' -A 'Mozilla/5.0'
```

#### 2.2 DuckDuckGo Trend Searches

Google search scraping is unreliable (bot detection). Use DuckDuckGo's HTML endpoint instead:

```bash
curl -s 'https://html.duckduckgo.com/html/?q=SEARCH+TERMS' -A 'Mozilla/5.0'
```

Extract result titles: `class="result__a"[^>]*>([^<]+)</a>`

**Recommended search queries** (adapt to channel's niche):
- `AI coding agent framework 2025 trends MCP protocol developer`
- `model context protocol MCP tutorial LangChain 2025`
- `agentic RAG graph RAG 2025 tutorial`
- `local LLM 2025 ollama tool use function calling tutorial`
- `AI coding assistant 2025 Claude Code Copilot Cursor trends`
- `computer use agent 2025 browser automation AI`
- `AI workflow automation 2025 n8n LangGraph crew AI`
- `RAG 2025 advancements trends vectordb`

#### 2.3 Synthesize Trends

Map findings into a trend heat map:
- 🔥🔥🔥 = Dominant topic (multiple HN posts + high search volume)
- 🔥🔥 = Growing topic (consistent signals)
- 🔥 = Emerging topic (early signals)
- ⚡ = Niche but important (security, ethics)

### Phase 3: Gap Analysis

Cross-reference the channel's existing video themes against current trends. Identify topics that are:
1. **Trending** (from Phase 2)
2. **Absent** from the channel's recent catalog (from Phase 1.4)
3. **Aligned** with the channel's audience and format

### Phase 4: Generate Video Ideas

For each idea, produce:

1. **Compelling title** — use the channel's naming style (action-oriented, specific)
2. **Why this idea** — trend justification + channel fit
3. **Tutorial outline** — 8-12 step walkthrough matching the channel's code-walkthrough format
4. **Target audience** — who specifically will click
5. **SEO keywords/tags** — 15+ comma-separated tags for YouTube metadata

**Idea quality checklist:**
- [ ] Topic is trending (Phase 2 evidence)
- [ ] Topic is absent from recent videos (Phase 1.4 evidence)
- [ ] Fits the channel's format (code walkthrough, GitHub repo, series-compatible)
- [ ] Has clear audience demand (search volume or HN discussion)
- [ ] Can be produced with the channel's existing tech stack (Python, Streamlit, LangChain, etc.)

### Phase 5: Prioritize & Recommend

Rank ideas by:
- **Trend heat** — how hot is the topic right now?
- **Channel fit** — how naturally does it extend existing content?
- **Production effort** — low/medium/high

Provide content strategy recommendations (series ideas, format suggestions, publishing cadence).

## Output Format

The final report should be a markdown file with these sections:

```
# CHANNEL NAME — Channel Research & Video Ideas Report

## 1. Channel Analysis
### 1.1 Channel Identity & Description
### 1.2 Content Style & Format (table)
### 1.3 Recent Video Catalog (themed clusters)
### 1.4 Audience Profile (table)
### 1.5 Content Gaps Identified

## 2. Current Trend Research
### 2.1 Trend Signals from Hacker News
### 2.2 Trend Signals from Search Research
### 2.3 Trend Synthesis — Heat Map

## 3. N Fresh Video Ideas
(Idea 1..N with title, why, outline, audience, keywords)

## 4. Summary & Recommendations
(Priority ranking table, content strategy recommendations)
```

## Pitfalls

1. **ytInitialData regex too greedy/not greedy enough** — the `\{.*?\}` pattern works for channel pages but may need `\{.*?\}\s*;` with different whitespace handling for other page types. Always verify the extracted JSON parses correctly.

2. **YouTube page structure changes** — as of mid-2026, videos use `richItemRenderer` → `lockupViewModel`. If scraping fails, inspect the raw JSON structure with `json.dumps(rich_items[0], indent=2)[:4000]` to find the new path.

3. **Google search blocking** — Google frequently blocks automated requests. DuckDuckGo's HTML endpoint is more reliable for trend research.

4. **Transcripts disabled** — some videos have no transcripts. Skip those and pick alternatives. The `youtube-content` skill handles this gracefully.

5. **Channel with few videos** — if the channel has <10 videos, the gap analysis is less meaningful. Note this limitation in the report.

6. **Non-English channels** — the transcript analysis and trend research should adapt to the channel's language. Search queries should be in the relevant language.

## Tips

- **Batch independent calls** — channel scraping, HN fetching, and DDG searches can all run in parallel.
- **Use execute_code for parsing** — the ytInitialData JSON is 400K+ chars. Parsing it in Python via `execute_code` keeps it out of your context window.
- **Save the report as a .md file** — the user can review, edit, and share it.
- **Offer to save as a skill** — after completing a complex analysis, offer to save the workflow. This skill itself was created from such an offer.