---
name: startup-investment-due-diligence
description: "Analyze private company investment opportunities from pitch decks, investment memos, and financial models. Verify market size claims against independent research, stress-test unit economics, research competitors and category history, check for disclosure/legal red flags, size the capital gap, and produce a PASS/INVEST verdict with a diligence checklist and terms to insist on. Use when the user provides a pitch deck, investment memo, or fundraising materials for a private company and wants investment analysis. Triggered by 'analyze this investment opportunity', 'review this pitch deck', 'should I invest in this company', 'due diligence on this startup', 'research this company and competitors', or similar."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [investment, due-diligence, pitch-deck, startup, private-company, angel-investing, market-research, unit-economics]
    related_skills: [deepstock, deep-research, equity-research]
---

# Startup Investment Due Diligence

Analyze a private company investment opportunity from its pitch deck (and any accompanying memo/model), independently verify every material claim, and deliver a structured PASS/INVEST verdict with a diligence checklist. This is angel/VC-style due diligence, not public-equity research — there are no ticker symbols, no analyst consensus, no SEC filings. The work is claim verification, competitive context, and risk identification.

## When to Use

- User provides a pitch deck PDF and asks for investment analysis
- User shares an investment memo or financial model for a private company
- User asks "should I invest in this company?" about a private/startup business
- User says "research this company and competitors' market size"
- User wants an investment strategy for a private placement, SAFE, or angel round

**Don't use for:** public stock tickers (use `deepstock`), general company research without an investment decision (use `deep-research`), or public equity research snapshots (use `equity-research`).

---

## Process

### Phase 1: Extract All Materials

1. **Extract the pitch deck.** Use `pymupdf` (via terminal or execute_code) for text-based PDFs. If the PDF is image-based/scanned, use `marker-pdf` or the `ocr-and-documents` skill.
2. **Extract supporting documents.** Investment memos (.docx → `python-docx`), financial models (.xlsx → `openpyxl`), term sheets, cap tables — extract everything provided.
3. **Read all materials fully** before starting research. Note every quantitative claim, competitive claim, team claim, and market size figure for verification.

**Pitfall:** `execute_code` runs in a sandbox that may not share the terminal's Python environment. If `import pymupdf` fails in execute_code, run extraction via `terminal` with `python3 -c "..."` instead — the terminal uses the system Python where packages are installed.

### Phase 2: Verify Market Size Claims

This is where most decks stretch the truth. The deck will cite a large TAM/SAM/SOM — verify each against independent research.

1. **Identify every market size claim** in the deck (TAM, SAM, SOM, "converging markets," growth rates).
2. **Search independently** for each claimed market. Use `parallel_search_web` with 4-5 queries covering: the claimed market, the actual served market, adjacent markets, and market growth rates.
3. **Identify the TRUE served market.** Decks often cite a broad market the company doesn't actually compete in (e.g., claiming a $254B QSR TAM for a hot-food vending kiosk business). Find the specific sub-market the company actually operates in.
4. **Check for double-counting.** "Converging market" TAMs that sum multiple sectors often overlap and double-count.
5. **Compute the honest market share.** At the company's own market share goal, what revenue does that imply? Compare to their projections.

**Key sources:** Future Market Insights, Mordor Intelligence, Grand View Research, Statista, IMARC, Market Data Forecast, Renub. Cross-reference 2-3 sources per market.

### Phase 3: Stress-Test Unit Economics

1. **Extract the "model" unit economics** from the deck — revenue per unit, orders/day, AOV, cost ratios, margins.
2. **Compute the ACTUAL unit economics** from reported totals (total revenue ÷ total units). This reveals the gap between the model and reality.
3. **Build a stress test table.** Apply the deck's cost ratios across a range of volumes (from model down to 50% of current). Identify the break-even volume.
4. **Flag if the current fleet is below break-even** on a fully-costed basis (including depreciation, host share, spoilage).
5. **Check for cost changes over time.** Has the per-unit cost changed since earlier filings/news? Increasing capex per unit worsens the path to profitability.

### Phase 4: Research Competitors and Category History

