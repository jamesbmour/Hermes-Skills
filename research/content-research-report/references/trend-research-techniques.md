# Trend Research Techniques for Content Reports

Beyond `delegate_task` with web-search subagents, these direct techniques are
fast, reliable, and work in a single-agent session without spawning children.

## Hacker News — Front Page & Show HN

HN is an excellent real-time signal for developer/tech trends. Two endpoints:

### Front page (what the community is discussing)

```bash
curl -s 'https://news.ycombinator.com/' -A 'Mozilla/5.0' 2>/dev/null \
  | grep -oE 'class="titleline"><a href="[^"]*"[^>]*>([^<]+)</a>' \
  | sed 's/<[^>]*>//g'
```

### Show HN (what people are building)

```bash
curl -s 'https://news.ycombinator.com/show' -A 'Mozilla/5.0' 2>/dev/null \
  | grep -oE 'class="titleline"><a href="[^"]*"[^>]*>([^<]+)</a>' \
  | sed 's/<[^>]*>//g'
```

**Signal to extract:** Look for patterns like "AI agent", "MCP", "local LLM",
"protocol", "framework", new model names (DeepSeek, Llama, Qwen), and
YC launch tags ("Launch HN:", "Show HN:").

## DuckDuckGo HTML — Search Trend Confirmation

Google blocks curl scraping (returns empty or JS-challenge pages). DuckDuckGo's
HTML endpoint works reliably:

```bash
curl -s 'https://html.duckduckgo.com/html/?q=YOUR+QUERY+HERE' \
  -A 'Mozilla/5.0' 2>/dev/null \
  | grep -oE 'class="result__a"[^>]*>([^<]+)</a>'
```

**Note:** DDG sometimes returns empty for certain queries. Retry with
simplified query terms or broader keywords. Google search via curl does NOT
work — it returns a JS challenge page with no `<h3>` results.

**Pitfall (2026-07):** DuckDuckGo now also shows a CAPTCHA challenge ("bots use
DuckDuckGo too") when accessed via browser or curl. Bing search also shows a
Cloudflare "Verify you are human" challenge. When both DDG and Bing are blocked,
fall back to **GitHub Trending** (see below) which has been consistently
accessible and is arguably a better signal for developer-tool trends.

## GitHub Trending — Developer Tool & Framework Trends

GitHub Trending is the most reliable trend source when search engines show
captchas. It shows what repos developers are actually starring this week —
a strong signal of real adoption, not just buzz.

### Accessing via browser

Navigate to `https://github.com/trending/python?since=weekly` (or any language).
The page loads without authentication. Use `browser_console` to extract all
repos as structured JSON:

```javascript
[...document.querySelectorAll('article')].map(a => {
  const h = a.querySelector('h2 a')?.textContent || '';
  const p = a.querySelector('p')?.textContent || '';
  const starsThisWeek = a.textContent.match(/([\d,]+)\s+stars this week/)?.[1];
  return { name: h.trim(), desc: p.trim(), starsThisWeek };
}).filter(r => r.name)
```

**Refined extraction (2026-07):** The `h2 a` selector is more reliable than `h2`
alone — it gets the link text directly without extra whitespace from nested spans.
The `textContent` approach for stars-this-week avoids fragile DOM selector paths.
This snippet returns a clean newline-separated JSON array suitable for scanning
in a single `browser_console` call.

**Why this works well:**
- No captcha/bot-detection issues (GitHub Trending is publicly accessible)
- `browser_console` extraction avoids the 8000-char snapshot truncation
- Returns 15-25 repos with name, description, total stars, and stars-this-week
- Filter by language (`/python`, `/typescript`, etc.) and time range (`daily`, `weekly`, `monthly`)
- The "stars this week" metric is a direct adoption signal — repos gaining 2,000+ stars/week are genuinely trending

**What to look for:** New frameworks with rapidly growing stars, tools that
solve problems in the channel's niche, libraries that complement the channel's
existing tech stack. Map repo descriptions to the channel's content gaps.

## Trend Synthesis Pattern

After collecting raw signals, organize into a heat map:

```
🔥🔥🔥 = Widely adopted, multiple major companies building, active tutorials
🔥🔥   = Growing adoption, multiple tools/libraries emerging
🔥     = Early stage, one or two notable implementations
⚡    = Emerging concern (security, compliance) gaining attention
```

Map each trend to the channel's existing content categories to find gaps —
topics that are trending but absent from the channel's recent catalog.