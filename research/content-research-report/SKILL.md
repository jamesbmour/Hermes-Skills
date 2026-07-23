---
name: content-research-report
description: "Use when the user wants a research-backed content strategy report for a YouTube channel (or similar creator platform) — channel analysis, trend research, video/topic ideation, and a formatted Markdown + PDF deliverable. Triggered by requests like 'analyze this YouTube channel and suggest video ideas', 'daily research report for my channel', 'content strategy report for @channel', or any request combining channel audit + trend research + ideation."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [youtube, content-strategy, research-report, video-ideation, channel-analysis]
    related_skills: [youtube-content, deep-research]
---

# Content Research Report

Generate a research-backed content strategy report for a YouTube channel (or similar creator platform). The output is a structured Markdown report and a PDF, covering: channel analysis, trend research, video/topic ideation with full briefs, and strategic recommendations.

## When to Use

- "Daily research report that analyzes my YouTube channel and suggests video ideas"
- "Analyze @channelname and give me content ideas based on current trends"
- "Research what's trending in AI coding and give me 5 video ideas for my channel"
- "Content strategy report for my tech tutorial channel"
- Any request combining channel audit + trend research + ideation

**Don't use for:** single-video transcript work (use `youtube-content`), general-purpose research without a channel focus (use `deep-research`), or financial/stock reports (use `deepstock` / `equity-research`).

## Prerequisites

- `yt-dlp` (usually pre-installed; `pip3 install yt-dlp` if missing)
- `youtube-transcript-api` (for transcript fetching — see `youtube-content` skill setup)
- `pandoc` (for PDF generation; `brew install pandoc` on macOS)
- A LaTeX distribution with `xelatex` (for PDF; `brew install --cask mactex` on macOS, or `apt install texlive-xetex` on Linux)
- `markdown` Python package (`pip3 install markdown`)

## Workflow

### Phase 1: Channel Analysis

**Goal:** Understand the channel's content, style, audience, and gaps.

1. **Get video listing** — fetch the 30-50 most recent videos with metadata. Two methods:

   **Method A — yt-dlp (includes duration, but can be slow):**
   ```bash
   yt-dlp --flat-playlist --dump-single-json "https://www.youtube.com/@CHANNEL/videos" 2>/dev/null | python3 -c "
   import json, sys
   data = json.load(sys.stdin)
   for i, v in enumerate(data.get('entries', [])[:50]):
       print(f'{i+1}. [{v.get(\"id\")}] {v.get(\"title\")} | Duration: {v.get(\"duration\",0)}s')
   print(f'Total videos: {len(data.get(\"entries\", []))}')
   "
   ```

   **Method B — ytInitialData scrape (faster, no yt-dlp dependency, includes channel metadata):**
   See `references/youtube-channel-scraping.md` for the full technique. Summary: curl the
   `/videos` page, extract `ytInitialData` JSON from HTML, navigate `richItemRenderer` →
   `lockupViewModel` for titles + video IDs. This method is preferred when yt-dlp is not
   installed or times out. It also yields channel description and keywords from
   `channelMetadataRenderer` in the same fetch.

   **PITFALL:** YouTube's internal JSON structure changes over time. If `richItemRenderer`
   or `lockupViewModel` keys disappear, inspect the JSON for any key containing `Renderer`
   and find where `videoId` or thumbnail URLs appear. See the reference file for debugging tips.

2. **Get channel metadata** — description, subscriber count:
   - If using Method B (ytInitialData scrape), channel description and keywords are already
     available from `channelMetadataRenderer` in the same fetch — no separate call needed.
   - If using Method A (yt-dlp):
     ```bash
     yt-dlp --print '%(title)s|||%(description).500s|||%(channel_follower_count)s' 'https://www.youtube.com/@CHANNEL' 2>/dev/null
     ```
     Note: This can be slow (30s+). If it times out, use the video listing output (which includes the uploader name) and estimate subscribers from context.