1. **Find the closest analog.** Is there a company that does what this company does, at larger scale? How much capital did they raise? How many units? What revenue per unit?
2. **Find the category graveyard.** What companies in this category have failed? How much did they burn? Why did they fail? This establishes the base rate.
3. **Research incumbent threats.** Who owns the distribution channels this company targets? Can they add this as a feature rather than a new business?
4. **Verify "unique" claims.** Decks often claim a differentiator is "unique" or "only we do this." Search specifically for whether competitors already offer it.
5. **Check for competitor-incumbent partnerships.** A competitor partnering with a major incumbent (e.g., Sodexo partnering with a kiosk startup) is a stronger signal than a startup claiming they'll displace that incumbent.

### Phase 5: Check Disclosure and Legal Red Flags

This is the step most analyses skip — and it's where the biggest findings often are.

1. **BBB profile.** Search `"[company name] BBB"` and read the full profile. Look for: active investigations, advertising substantiation requests, complaint patterns, ownership/investment program failures.
2. **Regulatory actions.** Search for SEC actions, FDA/health violations, state AG actions, lawsuit history.
3. **Website vs. deck consistency.** Does the company's public website show the same kiosk/location/customer counts as the deck? Discrepancies are a major red flag.
4. **Previous investment programs.** Has the company previously sold units, franchises, or passive ownership stakes to investors? Did those programs succeed or fail? Were refunds issued?
5. **Partner logo verification.** If the deck shows logos of major companies (Amazon, Home Depot, etc.), are these signed contracts or aspirational pipeline? Search for press releases or partnerships confirming each.
6. **Team claim verification.** Search for the founder's prior companies and exits. Can you independently verify revenue/scale claims?

### Phase 6: Size the Capital Gap

1. **Map the growth plan.** Extract unit counts and revenue projections for each year.
2. **Compute implied capex.** (Net new units × per-unit cost) for each year.
3. **Sum cumulative capex** over the projection period.
4. **Compare to the raise.** The unfunded gap = cumulative capex - amount raised. This gap often excludes working capital, inventory, S&M — note that the real gap is larger.
5. **Benchmark against the closest analog.** How much did the analog raise to reach a comparable scale? Is this company proposing to match that on a fraction of the capital?

### Phase 7: Produce the Verdict

Synthesize all findings into a structured report. The verdict is **PASS**, **CONDITIONAL**, or **INVEST** — not BUY/HOLD/SELL.

---

## Output Format

```markdown
# [Company Name] Investment Analysis — Complete Due Diligence Report

**Company:** [name] ([location])
**Round:** [amount] raise (terms: [disclosed/undisclosed])
**Deck Date:** [date]
**Analyst:** Hermes Agent for [user]
**Date:** [today]

---

## 1. Executive Summary & Recommendation

### VERDICT: [PASS / CONDITIONAL / INVEST]

[Company] is [1-sentence description of what they really are]. [2-3 sentences on the core finding — the single most important reason for the verdict.]

**Key issues:**
- [Bullet list of the 5-8 most material findings, ranked by severity]

---

## 2. [Major Red Flag Section — if found]

[If BBB investigation, failed prior programs, legal issues, or disclosure problems were found, dedicate a full section. This is often the most valuable part of the analysis.]

---

## 3. Company Overview

[What they do, location, founder, business evolution/pivots, current stage]

---

## 4. Market Size Analysis — Deck vs. Reality

[Table comparing deck claims to independent research. End with the true served market and what the company's own market share goal implies in revenue.]

---

## 5. Unit Economics

[Deck's "model unit" vs. actual fleet. Stress test table across volumes. Break-even point. Gap analysis.]

---

## 6. Capital Gap

[Growth plan table. Cumulative capex vs. raise. Unfunded gap. Benchmark against closest analog.]

---

## 7. Competitive Landscape

[Direct competitors, emerging competitors, incumbent threats, category graveyard. Verify "unique" claims.]

---

## 8. Team Assessment

[Strengths and weaknesses. Verify prior exit/scale claims independently.]

---

## 9. Risk Matrix (Ranked)

[Table: # / Risk / Severity (HIGH/MED/LOW) / Detail]

---

## 10. If You Invest Anyway (Angel Guidance)

[If not a clean PASS — what conditions and terms to insist on: disclosure, verified unit economics, milestone-gated tranches, financing bridge, pro-rata rights, position sizing]

---

## 11. Bottom Line

[2-3 paragraph synthesis. Clear verdict. What would need to change to revisit.]

---

## Sources

[Numbered list of all sources with URLs and what each contributed]
```

