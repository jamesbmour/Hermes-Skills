# Web Research Techniques for Deep Research

Proven methods for live web research when search engines block automated requests and websites are JS-rendered.

## Search Engines That Work with curl

| Engine | URL Pattern | Notes |
|--------|------------|-------|
| **Marginalia Search (old interface)** | `https://old-search.marginalia.nu/search?query={QUERY}` | Best option. Returns 25 HTML results with URLs + snippets. Keyword-based, not full-text. Must use the `old-` subdomain — the new UI requires JavaScript. |
| Google | `https://www.google.com/search?q={QUERY}` | Blocks automated curl — returns JS challenge page, no results. |
| Bing | `https://www.bing.com/search?q={QUERY}` | Blocks automated curl — returns empty results or challenge. |
| DuckDuckGo HTML | `https://html.duckduckgo.com/html/?q={QUERY}` | Inconsistent — sometimes returns results, sometimes empty. |

### Marginalia Search Usage

```bash
curl -sL --max-time 20 -H 'User-Agent: Mozilla/5.0' \
  'https://old-search.marginalia.nu/search?query=Cincinnati+warehousing+3PL'
```

Extract results: look for lines starting with `https://` in the stripped text. Each URL is followed by a title line and a snippet line. Parse with regex in `execute_code`.

### Query Tips
- Use `+` to join words: `vending+machine+installation+logistics`
- Marginalia is keyword-based, not full-text — use distinctive terms
- Quotes for exact phrases: `"white glove" installation`
- Hyphen to exclude: `logistics -freight`

### PITFALL: Marginalia Rate Limiting
Marginalia aggressively rate-limits automated requests. After 3-4 rapid queries, you'll get a "Wait For A Moment / barraged by queries from bots" page with a countdown timer. The page auto-refreshes after the countdown, but curl won't follow it. **Mitigations:**
- Space queries at least 5-10 seconds apart. Use `execute_code` with `time.sleep(8)` between `terminal()` calls.
- If you hit the rate limit, wait 30-60 seconds before retrying that query.
- Prioritize your most important queries first — you may only get 4-6 successful searches before hitting limits.
- The rate limit is per-search-engine-instance, not per-query — switching query terms doesn't reset it.
- When rate-limited, switch to direct competitor site fetches (`curl` individual URLs) while waiting for Marginalia to recover.

## Extracting Content from JS-Rendered Websites

### WordPress REST API (for WordPress sites)

Many company websites are WordPress but render content via JS. The HTML returns empty/near-empty `<body>` text. Solution: query the WP REST API directly.

```bash
# Get all pages with full content
curl -sL 'https://example.com/wp-json/wp/v2/pages?per_page=50'

# Get blog posts
curl -sL 'https://example.com/wp-json/wp/v2/posts?per_page=20'
```

Returns JSON array. Each page/post has:
- `title.rendered` — page title
- `content.rendered` — full HTML content (strip tags with regex)
- `slug` — URL slug
- `excerpt.rendered` — short excerpt
- `date` — publication date

Parse with `json_parse()` from `hermes_tools` (handles escaped JSON robustly).

**Detection:** Check page HTML for `/wp-json/` links, `wp-content/` paths, or WordPress generator meta tag.

### Direct HTML Stripping (for static sites)

```python
import re
text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
text = re.sub(r'\n\s*\n', '\n', text)
text = re.sub(r'[ \t]+', ' ', text).strip()
```

Also extract `<title>`, `<meta name="description">`, and `href` links for navigation discovery.

## Industry Directory Mining

Industry-specific directories are high-value for competitor research — they list companies with descriptions, phone numbers, and service categories that search engines don't surface well.

### Leonard's Guide (Warehousing/3PL)

| URL | Content |
|-----|---------|
| `leonardsguide.com/lgo/warehouse-companies/{state}.shtml` | Warehouse companies by state |
| `leonardsguide.com/lgo/order-fulfillment-warehouses/{state}.shtml` | Fulfillment warehouses by state |
| `leonardsguide.com/lgo/food-grade-storage-warehouses/{state}.shtml` | Food-grade warehouses by state |
| `leonardsguide.com/wlw-warehousing-central{N}.shtml` | Central US warehousing (paginated) |

Each listing includes company name, description (services, sq ft, industries), and phone numbers. No JS — pure HTML, curl works directly.

### Other Useful Directories
- **IWLA** (International Warehouse Logistics Association) — `iwla.com/directory` (may require JS)
- **Inbound Logistics Top 100 3PLs** — `inboundlogistics.com/articles/top-100-3pls/` (Cloudflare-protected, may block)
- **Armstrong & Associates** — `3plogistics.com` — 3PL market data and company lists

## Workflow for Competitor Research

1. **Scrape the subject company's website first** — understand their services, locations, industries, size, technology, and positioning before searching for competitors.
2. **Search via Marginalia** for `{industry} companies {city/region}` and `{service type} {geographic area}`.
3. **Mine industry directories** (Leonard's Guide for warehousing, equivalent directories for other industries) — these surface small/mid-size companies that search engines miss.
4. **Fetch competitor websites directly** — get their meta descriptions, about pages, services pages. Use WP REST API if WordPress.
5. **Search for industry market data** — market size, growth rates, trends via Marginalia → fetch resulting report/market research pages.
6. **Cross-reference** subagent training-knowledge summaries with live web findings — subagents provide breadth of knowledge, web research provides current verification.

## Batch Processing with execute_code

When fetching many URLs, use `execute_code` to batch `terminal` + `curl` calls:

```python
from hermes_tools import terminal
import re

urls = ["url1", "url2", "url3"]
for url in urls:
    result = terminal(command=f"curl -sL --max-time 15 -H 'User-Agent: Mozilla/5.0' '{url}'", timeout=25)
    html = result.get("output", "")
    # Strip tags, extract content
    text = re.sub(r'<[^>]+>', '\n', html)
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    print(text[:2000])
```

This keeps context window manageable by processing/trimming results programmatically before printing.