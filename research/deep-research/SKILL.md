---
name: deep-research
description: "Use when the user wants comprehensive, multi-source research on ANY topic — companies, technologies, historical events, scientific questions, industries, policy, trends, or competitive landscapes. Triggered by 'deep research on X', 'research X in depth', 'tell me everything about X', 'comprehensive analysis of X', 'deep dive into X', '/deep-research X', or any request for thorough, sourced investigation. Produces a structured report with executive summary, key findings, detailed analysis across multiple angles, and cited sources."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [deep-research, research, analysis, web-research, synthesis, report]
    related_skills: [deepstock, sp500, arxiv, youtube-content]
---

# Deep Research

## Overview

Perform comprehensive, multi-source research on any topic and deliver a structured, sourced report. This skill guides a multi-phase research process: understanding the query, identifying key angles, conducting parallel web research, optionally spawning deep-dive subagents for complex subtopics, and synthesizing everything into a clear, actionable report.

Unlike a quick web search that returns a paragraph, deep research means covering the topic from multiple angles, cross-referencing sources, and producing a report the user can rely on for decisions, writing, or further investigation.

## When to Use

- "deep research on quantum computing"
- "research the EV battery supply chain in depth"
- "tell me everything about the Suez Canal blockage"
- "comprehensive analysis of Starlink's competitive position"
- "deep dive into CRISPR gene editing recent breakthroughs"
- "/deep-research fusion energy progress 2026"
- "I need a thorough briefing on the US chip export controls"
- Any request where the user wants depth, multiple perspectives, and sources

**Don't use for:** simple fact-lookup ("what is the capital of France"), quick summaries ("give me a TLDR on X"), stock-specific research (use `deepstock`), market-wide scans (use `sp500`), or academic paper searches (use `arxiv`).

---

## Research Process

Execute research in phases. Do not skip phases or rush to output — thoroughness is the point.

### Phase 1: Understand and Scope

Before searching, clarify the topic:

1. **Parse the query.** What exactly is the user asking? What's the scope? Is there a time frame (e.g., "last 5 years," "recent developments")?
2. **Identify key angles.** Break the topic into 3-5 natural subtopics to research. For example, "quantum computing" breaks into: (a) how it works / technical state, (b) key players and funding, (c) recent breakthroughs, (d) applications and timeline, (e) risks and competition.
3. **If the query is ambiguous**, ask one clarifying question. "Deep research on Apple" — do they mean the company, the fruit industry, or Apple's AI strategy? Don't guess; clarify.

### Phase 2: Broad Research (Parallel)

Run 3-5 initial web searches covering the key angles. Use `terminal` with `curl` or `python3` to programmatically manage searches when you need many results. For each angle:

- Search with specific queries, not just the topic name. "quantum computing error correction breakthrough 2026" > "quantum computing"
- Open and extract content from the 2-3 most substantive results per angle
- Note source URLs, publication dates, and author/organization credibility

**Parallel execution pattern:**
When you have 3+ searches, spawn them as parallel `delegate_task` subagents — one per angle:

```
delegate_task(
    goal="Research angle: <angle description> for the topic '<topic>'",
    context="Search the web thoroughly for this specific angle. Find at least 3 credible sources. For each source, extract key facts, data points, quotes, and the source URL. Return a structured summary with citations.",
    toolsets=["web"]
)
```

For simpler topics (2-3 angles), do the searches inline with `terminal` + `curl`.

**PITFALL — subagent web tool limitations:** `delegate_task` with `toolsets=["web"]` may produce subagents that only have Context7 MCP documentation tools — NOT general web search/fetch. When parallel subagents return training-knowledge summaries instead of live web research, fall back to doing web research yourself via `terminal` + `curl`. Use `execute_code` to batch multiple `curl` calls and process results programmatically. See `references/web-research-techniques.md` for proven search and content extraction methods (Marginalia Search, WordPress REST API, industry directory mining).

### Phase 3: Deep Dives (Conditional)

For complex topics where Phase 2 reveals subtopics that need deeper investigation:

