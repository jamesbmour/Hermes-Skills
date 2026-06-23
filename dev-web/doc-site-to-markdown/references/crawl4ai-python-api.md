# Crawl4AI v0.9.0 Python API Reference

Condensed from source inspection of crawl4ai 0.9.0. Use when building custom
crawl logic or a Streamlit/Gradio UI on top of Crawl4AI.

## Core Classes

```python
from crawl4ai import (
    AsyncWebCrawler, BrowserConfig, CrawlerRunConfig,
    CacheMode, CrawlResult
)
```

### AsyncWebCrawler

```python
async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com", config=run_config)
    # For deep crawl with stream=True:
    async for result in await crawler.arun(url=url, config=run_config):
        process(result)
```

Key methods: `arun`, `arun_many`, `close`, `start`.

`arun()` returns a `CrawlResultContainer`. With `stream=True` in config,
returns an async iterator of `CrawlResult`.

---

## BrowserConfig

Controls browser launch behavior.

```python
BrowserConfig(
    browser_type="chromium",       # chromium | firefox | webkit
    headless=True,
    browser_mode="dedicated",      # dedicated | builtin
    use_managed_browser=False,
    verbose=True,
    java_script_enabled=True,
    text_mode=False,               # disables images/CSS for speed
    light_mode=False,              # minimal browser features
    ignore_https_errors=True,
    viewport_width=1080,
    viewport_height=600,
    user_agent="Mozilla/5.0 ...",  # or None for default
    user_agent_mode="",            # "" | "random"
    proxy=None,                    # "http://host:port"
    proxy_config=None,             # dict with server, username, password
    cookies=None,                  # list of cookie dicts
    headers=None,                  # dict of custom headers
    enable_stealth=False,          # anti-detection
    avoid_ads=False,
    memory_saving_mode=False,
    max_pages_before_recycle=0,    # 0 = no recycle
)
```

---

## CrawlerRunConfig

Controls per-crawl behavior: extraction, filtering, waiting, screenshots, etc.

```python
CrawlerRunConfig(
    # Content extraction
    word_count_threshold=200,      # min words per section
    css_selector=None,             # extract only this CSS selection
    excluded_tags=None,             # comma-separated HTML tags to remove
    excluded_selector=None,         # CSS selector for elements to remove
    only_text=False,
    prettiify=False,
    remove_forms=False,

    # Markdown generation
    markdown_generator=DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.48),
        content_source="cleaned_html",  # cleaned_html | raw_html | fit_html
    ),

    # Cache
    cache_mode=CacheMode.BYPASS,   # ENABLED | DISABLED | READ_ONLY | WRITE_ONLY | BYPASS

    # Page loading
    wait_until="domcontentloaded", # domcontentloaded | load | networkidle
    page_timeout=60000,            # milliseconds
    wait_for=None,                 # CSS selector to wait for
    wait_for_timeout=None,
    delay_before_return_html=0.1, # seconds
    js_code=None,                  # JS string to execute before scrape
    js_only=False,

    # Scrolling
    scan_full_page=False,
    scroll_delay=0.2,
    max_scroll_steps=None,

    # Page behavior
    process_iframes=False,
    remove_overlay_elements=False,  # remove popups/modals
    simulate_user=False,
    override_navigator=False,
    magic=False,                   # auto anti-bot + stealth
    adjust_viewport_to_content=False,

    # Media
    screenshot=False,
    pdf=False,
    capture_mhtml=False,
    exclude_all_images=False,
    exclude_external_images=False,

    # Links
    exclude_external_links=False,
    exclude_social_media_links=False,
    exclude_internal_links=False,
    exclude_domains=None,          # list of domains to exclude

    # Deep crawling
    deep_crawl_strategy=BFSDeepCrawlStrategy(...),

    # Misc
    check_robots_txt=False,
    log_console=False,
    verbose=True,
    stream=False,                  # stream results (for deep crawl)
    max_retries=0,
)
```

---

## Content Filters (for fit_markdown)

```python
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
```

### PruningContentFilter

Score-based content filtering. Removes low-information sections.

```python
PruningContentFilter(
    user_query=None,              # focus content around this query
    min_word_threshold=None,     # min words per section to keep
    threshold_type="fixed",      # fixed | dynamic | percentage
    threshold=0.48,              # 0-1; lower=more content, higher=more filtered
)
```

### BM25ContentFilter

Keyword-relevance based filtering using BM25 algorithm.

```python
BM25ContentFilter(
    user_query=None,             # query to rank content relevance
    bm25_threshold=1.0,          # lower=more content
    language="english",
    use_stemming=True,
)
```

---

## Deep Crawling

```python
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy, DFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import (
    FilterChain, DomainFilter, ContentTypeFilter,
    ContentRelevanceFilter, SEOFilter, URLPatternFilter,
)
from crawl4ai.deep_crawling.scorers import (
    KeywordRelevanceScorer, PathDepthScorer, ContentTypeScorer,
    FreshnessScorer, CompositeScorer,
)
```

### BFSDeepCrawlStrategy

```python
BFSDeepCrawlStrategy(
    max_depth=2,                  # crawl depth from seed URL
    filter_chain=FilterChain([...]),
    url_scorer=None,              # URLScorer or CompositeScorer
    include_external=False,       # follow links to other domains
    score_threshold=float('-inf'),
    max_pages=float('inf'),       # cap total pages
)
```

