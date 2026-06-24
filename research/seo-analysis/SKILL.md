---
name: seo-analysis
description: "Use when the user wants an SEO rating, SEO audit, SEO analysis, SEO evaluation, or SEO improvements for a website or webpage. Also triggers on requests to check search engine optimization, page optimization, content optimization, meta tags, keyword usage, or to improve search rankings — even if the user doesn't explicitly say 'SEO.'"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, search-engine-optimization, web-audit, content-analysis, keyword-research, meta-tags]
    related_skills: [crawl4ai-skill]
---

# SEO Analysis Skill

## Overview

Evaluates a webpage against a 12-point SEO content evaluation framework, produces a numeric score with a letter grade, and generates copy-paste-ready improvements. The skill crawls the target URL, extracts page elements (title, meta, headers, content, images, URL, links), evaluates each criterion, and outputs a structured report.

## When to Use

- User asks for an "SEO rating," "SEO audit," "SEO analysis," or "SEO score" for a website
- User wants to check or improve a page's search engine optimization
- User asks "how is my SEO?" or "can you rate my website?"
- User wants keyword usage, meta tags, or content optimization reviewed
- User wants to improve search rankings or page optimization for a specific URL

**Don't use for:** General website design feedback unrelated to SEO, PPC/ad optimization, social media optimization, or backlink profile analysis (which requires external tools like Ahrefs/SEMrush).

## Prerequisites

- `crawl4ai-skill` CLI installed (`pip install crawl4ai-skill`). This is the primary tool for fetching page content.
- If crawl4ai-skill is not available, fall back to `curl` to fetch raw HTML and parse it manually.

## Workflow

### Step 1: Crawl the Target Page

Fetch the page content using crawl4ai-skill in raw markdown and also fetch raw HTML for meta/structural analysis:

```bash
# Get clean markdown content for content analysis
crawl4ai-skill crawl <URL> --format raw_markdown --output /tmp/seo_content.md

# Get raw HTML for structural analysis (meta tags, headers, image alt text, schema)
crawl4ai-skill crawl <URL> --format raw_markdown --output /tmp/seo_raw.md
```

If crawl4ai-skill is unavailable, use curl:
```bash
curl -sL <URL> -o /tmp/seo_raw.html
```

### Step 2: Extract Page Elements

From the fetched content, identify and extract:
- **Page URL** — analyze structure, length, keyword presence
- **Title tag** (`<title>`) — exact text and character count
- **Meta description** — exact text and character count
- **All headers** — H1, H2, H3, H4, H5, H6 with their text
- **Body content** — word count, keyword frequency
- **Images** — all `<img>` tags, their `src` filenames and `alt` attributes
- **Internal links** — links pointing to the same domain
- **External links** — links pointing to other domains
- **Schema markup** — JSON-LD, microdata, or RDFa present
- **robots.txt** — fetch `https://<domain>/robots.txt` and check
- **sitemap.xml** — fetch `https://<domain>/sitemap.xml` and check
- **Mobile responsiveness** — check viewport meta tag and CSS media queries
- **Page speed indicators** — image sizes, script/CSS counts, inline vs external

### Step 3: Identify Keywords

Determine primary and secondary keywords by:
1. Analyzing the page title, H1, and first paragraph for keyword themes
2. Checking what keywords the user provided (if any)
3. If no keywords provided, infer primary keyword from H1 and title, then identify secondary keywords from H2-H3 headers and content themes
4. Use crawl4ai-skill search to validate keyword relevance if needed

### Step 4: Run the 12-Point Evaluation

Evaluate each criterion below. Score each on a 0–10 scale. Provide specific findings (not just "pass/fail") — quote the actual element text and explain why it scored that way.

---

#### 1. Keyword Research

- Identify the primary keyword and 3–5 secondary keywords
- Assess whether these keywords are well-chosen (relevance to content, search intent match)
- If the user provided target keywords, evaluate against those
- **Scoring:** 10 = keywords clearly identified, highly relevant, good mix of primary + secondary. 0 = no discernible keyword strategy.

#### 2. Content Analysis (Keyword Usage & Density)

- Check primary keyword presence in: title, meta description, H1, at least one H2, body content (first 100 words, throughout, last 100 words)
- Calculate keyword density: (keyword occurrences ÷ total words) × 100
- Ideal density: 1–2%. Below 0.5% = under-optimized. Above 3% = keyword stuffing risk.
- Check for LSI/related keyword usage (synonyms, related terms)
- **Scoring:** 10 = keyword in all key positions, density 1–2%, natural usage. 0 = keyword absent or severely stuffed.

#### 3. Title Tag

