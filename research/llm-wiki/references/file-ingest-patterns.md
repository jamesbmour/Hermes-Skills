# File Ingest Patterns for LLM Wiki

Practical patterns for ingesting files generated during research sessions into the wiki.

## Reading Files for Ingest with execute_code

When reading a file via `read_file` inside `execute_code` to ingest it as a raw source,
the output has line-number prefixes (`NUM|CONTENT`). Strip them before computing sha256
or saving as a raw source:

```python
from hermes_tools import read_file, write_file
import hashlib

result = read_file(path="/path/to/report.md", limit=2000)
raw = result.get("content", "")
lines = raw.split("\n")
clean = []
for line in lines:
    if "|" in line:
        parts = line.split("|", 1)
        clean.append(parts[1] if len(parts) > 1 else line)
    else:
        clean.append(line)
body = "\n".join(clean)
sha = hashlib.sha256(body.encode()).hexdigest()

# Save with raw frontmatter
frontmatter = f"""---
source_url: https://example.com/
ingested: 2026-06-23
sha256: {sha}
---

"""
write_file(path=f"{WIKI}/raw/articles/source-name.md", content=frontmatter + body)
```

This ensures the raw source file contains only the original content, not read_file's
line-number annotations. The sha256 is computed over the clean body only.

## Ingesting a Research Report as a Wiki Source

When a deep research report or analysis has been generated during a session:

1. **Save the report** to the workspace (e.g., `/workspace/Brendamour/report.md`)
2. **Copy into raw/articles/** with frontmatter (source_url, ingested date, sha256)
3. **Create entity pages** for each notable company/organization/person mentioned
4. **Create concept pages** for industry trends, market data, or technical concepts
5. **Create comparison pages** for competitive matrices or side-by-side analyses
6. **Cross-reference** all pages via `[[wikilinks]]` (minimum 2 outbound per page)
7. **Update index.md** — add entries under the correct sections, bump total page count
8. **Append to log.md** — document the ingest with source, page count, and files created

### Entity Page Template for Competitors

```yaml
---
title: Company Name
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity
tags: [competitive, warehousing]
sources: [raw/articles/source-file.md]
confidence: high
---
```

Include: overview, key facts (location, sq ft, services, industries), competitive
differentiation vs subject company, and source references via `[[wikilinks]]`.

### Comparison Page Template

```yaml
---
title: Competitive Landscape Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: comparison
tags: [competitive, comparison]
sources: [raw/articles/source-file.md]
confidence: high
---
```

Include: what's compared, comparison table (competitor, size, location, differentiator,
threat level), subject company's advantages and vulnerabilities, industry context.