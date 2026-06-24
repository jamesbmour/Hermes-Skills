# Large-Scale Bulk Ingest Pattern

Proven pattern for ingesting 100+ source files into an LLM wiki in a single session.

## When to Use

- User provides a large crawled documentation site (100+ markdown files)
- User asks to "process all files" from a directory
- User has an existing raw source directory that needs to be converted to wiki pages

## Step-by-Step

### 1. Copy raw sources first
```bash
cp -r /path/to/source-dir $WIKI/raw/articles/<name>
```
Get all sources into the immutable layer before creating any wiki pages.

### 2. Build a structured inventory
Use `execute_code` to scan all `.md` files, extract frontmatter (title, url),
determine section and page type, and output a JSON inventory. This drives worker
assignment and ensures no files are missed.

```python
import re, json
from pathlib import Path

source_dir = "/workspace/wiki/raw/articles/<name>"
inventory = {}
for filepath in sorted(Path(source_dir).rglob("*.md")):
    text = filepath.read_text(encoding='utf-8', errors='replace')
    # Extract frontmatter title and url
    # Determine section from directory structure
    # Classify page type (api-object, blog, sdk, etc.)
    # Record: rel_path, title, url, section, page_type, headings, lines
```

### 3. Update SCHEMA.md tags BEFORE creating pages
Add all domain-specific tags to the taxonomy. Workers cannot reference tags
that don't exist in the schema yet — they'll either skip them or create
inconsistencies.

### 4. Dispatch parallel workers
Split by natural section boundaries (module, directory). Up to 3 concurrent
via `delegate_task`. Give each worker:
- Exact file list with source paths and target wiki page names
- Frontmatter template (title, created, updated, type, tags, sources)
- Cross-reference guidance (which modules link to which)
- Page size limit (under 200 lines)
- Tags from the SCHEMA taxonomy
- At least 2 [[wikilinks]] per page

**Sizing rule:** ~40-50 entity files per worker maximum. Each file = 1 read + 1 write
= 2 tool calls. Workers cap at ~50 tool calls. Workers assigned 90+ files will
hit the limit before finishing — plan a second round for the overflow.

### 5. Verify and redispatch
After all workers complete, check the filesystem:
```bash
find $WIKI/entities -name "*.md" | wc -l
find $WIKI/concepts -name "*.md" | wc -l
```
Compare against expected counts. Identify missing pages by listing source files
and checking which wiki pages don't exist yet. Redispatch workers for gaps.

**Critical:** Workers that report "timeout" may still have completed most of their
work. Always verify by listing the output directory, not by trusting the status.

### 6. Generate index.md programmatically
For 100+ pages, use `execute_code` to scan all `.md` files in `concepts/` and
`entities/`, extract titles from frontmatter, sort alphabetically, and write
the complete index in one pass.

### 7. Write the log entry
Cover: source count, page count by type, modules covered, cross-references
implemented, and any issues encountered (e.g. worker timeouts).

## Real-World Example

**Sage Intacct Developer Documentation** (June 2026):
- **Source:** 327 crawled markdown files from developer.intacct.com (4.6MB)
- **Output:** 233 wiki pages (36 concept pages, 197 entity pages)
- **Workers:** 3 parallel in round 1 (Worker A: 89 files→95 pages, Worker B: 108
  files→16 concept pages then hit limit, Worker C: 61 files→13 pages)
- **Round 2:** 3 more workers for the 108 missing entity pages (B1: 41 pages,
  B2: 47 pages, B3: 21 pages)
- **Total time:** ~25 minutes across both rounds
- **Key lesson:** Worker B timed out on 108 files but Worker B1 (41 files)
  completed all pages despite also timing out — the timeout happened during
  the reporting phase, not the file writing phase. Always check the filesystem.