# Competitor Analysis Deep Research — Prompt Template

Reusable prompt scaffold for deep research competitor analysis on any company.
Replace all `{PLACEHOLDERS}` with company-specific details.

---

## Prompt

/deep-research

Perform a deep research on analyzing competitors to {COMPANY_NAME} within {GEOGRAPHIC_SCOPE} and nationwide. Go into great detail about how the competitors differentiate themselves from us and what are some areas that we could improve upon to grow our {BUSINESS_TYPE} business within {GEOGRAPHIC_SCOPE}.

Use the current website to learn more about {COMPANY_NAME} so that you can more accurately search for competitors.

{COMPANY_NAME} Website: {WEBSITE_URL}

---

## Research Execution Notes (for the agent)

### Phase 1: Scrape the Subject Company Website
- Fetch the homepage and all subpages via `curl` (use `execute_code` to batch)
- If the site is WordPress, use the WP REST API: `curl -sL '{URL}/wp-json/wp/v2/pages?per_page=50'` and `curl -sL '{URL}/wp-json/wp/v2/posts?per_page=20'`
- **PITFALL: WP REST API may return empty/404 even on WordPress sites.** Some WordPress hosts disable the REST API or the site may use a non-WordPress CMS (e.g., Laravel/Statamic, Storyblok headless CMS). If the API returns empty, fall back to direct HTML scraping: strip `<script>`, `<style>`, and all tags, then extract meaningful text lines (>20 chars). Also extract `<title>`, `<meta name="description">`, and navigation links to discover sub-pages.
- **PITFALL: Website may not reflect all served verticals.** The subject company's public website may market only a subset of what they actually do. Cross-reference the website findings with any additional context the user provides about the company's operations. Flag discrepancies — a website that only mentions kiosks when the company also serves vending, ATMs, and EV charging is itself a competitive vulnerability to note in the report.
- Extract: services offered, industries served, geographic coverage, facility locations/sizes, technology stack, years in business, ownership type, leadership team, value propositions, certifications
- This profile becomes the baseline for all competitor comparisons

### Phase 2: Identify Competitor Categories
Break competitors into 3-5 categories based on the company profile:
1. **Direct local competitors** — same geography, same services
2. **Regional competitors** — broader Midwest/regional players with overlapping services
3. **National competitors** — large players with overlapping service lines
4. **Niche/specialized competitors** — companies serving the same specialized equipment/industry niches
5. **Adjacent competitors** — companies offering substitute services (e.g., transportation companies with warehousing add-ons)

### Phase 3: Research Each Category
- Spawn parallel `delegate_task` subagents for each category (note: subagents may only have Context7 tools, not web search — see pitfall below)
- Search via **Marginalia Search (old interface)**: `curl -sL 'https://old-search.marginalia.nu/search?query={QUERY}'`
- **Mine industry directories** (see `references/web-research-techniques.md` for URLs):
  - Warehousing/3PL: Leonard's Guide state directories
  - Other industries: find equivalent trade association directories
- Fetch competitor websites directly via `curl` — get meta descriptions, about pages, services pages
- For each competitor, capture: name, locations, square footage/fleet size, services, industries, technology, years in business, ownership, key differentiators

### Phase 4: Research Industry Context
- Market size, growth rates, CAGR projections
- Key industry trends (technology, labor, regulation, consumer behavior)
- Geographic market advantages (why companies choose this location)
- How small/mid-size family-owned companies compete vs. national giants

### Phase 5: Synthesize
- Build competitive matrix tables (competitor × capability)
- Identify differentiation patterns — what do competitors do that the subject company doesn't?
- Identify improvement areas — concrete, actionable recommendations
- Organize by: immediate (0-6 months), near-term (6-18 months), strategic (18-36 months)

### PITFALL: Subagent Web Tool Limitations
`delegate_task` with `toolsets=["web"]` may produce subagents that only have Context7 MCP documentation tools — NOT general web search/fetch. When parallel subagents return training-knowledge summaries instead of live web research, fall back to doing web research yourself via `terminal` + `curl` and `execute_code`. Use the techniques in `references/web-research-techniques.md`.