- Check title length (ideal: 50–60 characters, max ~60 for full SERP display)
- Verify primary keyword is in the title, ideally near the beginning
- Assess compelling/click-worthy quality (numbers, power words, brackets, emotional triggers)
- **Scoring:** 10 = keyword in title, 50–60 chars, compelling. 0 = missing, too long/short, or keyword absent.

#### 4. Meta Description

- Check meta description length (ideal: 150–160 characters)
- Verify primary keyword is included
- Assess engagement quality (CTA, benefit statement, urgency)
- Check it's not auto-generated or duplicate of the first paragraph
- **Scoring:** 10 = keyword present, 150–160 chars, engaging with CTA. 0 = missing, too long/short, or keyword absent.

#### 5. Header Tags Structure

- Verify exactly one H1 on the page (multiple H1s is a negative)
- Check H2-H6 are used hierarchically and descriptively
- Verify primary keyword in H1, secondary keywords in H2s where natural
- Check headers aren't generic ("Welcome", "About Us") — they should be descriptive and keyword-rich
- **Scoring:** 10 = single H1 with keyword, logical H2-H6 hierarchy, descriptive headers. 0 = no headers, multiple H1s, or generic headers.

#### 6. Content Quality

- Assess originality and informativeness — does it provide unique value?
- Check readability: short paragraphs (3-5 sentences), bullet points, numbered lists, bold key terms
- Check content length — is it comprehensive enough for the topic? (thin content <300 words is a negative)
- Verify presence of internal links (2-5 relevant) and external links (1-3 authoritative sources)
- Assess overall value to the reader — would a human find this useful?
- **Scoring:** 10 = original, well-structured, comprehensive, good link profile. 0 = thin, duplicate-feeling, no links, wall of text.

#### 7. Image Optimization

- Check all images have `alt` attributes (missing alt = negative)
- Verify alt text is descriptive and includes keywords where relevant (not stuffed)
- Check image filenames are descriptive (e.g., `blue-widget-example.jpg` not `IMG_0042.jpg`)
- Note if images appear uncompressed (very large file sizes, no width/height attributes, no lazy loading)
- **Scoring:** 10 = all images have descriptive alt + filenames, optimized. 0 = no images or all images missing alt text.

#### 8. URL Structure

- Check URL length (shorter is better, ideally <75 characters)
- Verify URL is descriptive and includes primary keyword
- Check for stop words, special characters, parameters, or unnecessary numbers
- Verify URL uses hyphens (not underscores or spaces)
- Check HTTPS is enabled
- **Scoring:** 10 = short, keyword-rich, HTTPS, clean hyphens. 0 = long, dynamic parameters, no keyword, HTTP.

#### 9. Mobile-Friendliness

- Check for viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Look for responsive CSS (media queries, flexible layouts, `max-width` on images)
- Check font sizes are readable on mobile (not tiny fixed px sizes)
- Note any known mobile issues (Flash usage, tiny tap targets, horizontal scroll)
- **Scoring:** 10 = responsive, viewport tag present, mobile-optimized. 0 = no viewport tag, fixed-width layout.

#### 10. Page Speed Indicators

- Count external CSS and JS files (many = slower)
- Check if images are appropriately sized
- Look for render-blocking resources (CSS/JS in `<head>` without async/defer)
- Check for lazy loading on images (`loading="lazy"`)
- Note: Full PageSpeed test requires Google's tool — note this limitation and recommend the user run PageSpeed Insights separately for definitive scores
- **Scoring:** 10 = minimal render-blocking, lazy-loaded images, few external resources. 0 = many render-blocking scripts, uncompressed images, no optimization.

#### 11. User Engagement (CTAs & Multimedia)

- Check for clear calls-to-action (buttons, links with action verbs like "Get," "Download," "Try," "Sign up")
- Assess presence of engaging multimedia: images, videos, infographics, interactive elements
- Check for social proof (testimonials, reviews, ratings)
- Look for engagement signals (comment sections, social share buttons)
- **Scoring:** 10 = clear CTA, multimedia present, social proof. 0 = no CTA, text-only, no engagement elements.

#### 12. Technical SEO

- Fetch and check `robots.txt` — is it present and properly configured?
- Fetch and check `sitemap.xml` — is it present and up to date?
- Check for schema markup (JSON-LD, microdata, RDFa) — type present (Article, Product, FAQ, BreadcrumbList, etc.)
- Check canonical tag presence: `<link rel="canonical" href="...">`
- Check for Open Graph and Twitter Card meta tags
- Check for hreflang tags (if multi-language)
- **Scoring:** 10 = robots.txt + sitemap + schema + canonical + OG tags all present. 0 = none present.

---