- Spawn additional `delegate_task` subagents for specific deep dives
- These produce standalone mini-reports on their subtopic
- The main agent weaves them into the final report

**When to deep-dive:** The angle has substantial depth (multiple sub-angles, conflicting sources, technical complexity). **When to skip:** A straightforward angle covered well by 2-3 sources.

### Phase 4: Synthesize

Combine all findings into a coherent report. This is where value is created — anyone can run 5 Google searches. Synthesis means:

1. **Cross-reference sources.** Do multiple sources agree? Where do they conflict? Note disagreements explicitly.
2. **Identify patterns.** What themes recur across angles? What's the dominant narrative?
3. **Note gaps.** What important questions remain unanswered? Be honest about uncertainty.
4. **Form a perspective.** Don't just list facts — provide a synthesized view. What does it all mean?

### Phase 5: Deliver the Report

Use the output template below. Adapt section headings to fit the topic — the template is a guide, not a straitjacket.

---

## Output Format

```markdown
# 🔬 Deep Research: {TOPIC}

**Date:** {TODAY'S DATE}
**Scope:** {One sentence describing what was researched and any time/domain boundaries}
**Sources consulted:** {N}

---

## Executive Summary

{3-5 sentences that give a busy reader everything they need to know. The most important findings, the dominant narrative, and the bottom line. Write this LAST — after you understand the full picture.}

---

## Key Findings

1. **{Finding 1}** — {1-2 sentences with the most impactful data point or insight}
2. **{Finding 2}** — {1-2 sentences}
3. **{Finding 3}** — {1-2 sentences}
4. **{Finding 4}** — {1-2 sentences}
5. **{Finding 5}** — {1-2 sentences}

---

## {ANGLE 1: Descriptive Heading}

{3-5 paragraphs. Lead with the most important information. Include specific data, dates, names, numbers. Attribute claims to sources. If sources disagree, say so.}

> **Key data point:** {Pull out the most striking statistic or quote from this section}

---

## {ANGLE 2: Descriptive Heading}

{3-5 paragraphs. Same structure — lead with importance, support with evidence, cite sources.}

---

## {ANGLE 3: Descriptive Heading}

{3-5 paragraphs.}

---

## {ANGLE 4+ as needed}

---

## Perspectives & Debates

{1-2 paragraphs on where experts disagree, what the competing narratives are, and what's still uncertain. This section is critical — it shows you've done balanced research, not cherry-picked one narrative.}

---

## Timeline / Key Events

| Date | Event | Significance |
|------|-------|-------------|
| {Date} | {Event} | {Why it matters} |

{5-10 key events that trace the story arc of the topic}

---

## Key Players / Stakeholders

| Entity | Role | Significance |
|--------|------|-------------|
| {Name} | {What they do} | {Why they matter to this topic} |

---

## Outlook / What to Watch

{2-3 paragraphs on where things are heading. What are the key variables? What would change the trajectory? What should the reader watch for in the next 6-12 months?}

---

## Sources

{Numbered list of all sources consulted, with URLs and brief descriptions}

1. [{Title}]({URL}) — {Source/author}, {date}. {One sentence on what this source contributed.}
2. [{Title}]({URL}) — {Source/author}, {date}. {One sentence.}
...

---

*Research conducted on {date}. Information may change. This is AI-assisted research — verify critical facts before relying on them for decisions.*
```

---

## Research Strategy by Topic Type

