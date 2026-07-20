# Due Diligence Sources & Techniques

Specific data sources, search patterns, and verification techniques for private company investment due diligence. Condensed from the Homechow analysis (July 2026) — proven patterns that surfaced material findings the investment memo missed.

---

## Market Size Verification Sources

When a deck cites a TAM/SAM/SOM, verify against these sources. Cross-reference 2-3 per market.

| Source | Coverage | URL Pattern |
|--------|----------|-------------|
| Future Market Insights | Niche sub-markets (hot-food vending, etc.) | `futuremarketinsights.com/reports/[market]` |
| Mordor Intelligence | Broad markets (QSR, vending, foodservice) | `mordorintelligence.com/industry-reports/[market]` |
| Grand View Research | Broad markets with growth forecasts | `grandviewresearch.com/industry-analysis/[market]` |
| Statista | Aggregated stats from multiple markets | `statista.com/topics/[topic]` |
| IMARC Group | Market sizing with CAGR | `imarcgroup.com/[market]-market` |
| Market Data Forecast | Smart vending, tech markets | `marketdataforecast.com/market-reports/[market]` |
| Renub Research | Regional markets (US QSR, etc.) | `renub.com/[market].php` |
| Custom Market Insights | US-specific markets | `custommarketinsights.com/report/[market]` |

### Search Patterns for Market Verification

Use `parallel_search_web` with 4-5 queries per market:

```
"[market name] market size 2025 2026 US"
"[market name] market growth CAGR forecast"
"true served market [company type] [geography]"
"[adjacent market] vs [claimed market] difference"
"[market name] Future Market Insights OR Mordor OR Grand View"
```

### The "True Served Market" Technique

Decks cite the broadest market they can plausibly name. The actual served market is usually a sub-segment 10-100x smaller.

**Example:** Homechow (hot-food kiosk company) claimed a $254B QSR TAM. The true served market — US/Canada hot-food vending — is ~$5.5B (Future Market Insights). That's a ~50x overstatement.

**Method:**
1. Identify what the company actually sells (not what it "disrupts")
2. Find the market research report for that specific product category
3. Compare the company's own market share goal × true market = honest revenue ceiling
4. If the deck's market is >10x the true served market, flag it as overstated

---

## Unit Economics Stress Test

### The Gap Calculation

```
Deck's "model unit" revenue:    $74,770/yr  (19.4 orders/day × $10.70 AOV × 360 days)
Actual fleet implied revenue:  total_revenue ÷ total_units
Gap ratio:                      model ÷ actual  (e.g., 6x)
```

If the gap is >3x, the entire investment case depends on closing that gap — which the deck asserts but doesn't demonstrate.

### Volume Stress Test Formula

Apply the deck's cost ratios across a range of daily volumes:

```python
aov = 10.70          # from deck
days = 360           # operating days
food_cost_pct = 0.37 # from deck
ops_pct = 0.29       # from deck (includes host revenue share)
ga_pct = 0.07        # from deck
kiosk_cost = 14600   # from use-of-funds
depr_life = 5        # years

for orders_per_day in [19.4, 10, 5, 3, 2]:
    rev = orders_per_day * aov * days
    food = rev * food_cost_pct
    ops = rev * ops_pct
    gross = rev - food - ops
    ga = rev * ga_pct
    depr = kiosk_cost / depr_life
    ebit = gross - ga - depr
    print(f"{orders_per_day}/day: rev=${rev:,.0f}, EBIT=${ebit:,.0f}, margin={ebit/rev:.1%}")
```

**Break-even threshold:** The orders/day where EBIT crosses zero. If the current fleet is below this, the business is losing money on a fully-costed basis.

---

## Capital Gap Calculation

```python
# From the deck's projections
kiosks = [60, 189, 3201, 7149]           # year-end counts
revenue = [700_000, 3_800_000, 142_100_000, 405_000_000]
kiosk_cost = 14_600                        # per unit

net_adds = [kiosks[i] - kiosks[i-1] for i in range(1, len(kiosks))]
capex = [n * kiosk_cost for n in net_adds]
cumulative_capex = sum(capex)
raise_amount = 2_000_000
unfunded_gap = cumulative_capex - raise_amount

# Compare to closest analog
# e.g., Farmer's Fridge raised $82-175M to reach ~1,200 machines
# This company projects 3,201 machines by year 3 on $2M raised
```

**Key check:** cumulative capex ÷ raise amount. If >20x, the growth plan is aspirational, not funded. Note that capex alone understates the real gap — add working capital, inventory, restocking labor, and new-market S&M.

---

## BBB and Legal Red Flag Checks

### BBB Profile Search

```
Search: "[company name] BBB"
URL: bbb.org/us/[state]/[city]/profile/[category]/[company-slug]
```