3. **Fetch transcripts** from 3-5 representative videos using the `youtube-content` skill's helper script:
   ```bash
   python3 ~/.hermes/skills/media/youtube-content/scripts/fetch_transcript.py "VIDEO_ID" --text-only
   ```
   Sample recent hits, long-form tutorials, and different content categories to capture the range of style and format.

5. **Synthesize** the channel profile:
   - Content categories (with approximate video counts)
   - Style and format (code-along? talking head? screen recording?)
   - Tone and hosting style
   - Audience skill level and interests
   - Strengths and content gaps (what topics are missing?)

### Phase 2: Trend Research

**Goal:** Identify current trends that align with the channel's niche.

1. **Identify key trend angles** relevant to the channel's niche. For a coding/AI channel, angles include:
   - New AI/LLM models, frameworks, and developer tools
   - Trending programming languages and frameworks
   - Popular tutorial topics and search trends
   - AI coding assistants and developer workflow tools
   - Emerging tech (local AI, agentic workflows, MCP, RAG 2.0, etc.)

2. **Run parallel research** — two approaches depending on session needs:

   **Approach A — delegate_task (for multi-angle, parallel research):**
   ```python
   delegate_task(
       tasks=[
           {goal: "Research angle A...", toolsets: ["web"]},
           {goal: "Research angle B...", toolsets: ["web"]},
           {goal: "Research angle C...", toolsets: ["web"]},
       ]
   )
   ```
   **PITFALL:** Some subagents return only their search queries without synthesized results. To mitigate:
   - Make each goal very specific — name exact tools/models/versions to search for
   - Include "Return a structured summary with specific tool names, versions, and why each is trending" in the goal
   - If a subagent returns insufficient detail, fall back to direct `terminal` + `curl` searches

   **Approach B — direct curl searches (faster for single-agent sessions):**
   See `references/trend-research-techniques.md` for full details. Key sources:
   - **Hacker News front page + /show** — `curl` + grep for `titleline` class. Excellent for real-time dev sentiment.
   - **DuckDuckGo HTML** — `curl 'https://html.duckduckgo.com/html/?q=...'` + grep for `result__a` class. Google blocks curl; DDG works reliably.
   - Combine both for a fast trend snapshot without spawning subagents.

3. **Synthesize trends** into a ranked list with:
   - Trend name and description
   - Why it's hot right now
   - Relevance score to the channel
   - Whether it's a good tutorial topic

4. **Build a trend-channel fit matrix** — which trends map best to the channel's existing expertise and content gaps.

### Phase 3: Video Ideation

**Goal:** Generate N fresh, trend-aligned video ideas tailored to the channel.

**Default:** 5 ideas. Adjust if the user specifies a different count (e.g., "give me 10 ideas").

Each idea must include:

1. **Compelling title** — specific, benefit-driven, optimized for YouTube search
2. **Tutorial outline** — section-by-section breakdown with estimated durations
3. **Total runtime** — realistic estimate
4. **Target audience** — who this video is for, including existing channel viewers
5. **SEO keywords/tags** — 8-12 comma-separated tags for YouTube optimization
6. **Rationale** — why this video will work (trend alignment, channel fit, series potential)

**Quality criteria for ideas:**
- Must NOT have been covered recently by the channel (check against Phase 1 video listing)
- Must align with current trends from Phase 2
- Must fit the channel's format, style, and audience
- Prefer ideas that build on existing content series (creates binge-watching)
- Include at least 2 ideas that combine the channel's strongest categories with trending topics (crossover content performs well)

### Phase 4: Strategic Recommendations

Add a section with:
- Prioritized content calendar (which video to produce first and why)
- Series opportunities (how to turn one video into a 3-5 part series)
- Growth tactics (Shorts, cross-promotion, community engagement)

### Phase 5: Deliver the Report

1. **Write the Markdown report** — use `write_file` to create the `.md` file. Structure:
   ```markdown
   # Channel Name — Daily Research Report
   ## Executive Summary
   ## Part 1: Channel Analysis
   ## Part 2: Trend Landscape
   ## Part 3: N Video Ideas (one per idea with full briefs)
   ## Part 4: Strategic Recommendations
   ## Part 5: Sources
   ```

