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