### Filters

```python
DomainFilter(allowed_domains=["docs.example.com"], blocked_domains=["ads.example.com"])
ContentTypeFilter(allowed_types=["text/html", "application/json"])
URLPatternFilter(patterns=["*/docs/*", "*/api/*"], use_glob=True)
ContentRelevanceFilter(query="authentication", threshold=0.5, k1=1.2, b=0.75)
SEOFilter(threshold=0.65, keywords=["python", "api"], weights=None)
```

### Scorers

```python
KeywordRelevanceScorer(keywords=["api", "reference"], weight=1.0)
PathDepthScorer(optimal_depth=3, weight=1.0)
ContentTypeScorer(type_weights={"text/html": 1.0}, weight=1.0)
FreshnessScorer(weight=1.0, current_year=2024)
CompositeScorer(scorers=[keyword_scorer, depth_scorer])
```

### Usage with stream=True

```python
run_config = CrawlerRunConfig(
    deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=3, max_pages=100),
    stream=True,                  # MUST be True for deep crawl progress
    markdown_generator=md_generator,
    cache_mode=CacheMode.BYPASS,
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    async for result in await crawler.arun(url=seed_url, config=run_config):
        # Each result is a CrawlResult for one page
        print(f"Crawled: {result.url}")
```

---

## CrawlResult Fields

```python
result.url              # str — the crawled URL
result.html             # str — raw HTML
result.cleaned_html     # Optional[str] — HTML after cleaning
result.success          # bool
result.markdown         # str — raw markdown
result.fit_markdown     # Optional[str] — filtered markdown (if content_filter set)
result.markdown_v2     # MarkdownGenerationResult object (see below)
result.media           # Dict — {"images": [...], "videos": [...]}
result.links           # Dict — {"internal": [...], "external": [...]}
result.screenshot      # Optional[str] — base64 screenshot
result.pdf             # Optional[bytes]
result.mhtml           # Optional[str]
result.extracted_content  # Optional[str] — LLM-extracted structured data
result.metadata        # Optional[dict]
result.error_message   # Optional[str]
result.status_code     # Optional[int]
result.response_headers  # Optional[dict]
result.redirected_url  # Optional[str]
result.tables          # List[Dict] — extracted tables
result.session_id      # Optional[str]
result.cache_status    # Optional[str]
result.crawl_stats     # Optional[Dict]
```

### MarkdownGenerationResult

Accessed via `result.markdown_v2`:

```python
result.markdown_v2.raw_markdown           # str
result.markdown_v2.markdown_with_citations  # str
result.markdown_v2.references_markdown    # str
result.markdown_v2.fit_markdown           # Optional[str]
result.markdown_v2.fit_html              # Optional[str]
```

---

## CacheMode Values

```python
CacheMode.ENABLED      # read + write cache
CacheMode.DISABLED     # no caching
CacheMode.READ_ONLY    # read from cache only
CacheMode.WRITE_ONLY   # write to cache only
CacheMode.BYPASS       # ignore cache entirely (default)
```

---

## Common Patterns

### Single page with fit_markdown

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

browser_config = BrowserConfig(headless=True, verbose=False)
md_generator = DefaultMarkdownGenerator(
    content_filter=PruningContentFilter(threshold=0.48)
)
run_config = CrawlerRunConfig(
    markdown_generator=md_generator,
    word_count_threshold=200,
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(url="https://example.com", config=run_config)
    print(result.markdown)
```

### Deep crawl with domain filter

```python
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter

filter_chain = FilterChain([
    DomainFilter(allowed_domains=["docs.example.com"])
])
bfs = BFSDeepCrawlStrategy(max_depth=3, max_pages=100, filter_chain=filter_chain)

run_config = CrawlerRunConfig(
    deep_crawl_strategy=bfs,
    stream=True,
    cache_mode=CacheMode.BYPASS,
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    async for result in await crawler.arun(url="https://docs.example.com", config=run_config):
        save_markdown(result)
```

---

## Pitfalls

1. **Playwright system libs**: Chromium needs libglib, libnss3, libnspr4, libatk, etc. If
   `BrowserType.launch` fails with `error while loading shared libraries`, install:
   `apt install libglib2.0-0 libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libdbus-1-3
   libcups2 libdrm2 libxcb1 libxkbcommon0 libx11-6 libxcomposite1 libxdamage1 libxext6
   libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2`
   If no root access, fall back to httpx + markdownify for static sites.

2. **stream=True required for deep crawl progress**: Without `stream=True`, deep crawl
   results are collected silently and returned as a batch. Set `stream=True` to get
   per-page results via async iterator.

3. **CrawlResultContainer vs CrawlResult**: `arun()` returns a `CrawlResultContainer`,
   not a `CrawlResult` directly. The container wraps the result — access fields like
   `result.markdown`, `result.success` directly on the container (it proxies).

4. **markdown_v2 is a computed property**: It returns a `MarkdownGenerationResult`
   object, not a string. Use `result.markdown` (str) for simple access, or
   `result.markdown_v2.fit_markdown` for filtered output.

5. **DFSDeepCrawlStrategy takes *args, **kwargs**: It's a thin wrapper that forwards
   to BFSDeepCrawlStrategy. Prefer BFS for most documentation crawling.