2. **Convert to PDF** — use pandoc with xelatex:
   ```bash
   pandoc REPORT.md -o REPORT.pdf --pdf-engine=xelatex \
     -V geometry:margin=2.5cm -V colorlinks=true -V linkcolor=blue \
     -V mainfont="Helvetica"
   ```
   **CRITICAL:** Strip all emoji characters from the Markdown before conversion. pdflatex crashes on emojis; xelatex leaves blank gaps. Use Python to replace emojis with text equivalents (e.g., 🔥 → '', 🎯 → '[TARGET] ', ⭐ → '').

   **Alternative (if pandoc unavailable):** Use Python `markdown` + `weasyprint`, but note weasyprint requires system libraries (libgobject, pango) that may not be installed. Run Python PDF scripts via `terminal()`, not `execute_code()` — the `execute_code` sandbox does not have access to system pip packages.

## Output Format

Both files are placed in the user's home directory (or a specified path):

- `CHANNEL_NAME_Daily_Research_Report.md` — the full Markdown report
- `CHANNEL_NAME_Daily_Research_Report.pdf` — styled PDF version

## Support Files

- `references/channel-analysis-commands.md` — proven yt-dlp commands for channel metadata, video listing, and transcript fetching
- `references/youtube-channel-scraping.md` — full technique for scraping channel data via ytInitialData JSON (no yt-dlp needed; faster, includes channel metadata)
- `references/trend-research-techniques.md` — direct curl techniques for Hacker News and DuckDuckGo trend research without spawning subagents
- `scripts/strip_emoji.py` — strips emoji and problematic Unicode before PDF conversion; accepts `--in-place`

## Verification Checklist

- [ ] Channel: 30+ videos listed and categorized
- [ ] Channel: transcripts fetched from 3+ representative videos
- [ ] Channel: content gaps identified
- [ ] Trends: 8+ specific tools/models/trends cited with names and versions
- [ ] Trends: trend-channel fit matrix built
- [ ] Ideas: exactly N (user-specified count, default 5), each with title, outline, audience, SEO tags, rationale
- [ ] Ideas: none duplicate recently covered channel topics
- [ ] Strategy: prioritization and series opportunities included
- [ ] Report: Markdown file written and verified
- [ ] Report: PDF generated with zero LaTeX errors (emojis stripped)
- [ ] Report: both files confirmed on disk with `ls -lh`

## Common Pitfalls

1. **yt-dlp channel page times out** — the channel-level `--dump-single-json` call can take 30s+. If it times out, skip it; the video listing already includes the uploader name and total count.
2. **delegate_task returns only search queries** — subagents with `toolsets=["web"]` sometimes return their function-call trace instead of synthesized results. Make goals extremely specific and include "Return a structured summary" in the goal text. Be prepared to fall back to direct searches.
3. **Emojis break PDF generation** — pdflatex crashes on emoji characters. xelatex produces blank gaps. Always strip emojis before pandoc conversion.
4. **execute_code can't use pip packages** — the sandbox doesn't inherit system Python packages. Use `terminal()` for Python scripts that need `markdown`, `weasyprint`, or other installed libraries.
5. **View counts are zero in flat-playlist dumps** — `yt-dlp --flat-playlist` doesn't include view counts. For view data, fetch individual video metadata or estimate from context.
6. **json.loads fails on ytInitialData** — the raw JSON from YouTube's HTML contains control characters that strict `json.loads` rejects. Always use `json_parse()` from `hermes_tools` (which uses `strict=False`) when parsing scraped YouTube JSON.
7. **Google search blocks curl** — `curl` to Google search returns a JS challenge page with no extractable results. Use DuckDuckGo's HTML endpoint (`html.duckduckgo.com/html/`) instead, which returns parseable HTML.
8. **YouTube renderer key names change** — the internal JSON structure (`richItemRenderer`, `lockupViewModel`, etc.) can change without notice. If extraction returns empty results, inspect the JSON structure by listing all keys containing `Renderer` and finding where `videoId` or thumbnail URLs appear. See `references/youtube-channel-scraping.md` for debugging steps.
