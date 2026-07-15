#!/usr/bin/env python3
"""
Download all pics and videos from a CSV of Reddit saved/upvoted posts.

Handles:
  - redgifs.com  → video via API v2
  - i.redd.it    → direct image/gif download
  - v.redd.it    → video via Reddit HTML scrape
  - reddit.com/gallery  → images via Reddit HTML scrape
  - imgchest.com → gallery page scrape
  - "No text found" / text-only → skipped

Usage:
    python3 download_reddit_media.py [--csv PATH] [--out DIR] [--workers N]

Defaults:
    --csv    ~/Downloads/reddit_media_downloader/Upvoted Reddit Posts - Sheet1.csv
    --out    ~/Downloads/reddit_media_downloader/downloads
    --workers 4
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests

# ── constants ──────────────────────────────────────────────────────────────

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

HEADERS = {"User-Agent": USER_AGENT, "Accept": "*/*"}

REDDIT_BROWSER_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

_RG_LOCK = threading.Lock()
_RG_TOKEN = {"token": None, "expires": 0}

# ── helpers ────────────────────────────────────────────────────────────────

def safe_filename(s, max_len=120):
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', s)
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > max_len:
        s = s[:max_len].rstrip()
    return s or "untitled"


def download_file(url, dest, session=None, retries=3):
    s = session or SESSION
    for attempt in range(retries):
        try:
            r = s.get(url, stream=True, timeout=60, headers=HEADERS)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
            return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                print(f"    ✗ Failed: {e}")
                return False
    return False


def pick_ext_from_url(url, default=".mp4"):
    p = urlparse(url)
    root, ext = os.path.splitext(p.path)
    if ext and len(ext) <= 5:
        return ext
    return default


# ── redgifs ────────────────────────────────────────────────────────────────

def rg_get_token(session):
    """Get a temporary API token from redgifs (thread-safe)."""
    with _RG_LOCK:
        if _RG_TOKEN["token"] and time.time() < _RG_TOKEN["expires"] - 30:
            return _RG_TOKEN["token"]
        url = "https://api.redgifs.com/v2/auth/temporary"
        headers = {"User-Agent": USER_AGENT, "Origin": "https://www.redgifs.com",
                   "Referer": "https://www.redgifs.com/"}
        r = session.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        token = data.get("token")
        expires = time.time() + 3600
        _RG_TOKEN["token"] = token
        _RG_TOKEN["expires"] = expires
        return token


def rg_extract_id(source_url):
    """Extract the gif ID from any redgifs URL variant."""
    m = re.search(r'redgifs\.com/(?:watch|ifr)/([A-Za-z0-9]+)', source_url)
    if m:
        return m.group(1)
    return None


def rg_download(source_url, dest_dir, title, session):
    """Download a redgifs video. Returns True on success."""
    gid = rg_extract_id(source_url)
    if not gid:
        print(f"    ✗ Could not extract redgifs ID from {source_url}")
        return False

    token = rg_get_token(session)
    api_url = f"https://api.redgifs.com/v2/gifs/{gid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
        "Origin": "https://www.redgifs.com",
        "Referer": "https://www.redgifs.com/",
    }

    r = session.get(api_url, headers=headers, timeout=30)
    if r.status_code == 401:
        _RG_TOKEN["token"] = None
        token = rg_get_token(session)
        headers["Authorization"] = f"Bearer {token}"
        r = session.get(api_url, headers=headers, timeout=30)
    if r.status_code == 429:
        time.sleep(5)
        r = session.get(api_url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()

    gif = data.get("gif", {})
    urls = gif.get("urls", {})
    video_url = urls.get("hd") or urls.get("sd") or urls.get("gif")
    if not video_url:
        print("    ✗ No video URL in redgifs API response")
        return False

    ext = ".mp4"
    fname = f"{safe_filename(title)}{ext}"
    dest = dest_dir / fname
    if dest.exists() and dest.stat().st_size > 0:
        print(f"    ✓ Already exists: {fname}")
        return True

    return download_file(video_url, dest, session)


# ── i.redd.it (direct media) ──────────────────────────────────────────────

def ireddit_download(source_url, dest_dir, title, session):
    """Download a direct i.redd.it image/gif."""
    ext = pick_ext_from_url(source_url, ".jpg")
    fname = f"{safe_filename(title)}{ext}"
    dest = dest_dir / fname
    if dest.exists() and dest.stat().st_size > 0:
        print(f"    ✓ Already exists: {fname}")
        return True
    return download_file(source_url, dest, session)


# ── Reddit HTML scraping helpers ───────────────────────────────────────────

def _extract_reddit_post_id(reddit_url):
    """Extract the post ID from a reddit comments URL or gallery URL."""
    m = re.search(r'/comments/(\w+)/', reddit_url)
    if m:
        return m.group(1)
    m = re.search(r'reddit\.com/gallery/(\w+)', reddit_url)
    if m:
        return m.group(1)
    return None


def _reddit_api_info(post_id, session):
    """Fetch the old-reddit HTML api/info page and return the HTML (with retries)."""
    url = f"https://www.reddit.com/api/info?id=t3_{post_id}"
    for attempt in range(3):
        try:
            r = session.get(url, headers=REDDIT_BROWSER_HEADERS, timeout=30)
            if r.status_code == 403:
                wait = 10 * (attempt + 1)
                print(f"    ⏳ Reddit 403, retrying in {wait}s (attempt {attempt+1}/3)...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            return r.text
        except requests.exceptions.HTTPError:
            if attempt < 2:
                time.sleep(10 * (attempt + 1))
                continue
            raise
    raise requests.exceptions.HTTPError(f"403 Client Error: Blocked for url: {url}")


# ── v.redd.it (reddit hosted video) ───────────────────────────────────────

def vreddit_download(source_url, dest_dir, title, session, reddit_url=""):
    """Download a v.redd.it video by scraping the reddit api/info HTML."""
    post_id = _extract_reddit_post_id(reddit_url) or _extract_reddit_post_id(source_url)
    if not post_id:
        print(f"    ✗ Could not extract post ID for v.redd.it")
        return False

    html = _reddit_api_info(post_id, session)

    cmaf_urls = re.findall(r'(https?://v\.redd\.it/\w+/CMAF_\d+\.mp4)', html)
    dash_urls = re.findall(r'(https?://v\.redd\.it/\w+/DASH_\d+\.mp4)', html)

    all_urls = cmaf_urls + dash_urls
    if not all_urls:
        print("    ✗ No video URL found in reddit HTML")
        return False

    def sort_key(url):
        m = re.search(r'(?:CMAF|DASH)_(\d+)\.mp4', url)
        res = int(m.group(1)) if m else 0
        is_dash = 100000 if 'DASH' in url else 0
        return res + is_dash

    best_url = max(all_urls, key=sort_key)

    fname = f"{safe_filename(title)}.mp4"
    dest = dest_dir / fname
    if dest.exists() and dest.stat().st_size > 0:
        print(f"    ✓ Already exists: {fname}")
        return True

    return download_file(best_url, dest, session)


# ── reddit gallery ──────────────────────────────────────────────────────────

def reddit_gallery_download(source_url, dest_dir, title, session, reddit_url=""):
    """Download images from a reddit.com/gallery post by scraping api/info HTML."""
    post_id = _extract_reddit_post_id(source_url)
    if not post_id:
        post_id = _extract_reddit_post_id(reddit_url)
    if not post_id:
        print(f"    ✗ Could not extract gallery ID from {source_url}")
        return False

    html = _reddit_api_info(post_id, session)

    media_ids = list(dict.fromkeys(re.findall(r'preview\.redd\.it/(\w+)\.\w+', html)))

    if not media_ids:
        img_urls = re.findall(r'(https://i\.redd\.it/\w+\.\w+)', html)
        if img_urls:
            for i, img_url in enumerate(img_urls[:1]):
                ext = pick_ext_from_url(img_url, ".jpg")
                fname = f"{safe_filename(title)}{ext}"
                dest = dest_dir / fname
                if dest.exists() and dest.stat().st_size > 0:
                    print(f"    ✓ Already exists: {fname}")
                    return True
                return download_file(img_url, dest, session)
        print("    ✗ No gallery images found in reddit HTML")
        return False

    success = False
    for i, media_id in enumerate(media_ids):
        img_url = f"https://i.redd.it/{media_id}.jpg"
        ext = ".jpg"
        fname = f"{safe_filename(title)}_{i+1:02d}{ext}"
        dest = dest_dir / fname
        if dest.exists() and dest.stat().st_size > 0:
            print(f"    ✓ Already exists: {fname}")
            success = True
            continue
        if download_file(img_url, dest, session):
            success = True
        else:
            img_url = f"https://i.redd.it/{media_id}.png"
            fname = f"{safe_filename(title)}_{i+1:02d}.png"
            dest = dest_dir / fname
            if download_file(img_url, dest, session):
                success = True
    return success


# ── imgchest ──────────────────────────────────────────────────────────────

def imgchest_download(source_url, dest_dir, title, session):
    """Download images from an imgchest.com gallery page."""
    ids = re.findall(r'imgchest\.com/p/([a-z0-9]{10,15})', source_url)
    if not ids:
        print(f"    ✗ No imgchest URLs found")
        return False

    urls = [f"https://imgchest.com/p/{id}" for id in ids]

    success = False
    for idx, gallery_url in enumerate(urls):
        r = session.get(gallery_url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        html = r.text

        image_urls = set()
        json_matches = re.findall(r'"file_url"\s*:\s*"(https?://[^"]+)"', html)
        image_urls.update(json_matches)
        img_matches = re.findall(r'src="(https://(?:cdn|media|images?)\.imgchest\.com/[^"]+)"', html)
        image_urls.update(img_matches)
        og_matches = re.findall(r'og:image"\s*content="(https://[^"]+)"', html)
        image_urls.update(og_matches)
        lazy_matches = re.findall(r'data-src="(https://[^"]+)"', html)
        image_urls.update([u for u in lazy_matches if 'imgchest' in u or 'png' in u or 'jpg' in u or 'jpeg' in u])

        if not image_urls:
            print(f"    ✗ No images found in imgchest gallery {gallery_url}")
            continue

        sorted_urls = sorted(image_urls)
        for i, img_url in enumerate(sorted_urls):
            ext = pick_ext_from_url(img_url, ".jpg")
            suffix = f"_{idx+1}_{i+1:02d}" if len(urls) > 1 else f"_{i+1:02d}"
            fname = f"{safe_filename(title)}{suffix}{ext}"
            dest = dest_dir / fname
            if dest.exists() and dest.stat().st_size > 0:
                print(f"    ✓ Already exists: {fname}")
                success = True
                continue
            if download_file(img_url, dest, session):
                success = True
    return success


# ── dispatcher ────────────────────────────────────────────────────────────

def classify_source(source_url):
    """Return a handler name based on the source URL."""
    if not source_url or source_url.startswith("No text"):
        return "skip"
    u = source_url.lower()
    if "redgifs.com" in u:
        return "redgifs"
    if "i.redd.it" in u:
        return "ireddit"
    if "v.redd.it" in u:
        return "vreddit"
    if "reddit.com/gallery" in u:
        return "gallery"
    if "imgchest.com" in u:
        return "imgchest"
    if re.search(r'https://imgchest\.com/p/\w+', source_url):
        return "imgchest"
    return "skip"


def process_row(row, dest_dir, session):
    """Process one CSV row. Returns (handler, success)."""
    title = row.get("Title", "").strip()
    source = row.get("Source", "").strip()
    subreddit = row.get("comunity", "").strip()
    reddit_url = row.get("url", "").strip()

    handler = classify_source(source)
    if handler == "skip":
        return ("skip", True)

    desc = safe_filename(title) if title else safe_filename(reddit_url.split("/")[-1] if reddit_url else "untitled")

    try:
        if handler == "redgifs":
            success = rg_download(source, dest_dir, desc, session)
        elif handler == "ireddit":
            success = ireddit_download(source, dest_dir, desc, session)
        elif handler == "vreddit":
            success = vreddit_download(source, dest_dir, desc, session, reddit_url)
        elif handler == "gallery":
            success = reddit_gallery_download(source, dest_dir, desc, session, reddit_url)
        elif handler == "imgchest":
            success = imgchest_download(source, dest_dir, desc, session)
        else:
            return ("skip", True)
        return (handler, success)
    except Exception as e:
        print(f"    ✗ Error processing [{handler}]: {e}")
        return (handler, False)


# ── main ──────────────────────────────────────────────────────────────────

def main():
    default_csv = str(Path.home() / "Downloads" / "reddit_media_downloader" / "Upvoted Reddit Posts - Sheet1.csv")
    default_out = str(Path.home() / "Downloads" / "reddit_media_downloader" / "downloads")

    ap = argparse.ArgumentParser(description="Download media from Reddit saved-posts CSV")
    ap.add_argument("--csv", default=default_csv, help="Path to CSV file")
    ap.add_argument("--out", default=default_out, help="Output directory")
    ap.add_argument("--workers", type=int, default=4, help="Concurrent download threads")
    ap.add_argument("--limit", type=int, default=0, help="Max rows to process (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Classify sources without downloading")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    dest_dir = Path(args.out)
    dest_dir.mkdir(parents=True, exist_ok=True)

    if not csv_path.exists():
        sys.exit(f"CSV not found: {csv_path}")

    print(f"CSV:      {csv_path}")
    print(f"Output:   {dest_dir}")
    print(f"Workers:  {args.workers}")
    print()

    rows = []
    with open(csv_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if args.limit:
        rows = rows[: args.limit]

    print(f"Total rows: {len(rows)}")

    counts = {}
    for row in rows:
        h = classify_source(row.get("Source", "").strip())
        counts[h] = counts.get(h, 0) + 1
    print("Source breakdown:")
    for h, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {h:12s} {c}")
    print()

    if args.dry_run:
        print("Dry run — no downloads.")
        return

    results = {"redgifs": [0, 0], "ireddit": [0, 0], "vreddit": [0, 0],
               "gallery": [0, 0], "imgchest": [0, 0], "skip": [0, 0]}

    completed = 0
    total = len(rows)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(process_row, row, dest_dir, requests.Session()): (i + 1, row)
            for i, row in enumerate(rows)
        }
        for future in as_completed(futures):
            idx, row = futures[future]
            try:
                handler, success = future.result()
            except Exception as e:
                handler, success = "skip", False
                print(f"[{idx}/{total}] ERROR: {e}")
            completed += 1
            if handler in results:
                results[handler][0 if success else 1] += 1
            title_preview = row.get("Title", "")[:60]
            status = "✓" if success else "✗"
            if handler != "skip":
                print(f"[{completed}/{total}] {status} [{handler}] {title_preview}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_ok = sum(v[0] for v in results.values())
    total_fail = sum(v[1] for v in results.values())
    for h in ["redgifs", "ireddit", "vreddit", "gallery", "imgchest", "skip"]:
        s, f = results[h]
        print(f"  {h:12s}  ✓ {s:4d}  ✗ {f:4d}")
    print(f"  {'TOTAL':12s}  ✓ {total_ok:4d}  ✗ {total_fail:4d}")
    print(f"\nFiles saved to: {dest_dir}")


if __name__ == "__main__":
    main()