| Topic Type | Key Angles to Cover | Special Considerations |
|---|---|---|
| **Technology** | How it works, key players, recent breakthroughs, applications, timeline to maturity, competitive landscape, regulatory issues | Focus on technical accuracy. Cite arXiv papers and engineering sources. |
| **Company/Business** | Business model, financials, competitive position, leadership, strategy, risks, market context | Use `deepstock` if the user wants a BUY/SELL verdict. This skill is for business analysis, not investment advice. |
| **Competitor Analysis** | Subject company profile, direct competitors, indirect competitors, market position, differentiation, gaps/opportunities, industry trends | Scrape the subject company's website FIRST to inform competitor searches. Mine industry directories (e.g., Leonard's Guide for warehousing) for small/mid-size competitors search engines miss. Search by geography + service type. Include competitive matrix tables. See `references/web-research-techniques.md` for directory URLs. |
| **Industry/Market** | Market size & growth, key players, trends, regulations, barriers to entry, disruption risks | Include TAM/SAM/SOM if available. Cite industry reports. |
| **Policy/Regulation** | What the policy does, who it affects, political context, implementation status, impact analysis, supporters/opponents | Present multiple viewpoints fairly. Cite government sources and advocacy groups. |
| **Science/Research** | Current understanding, recent breakthroughs, key researchers/institutions, remaining unknowns, practical implications | Cite papers (use `arxiv` if relevant). Distinguish between consensus and frontier research. |
| **Historical Event** | Context/background, key events timeline, causes, consequences, different historical interpretations, modern relevance | Cite historians and primary sources. Note historiographical debates. |
| **Person/Figure** | Background, key achievements, controversies, influence/legacy, current activities | Balance accomplishments with criticisms. Cite biographical sources. |

---

## Common Pitfalls

1. **Too few sources.** Deep research means 8-15+ sources minimum. A report based on 3 sources is a summary, not deep research.

2. **Single-narrative bias.** If all your sources agree, you haven't looked hard enough. Every interesting topic has opposing viewpoints. Find and present them.

3. **Vague claims without data.** "The market is growing rapidly" — how rapidly? What's the CAGR? What's the source? Every claim needs a number or a citation, preferably both.

4. **Source quality blindness.** A Reddit comment and a peer-reviewed paper are not equal. Prioritize: primary sources > reputable journalism > industry reports > academic papers > blogs > social media. Note source quality in the report.

5. **Executive summary written first.** Write the executive summary LAST. You cannot summarize what you haven't yet understood. Writing it first locks in an incomplete picture.

6. **Ignoring recency.** A 2019 article about AI is archaeological. Check publication dates. For fast-moving topics, prioritize sources from the last 6-12 months. For historical context, older sources are fine.

7. **No gap acknowledgement.** "Here's what we know, and here's what we don't know" is a sign of good research. Pretending to have complete knowledge when sources are thin is misleading.

8. **Skipping the synthesis phase.** Collecting facts is research. Weaving them into insight is analysis. The user wants analysis.

9. **Too long or too short.** Aim for a report that takes 5-10 minutes to read. Shorter = missed depth. Longer = the user won't finish it. Use clear section breaks so they can skim.

10. **Fabricating data.** Never invent statistics, dates, or quotes. If you can't find a data point, say "data unavailable" rather than guessing. The user trusts this report — don't betray that trust.

---

## Templates

- **`templates/competitor-analysis-prompt.md`** — Reusable prompt scaffold for deep research competitor analysis on any company. Includes execution notes for website scraping, competitor categorization, directory mining, and synthesis. Use when the user asks for `/deep-research` on competitors for a specific company and provides a website URL.
- **`references/bsl-competitor-knowledge-bank.md`** — Condensed competitor profiles, market data, and search techniques from the June 2026 BSL competitive analysis. Load this when doing any follow-up research on Brendamour Specialized Logistics, its competitors, or the specialized equipment logistics industry to avoid re-researching known facts.

---

## Verification Checklist

- [ ] Topic scope clarified (time frame, domain, depth expected)
- [ ] 3-5 key angles identified before research begins
- [ ] 8+ sources consulted across multiple domains
- [ ] Source URLs and dates captured for every factual claim
- [ ] At least one opposing/critical perspective included
- [ ] Executive summary written last, after full synthesis
- [ ] Data claims backed by specific numbers and sources
- [ ] Sources assessed for quality (primary > secondary > tertiary)
- [ ] Timeline or key events section included where relevant
- [ ] Key players/stakeholders section included where relevant
- [ ] "What we don't know" or uncertainties explicitly noted
- [ ] Outlook / forward-looking section included
- [ ] Report is 5-10 minute read with clear section breaks
- [ ] Disclaimer included at bottom
- [ ] No fabricated data, dates, or statistics