### Step 5: Calculate Overall Score

Sum all 12 category scores (each 0–10) for a total out of 120, then convert to a percentage and assign a letter grade:

| Score Range | Grade |
|---|---|
| 90–100% | A (Excellent) |
| 80–89% | B (Good) |
| 70–79% | C (Needs Improvement) |
| 60–69% | D (Poor) |
| Below 60% | F (Critical Issues) |

### Step 6: Generate Copy-Paste Improvements

For each criterion that scored below 8/10, generate specific, ready-to-use improved copy. Format each improvement as a labeled code block that the user can directly copy and paste into their CMS or HTML.

**Improvement output format:**

```
### [Criterion Name] — Current Score: X/10

**What's wrong:** [Specific finding with quoted text]

**Improved version (copy-paste ready):**

[The actual improved element — e.g., new title tag, new meta description, new H1, etc.]

[For content improvements, provide the full revised section text]
```

**Rules for improvements:**
- Title tag: provide the exact new `<title>` text, within 50-60 chars, keyword near front
- Meta description: provide the exact new meta description text, within 150-160 chars, with keyword + CTA
- Headers: provide revised H1/H2 text with keywords naturally integrated
- Content: provide revised paragraphs or sections with improved keyword density, better structure, added bullet points
- Image alt text: provide exact alt text for each image that needs it
- URL: suggest a cleaner URL structure
- Technical: provide exact code snippets (schema markup, canonical tag, OG tags, viewport tag)
- CTAs: suggest specific CTA button text and placement

## Output Format

Present the full report in this structure:

```markdown
# SEO Analysis Report for [URL]

**Date:** [date]
**Target Keywords:** Primary: [keyword] | Secondary: [list]

---

## Overall Score: [XX/120] ([XX%]) — Grade [X]

## Scorecard

| # | Criterion | Score | Key Finding |
|---|---|---|---|
| 1 | Keyword Research | X/10 | [one-line finding] |
| 2 | Content Analysis | X/10 | [one-line finding] |
| 3 | Title Tag | X/10 | [one-line finding] |
| 4 | Meta Description | X/10 | [one-line finding] |
| 5 | Header Tags | X/10 | [one-line finding] |
| 6 | Content Quality | X/10 | [one-line finding] |
| 7 | Image Optimization | X/10 | [one-line finding] |
| 8 | URL Structure | X/10 | [one-line finding] |
| 9 | Mobile-Friendliness | X/10 | [one-line finding] |
| 10 | Page Speed | X/10 | [one-line finding] |
| 11 | User Engagement | X/10 | [one-line finding] |
| 12 | Technical SEO | X/10 | [one-line finding] |

## Detailed Findings

[For each criterion, provide: score, what was found (with quoted text), and what needs improvement]

## Copy-Paste Improvements

[For each criterion scoring below 8/10, provide ready-to-paste improved copy in labeled code blocks]

## Priority Action Items

1. [Highest impact fix]
2. [Second highest]
3. [Third highest]
```

## Common Pitfalls

1. **Guessing at keywords.** If the user doesn't provide target keywords, infer them from the page content (H1, title, first paragraph) rather than asking. State your inferred keywords clearly in the report.

2. **Scoring too leniently.** Be honest in scoring. A page with no meta description is a 0/10 for that criterion, not a 5/10. The user benefits from accurate scores, not encouraging ones.

3. **Generic improvements.** "Make your title more compelling" is useless. Provide the exact improved title text. "Add alt text to images" is useless. Provide the exact alt text for each image.

4. **Ignoring the user's keywords.** If the user specifies target keywords, always evaluate against those — don't substitute your own inferred keywords.

5. **Forgetting to fetch robots.txt and sitemap.** These are separate fetches from the main page. Always check `<domain>/robots.txt` and `<domain>/sitemap.xml`.

6. **Not checking for multiple H1s.** Multiple H1 tags is a common SEO mistake. Count them carefully from the HTML.

7. **Character counting errors.** Use exact character counts for title (50-60) and meta description (150-160). Don't estimate — count programmatically.

## Verification Checklist

- [ ] Target URL was successfully crawled and content extracted
- [ ] Primary and secondary keywords identified and stated
- [ ] All 12 criteria evaluated with specific findings (not generic)
- [ ] Each criterion has a numeric score (0-10) with justification
- [ ] Overall score calculated correctly (sum / 120, percentage, letter grade)
- [ ] Copy-paste improvements provided for every criterion scoring below 8/10
- [ ] Improvements are specific, ready-to-paste text (not instructions)
- [ ] Priority action items listed in order of impact
- [ ] robots.txt and sitemap.xml checked
- [ ] Character counts for title and meta description are exact