**What to look for in the BBB profile:**
- **Active correspondence/investigation** — dates of BBB letters and whether the company responded
- **Advertising substantiation requests** — BBB asking the company to prove claims
- **Previous investment programs** — did the company sell units/franchises/ownership to passive investors? Did those programs fail? Were refunds issued?
- **Website vs. reality discrepancies** — BBB often catches inflated location/asset counts that the deck repeats
- **"Sold out" or non-operational units** — signs of stock-out or broken operations

**Example finding:** Homechow's BBB profile revealed they had sold kiosks to 47 passive investors, the program failed due to poor location performance, and investors were converted to equity instead of receiving refunds. This was not in the investment memo and changed the entire analysis.

### Other Legal/Regulatory Searches

```
"[company name] lawsuit OR SEC OR complaint OR action"
"[company name] FDA OR "health department" OR violation"
"[founder name] lawsuit OR fraud OR SEC OR complaint"
"[company name] reviews complaints scam"
```

---

## Website vs. Deck Consistency Check

Decks claim kiosk/location/customer counts that may not match the public website.

1. Navigate to the company's website (locations/finder page)
2. Count the actual listed locations
3. Compare to deck claims
4. If website shows 15-18 but deck claims 60-100+, that's a material discrepancy

Also check:
- Menu/product pages for "sold out" items (indicates stock-out or non-operational units)
- "About" page claims vs. deck claims
- Partner/customer logos on website vs. deck

---

## Category Graveyard Research

Every frontier/automated category has failed companies. Find them to establish the base rate.

```
Search: "[category] startup failed shutdown bankruptcy"
Search: "[category] company burned raised million"
Search: "[specific failed company] why failed lessons"
```

**Documented failure cases to know:**
| Company | Category | Raised | Outcome |
|---------|----------|--------|---------|
| Zume Pizza | Automated food | $428-500M | Shutdown June 2023 |
| Chowbotics | Fresh food robots | ~$15M | Acquired by DoorDash, then shut down |
| Piestro | Automated pizza | ~$20M | Shut down |
| Basil Street | Automated pizza | ~$10M | Shut down |
| Redbox | DVD kiosks | N/A (public) | Liquidated July 2024, ~$1B debt |

**Cautionary precedent pattern:** If the target company's own executive came from a failed company in an adjacent space (e.g., Homechow's SVP BizDev from Redbox), note it — kiosk networks can reach massive scale and still fail on unit economics.

---

## Closest Analog Research

Find the company that does the same thing at larger scale. This is the benchmark for what the business should look like when it works.

```
Search: "[company type] largest company funding raised"
Search: "[category] leader market share revenue"
Search: "[analog company] funding rounds total raised"
```

**Data to extract for the analog:**
- Total capital raised (check Crunchbase, PitchBook, Tracxn, press releases)
- Number of units deployed
- Revenue per unit (if disclosed)
- Timeline to reach current scale
- Whether they are profitable

**Comparison:** If the analog raised $100M to reach 1,200 units, and the target projects 3,200 units on $2M raised, that's a 50:1 capital efficiency gap — not impossible, but extraordinary and requiring explanation.

---

## Partner Logo Verification

Decks often show logos of major companies. Verify whether each is a signed contract, LOI, or aspirational.

```
Search: "[major company] [target company] partnership OR contract OR press release"
Search: "[major company] [target company] deal OR agreement"
```

If you cannot find a press release or announcement confirming the partnership, treat the logo as unverified. If the deck presents aspirational pipeline as signed partners, flag it as a disclosure red flag.

**Incumbent check:** If the deck targets corporate/hospital/education venues, check whether incumbent foodservice operators (Canteen/Compass, Aramark, Sodexo, AVI Foodsystems) already serve those venues. These incumbents can add automated offerings as a feature — they don't need a new business to do it.

---

## Team Claim Verification

```
Search: "[founder name] [previous company] revenue OR exit OR sold"
Search: "[founder name] [previous company] crunchbase OR pitchbook"
Search: "[founder name] linkedin background"
```

If a founder claims "$250K to $6M in 24 months via Walmart/Dick's channels," search for the previous company name + "revenue" or "crunchbase." If no public record exists, flag the claim as unverified in the report. Don't call it false — just unverified.

---

## Useful Parallel Search Patterns

Use `mcp__jina_mcp_server__parallel_search_web` to run 5 searches simultaneously:

```
[
  {"query": "[analog company] revenue funding scale 2024 2025"},
  {"query": "[category] market size 2025 2026 [geography]"},
  {"query": "[failed company 1] [failed company 2] [category] failed shutdown"},
  {"query": "[market type] market size growth CAGR forecast"},
  {"query": "[target company] [founder name] [location] reviews news"}
]
```

This covers the analog, market size, category graveyard, market forecast, and company-specific news in one parallel batch.
