---
name: doc-site-to-markdown
description: "Crawl an entire documentation website and convert it to organized, LLM-optimized markdown files. Covers sitemap-based discovery, async fetching, HTML cleaning, markdown conversion with YAML frontmatter, directory mirroring, and index generation. Use when the user wants to download docs for offline LLM Q&A, RAG pipelines, or knowledge base construction. Triggers: 'crawl this documentation site', 'convert docs to markdown', 'download docs for LLM', 'scrape documentation for RAG', 'crawl site to markdown'."
version: 1.0.0
tags:
  - web-crawling
  - documentation
  - markdown
  - llm
  - rag
  - static-site
  - sitemap
  - scraping
---

# Doc Site to Markdown

Crawl a documentation website and produce clean, organized markdown files optimized for LLM consumption (Q&A, RAG, knowledge bases).

## When to Use This Skill

- User wants to download an entire documentation site as markdown for offline LLM use
- User is building a RAG pipeline and needs clean source documents
- User wants to mirror a docs site locally for search/Q&A

## Approach Selection

### 1. Check if the site is static HTML first (PREFERRED)

Most documentation sites (MkDocs, Docusaurus, Hugo, Jekyll, S3-hosted static sites) serve fully rendered HTML without needing JavaScript. For these, use the **httpx + BeautifulSoup + markdownify** pipeline described below. It is:
- 10-50x faster than browser-based crawling (no Playwright/Chromium needed)
- More reliable on headless servers (no missing system library issues)
- Simpler to debug and customize

### 2. Fall back to crawl4ai-skill for dynamic/JS-rendered sites

If the site requires JavaScript rendering (SPA frameworks, dynamic content loading), use the `crawl4ai-skill` CLI:
```bash
pip install crawl4ai-skill crawl4ai
python3 -m playwright install chromium
crawl4ai-skill crawl-site https://docs.example.com --max-pages 200 --format fit_markdown --output-dir ./output
```

**Pitfall:** Playwright's Chromium requires system libraries (libglib, libnss, etc.) that may be missing on headless servers. If `crawl4ai-skill crawl-site` fails with `error while loading shared libraries`, either install the missing libs (`apt install libglib2.0-0 libnss3 libnspr4 ...`) or switch to the httpx pipeline for static sites.

### 3. Hybrid: use crawl4ai-skill for single-page dynamic scraping

For a single JS-heavy page, `crawl4ai-skill crawl <url> --format fit_markdown` works well. For full-site crawls of static sites, prefer httpx.

## Static Site Pipeline (Recommended)

### Prerequisites

```bash
pip install httpx markdownify beautifulsoup4 lxml
```

### Step 1: Discover URLs via sitemap.xml

Most documentation sites expose `sitemap.xml` at the root:

```bash
curl -s https://docs.example.com/sitemap.xml | grep -c '<loc>'
```

If no sitemap exists, you can:
- Crawl the homepage and recursively follow links matching the site's domain
- Check for `llms-full.txt` (some modern docs sites provide this)
- Use `crawl4ai-skill crawl-site <url> --strategy recursive`

### Step 2: Run the crawl script

Use `templates/crawl_docs_site.py` as the starting template. Key parameters to customize:
- `BASE` — the root URL of the docs site
- `SITEMAP_URL` — path to sitemap (usually `{BASE}/sitemap.xml`)
- `OUTPUT_DIR` — where to save markdown files
- `CONCURRENCY` — number of parallel fetches (10 is safe; 20+ may trigger rate limits)

```bash
python3 crawl_docs_site.py
```

### Step 3: Verify output

```bash
# Count files
find output/ -name "*.md" | wc -l

# Check largest files (should be content-rich, not nav/boilerplate)
find output/ -name "*.md" -exec wc -l {} + | sort -rn | head -10

# Spot-check a file
cat output/api/some-endpoint.md | head -30
```

## Output Structure

The pipeline produces:

```
output/
├── INDEX.md          ← Categorized table of contents with relative links
├── index.md          ← Homepage
├── api/              ← Mirrors the site's URL path structure
│   ├── section-name/
│   │   ├── page-1.md
│   │   └── page-2.md
│   └── ...
├── guides/
│   └── ...
└── blog/
    └── ...
```

### Each markdown file contains:
- **YAML frontmatter** with `title` and `url` (source page URL)
- **H1 heading** with the page title
- **Clean content** — navigation, footers, scripts, ads, and sidebars stripped
- **Preserved structure** — headings, tables, code blocks, lists all intact

### INDEX.md contains:
- Total page count
- Pages grouped by URL section (e.g., `api/`, `blog/`, `guides/`)
- Relative markdown links to every file

## HTML Cleaning Strategy

The template script strips these elements before markdown conversion:
- `<nav>`, `<footer>`, `<header>`, `<script>`, `<style>`, `<noscript>`, `<iframe>`
- Bootstrap navbar classes (`.navbar`, `.navbar-collapse`, etc.)
- Elements with class/id matching `nav|footer|header|sidebar|breadcrumb|search`
- Google Analytics scripts and tracking pixels

It then finds the main content container by checking (in order): `<main>`, `<article>`, `.content`, `.main-content`, `#content`, `.page-content`, falling back to `<body>`.

## Pitfalls

1. **Missing sitemap**: Not all sites have `sitemap.xml`. Check `/robots.txt` for sitemap location, or fall back to recursive link-following.
2. **PDF/binary files in sitemap**: The sitemap may list PDFs or other non-HTML resources. Filter these out or handle gracefully (the template script catches errors per-page).
3. **Rate limiting**: High concurrency may trigger 429 responses. Reduce `CONCURRENCY` to 5 or add a delay between requests.
4. **Authentication-gated docs**: Some docs require login. Use `crawl4ai-skill crawl-with-login` or add auth headers/cookies to the httpx client.
5. **Relative links in markdown**: When stripping `<a>` tags (the template uses `strip=["img", "a"]`), links are converted to plain text. If you need links preserved, remove `"a"` from the strip list and handle relative URL resolution.
6. **Encoding issues**: Always specify `encoding="utf-8"` when writing files. The template handles this.

## Delivering Output to the User

When the crawl is complete, the user needs the files. Deliver a **zip archive** — do not expect the user to open files from a server file manager (e.g. `xdg-open` is not available on headless servers). Use:

```python
import shutil
shutil.make_archive('/path/to/output', 'zip', '.', 'output_dir')
```

Then provide the zip via `MEDIA:/absolute/path/to/output.zip` so the user can download it directly. This is the user's preferred delivery method for multi-file crawl output.

## Using the Output with an LLM

```bash
# Direct: feed specific docs into a prompt
cat output/api/accounts-payable/bills.md | your-llm-cli "How do I create a bill?"

# RAG: chunk and embed all files
# Files are clean markdown — ready for standard chunking strategies

# Context: use INDEX.md to find relevant docs
cat output/INDEX.md | your-llm-cli "Which docs cover AP payments?"
```

## Support Files

- `templates/crawl_docs_site.py` — Async Python script template for crawling a static docs site to markdown via sitemap. Customize BASE, SITEMAP_URL, OUTPUT_DIR, and CONCURRENCY at the top of the file.
- `references/crawl4ai-python-api.md` — Crawl4AI v0.9.0 Python API reference: BrowserConfig, CrawlerRunConfig, BFSDeepCrawlStrategy, filters, content filters, CrawlResult fields. Use when building custom crawl logic or Streamlit UIs on top of Crawl4AI.