#!/usr/bin/env python3
"""
Crawl a documentation website and convert each page to clean, LLM-optimized markdown.

Uses the site's sitemap.xml for URL discovery, async httpx for fast fetching,
BeautifulSoup for HTML cleaning, and markdownify for HTML-to-Markdown conversion.

Customize the 4 constants below before running:
  BASE          - root URL of the docs site
  SITEMAP_URL   - full URL to the sitemap
  OUTPUT_DIR    - local directory for markdown output
  CONCURRENCY   - number of parallel fetches (10 is safe; reduce if rate-limited)

Usage:
  python3 crawl_docs_site.py
"""

import asyncio
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote

import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify as md

# ============================================================
# CONFIGURATION — customize these for your target site
# ============================================================
BASE = "https://docs.example.com"
SITEMAP_URL = f"{BASE}/sitemap.xml"
OUTPUT_DIR = "./docs-output"
CONCURRENCY = 10
TIMEOUT = 30
# ============================================================


async def fetch_sitemap(client: httpx.AsyncClient) -> list[str]:
    """Fetch and parse all URLs from the sitemap."""
    resp = await client.get(SITEMAP_URL)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for url_elem in root.findall(".//sm:loc", ns):
        urls.append(url_elem.text.strip())
    return urls


def url_to_filepath(url: str) -> str:
    """Convert a URL to a filesystem path under OUTPUT_DIR."""
    parsed = urlparse(url)
    path = unquote(parsed.path).strip("/")

    if not path:
        return os.path.join(OUTPUT_DIR, "index.md")

    if path.endswith("/"):
        path = path.rstrip("/")

    parts = path.split("/")
    return os.path.join(OUTPUT_DIR, *parts) + ".md"


def clean_html(html: str, source_url: str) -> str:
    """Extract the main content from the HTML page and convert to markdown."""
    soup = BeautifulSoup(html, "lxml")

    # Extract title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "Untitled"

    # Remove nav, footer, scripts, styles, and other non-content elements
    for selector in [
        "nav", "footer", "script", "style", "noscript", "header",
        ".navbar", ".site-header", ".site-footer", ".sidebar",
        ".breadcrumb", ".search", "#navbar-collapse", ".footer",
        ".ads", ".google-analytics", "iframe",
    ]:
        for elem in soup.select(selector):
            elem.decompose()

    # Remove elements by class/id pattern
    for elem in soup.find_all(attrs={"class": re.compile(r"nav|footer|header|sidebar|breadcrumb|search", re.I)}):
        elem.decompose()

    # Find the main content area
    content = None
    for selector in ["main", "article", ".content", ".main-content", "#content", ".page-content", ".container .row"]:
        content = soup.select_one(selector)
        if content:
            break

    if not content:
        content = soup.find("body") or soup

    # Remove any remaining nav elements inside content
    for elem in content.find_all("nav"):
        elem.decompose()

    # Convert to markdown
    # strip=["img", "a"] removes images and links (plain text remains)
    # Remove "a" from strip list if you want to preserve links
    markdown = md(str(content), heading_style="ATX", strip=["img", "a"], code_language="xml")

    # Clean up excessive blank lines
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    # Build the final document with YAML frontmatter
    result = f"""---
title: {title}
url: {source_url}
---

# {title}

{markdown.strip()}
"""
    return result


async def fetch_and_convert(client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore) -> tuple[str, str | None]:
    """Fetch a URL and convert to markdown. Returns (url, markdown_content_or_error)."""
    async with semaphore:
        try:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            markdown = clean_html(resp.text, url)
            return url, markdown
        except Exception as e:
            return url, f"ERROR: {e}"


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(TIMEOUT),
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
        http2=True,
    ) as client:
        # Fetch sitemap
        print("Fetching sitemap...")
        urls = await fetch_sitemap(client)
        print(f"Found {len(urls)} URLs to crawl")

        # Crawl with concurrency limit
        semaphore = asyncio.Semaphore(CONCURRENCY)
        tasks = [fetch_and_convert(client, url, semaphore) for url in urls]

        success = 0
        failed = 0

        done_count = 0
        for coro in asyncio.as_completed(tasks):
            url, content = await coro
            done_count += 1

            if content and not content.startswith("ERROR"):
                filepath = url_to_filepath(url)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                success += 1
            else:
                failed += 1
                print(f"  FAILED [{done_count}/{len(urls)}]: {url} -> {content[:80] if content else 'None'}")

            if done_count % 50 == 0:
                print(f"  Progress: {done_count}/{len(urls)} pages processed ({success} ok, {failed} failed)")

        print(f"\nDone! Success: {success}, Failed: {failed}, Total: {len(urls)}")
        print(f"Output directory: {OUTPUT_DIR}")

        # Generate an index file
        index_path = os.path.join(OUTPUT_DIR, "INDEX.md")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(f"# Documentation Index\n\n")
            f.write(f"Crawled {success} pages from {BASE}\n\n")

            sections = {}
            for url in urls:
                parsed = urlparse(url)
                parts = parsed.path.strip("/").split("/")
                section = parts[0] if parts and parts[0] else "root"
                sections.setdefault(section, []).append(url)

            for section in sorted(sections.keys()):
                urls_in_section = sorted(sections[section])
                f.write(f"## {section} ({len(urls_in_section)} pages)\n\n")
                for u in urls_in_section:
                    fp = url_to_filepath(u)
                    rel_path = os.path.relpath(fp, OUTPUT_DIR)
                    parsed = urlparse(u)
                    page_title = parsed.path.strip("/").split("/")[-1].replace("-", " ").title()
                    f.write(f"- [{page_title}]({rel_path})\n")
                f.write("\n")

        print(f"Index file: {index_path}")


if __name__ == "__main__":
    asyncio.run(main())