Save the report as a markdown file alongside the input documents.

---

## Common Pitfalls

1. **Taking deck claims at face value.** Every quantitative claim (market size, revenue, kiosk count, "unique" differentiator) must be independently verified. Decks are marketing documents, not audited financials.

2. **Missing the BBB/legal check.** This is the highest-signal step and the easiest to skip. A BBB investigation or failed prior investment program can change the entire verdict. Always search `"[company name] BBB"` and `"[company name] lawsuit|SEC|complaint"`.

3. **Confusing the headline market with the served market.** A company claiming a $254B QSR TAM for a kiosk business is not competing in QSR. Find the specific sub-market (e.g., $5.5B hot-food vending) and size against that.

4. **Not stress-testing unit economics.** The "model unit" in a deck is always the best case. Compute the actual fleet's implied per-unit revenue (total revenue ÷ total units) and compare. A 3-6x gap is common and is the single most important number in the analysis.

5. **Ignoring the capital gap.** Decks show 3-5 year projections but only raise enough for year 1. Compute cumulative capex for the full plan and compare to the raise. A 50x gap between capital raised and capital needed is not unusual — but it means this round's investors face massive dilution risk.

6. **Forgetting the category graveyard.** Every hot category has failed companies. Find them. How much did they burn? Why did they fail? This establishes the base rate and tempers optimism. ~90% failure rates are common in frontier tech categories.

7. **Accepting "unique" claims without verification.** "We're the only company that does X" is a standard deck claim. Search specifically for whether the closest competitor already does X. If they do, the deck's marquee differentiator is false.

8. **No terms disclosed.** If the deck doesn't include valuation, security type, or cap table, you cannot price a return. This alone can justify a PASS regardless of business quality.

9. **Not verifying team claims.** "Built a company from $250K to $6M in 24 months" sounds impressive. Search for the company name, the founder's LinkedIn, press coverage. If you can't find independent confirmation, flag it as unverified.

10. **Ambiguous partner logos.** Major company logos on a deck slide can mean signed contracts, LOIs, pipeline aspirations, or "we talked to them once." Always verify which. If they're aspirational presented as signed, that's a disclosure red flag.

---

## Verification Checklist

- [ ] All materials extracted and read fully (deck, memo, model)
- [ ] Every market size claim verified against 2+ independent sources
- [ ] True served market identified (not the headline TAM)
- [ ] Unit economics stress-tested across volume scenarios
- [ ] Actual fleet performance computed from reported totals
- [ ] Capital gap sized (cumulative capex vs. raise)
- [ ] Closest analog researched (capital raised, scale, revenue/unit)
- [ ] Category graveyard identified (failed companies, burn amounts, failure reasons)
- [ ] Incumbent threats assessed (who owns the distribution channel?)
- [ ] "Unique" claims verified or debunked
- [ ] BBB profile checked
- [ ] Legal/regulatory history searched
- [ ] Website vs. deck consistency checked (kiosk/location/customer counts)
- [ ] Partner logos verified (signed vs. pipeline)
- [ ] Team claims independently verified where possible
- [ ] Risk matrix produced (ranked by severity)
- [ ] Verdict is clear (PASS/CONDITIONAL/INVEST)
- [ ] If not PASS: diligence checklist and terms to insist on included
- [ ] Report saved as markdown file alongside input documents

---

## References

- `references/diligence-sources-and-techniques.md` — specific data sources, search patterns, and verification techniques used in private company due diligence (BBB lookup, market size verification sources, unit economics stress test formula, capital gap calculation, category graveyard research)
