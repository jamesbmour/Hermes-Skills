---
name: sector-rotation
description: "Use when the user wants to analyze sector rotation — which sectors are leading/lagging, relative strength rankings, sector ETF performance, fund flows, momentum shifts, or defensive-vs-cyclical rotation signals. Triggered by 'sector rotation analysis', 'which sectors are leading', 'sector performance heatmap', 'is money rotating out of tech', 'sector ETF flows', 'defensive vs cyclical', 'sector momentum ranking', or any request about sector-level market dynamics."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sector-rotation, sector-analysis, ETF-flows, relative-strength, market-breadth, macro]
    related_skills: [sp500, deepstock, macro-dashboard, technical-scanner]
---

# Sector Rotation

## Overview

Track and analyze rotation between the 11 S&P 500 sectors using ETF performance, relative strength, fund flows, and momentum signals. Identify which sectors institutions are moving into and out of — actionable intelligence for positioning and risk management.

## When to Use

- "which sectors are leading right now"
- "sector performance heatmap"
- "is money rotating out of tech into financials"
- "defensive vs cyclical — who's winning"
- "sector ETF fund flows this week"
- "sector momentum rankings"
- "which sectors are oversold"
- "rotation signals for this quarter"
- "compare XLF vs XLK performance"

**Don't use for:** individual stock picks (use `deepstock`), market-wide scans (use `sp500`), or macroeconomic indicator analysis (use `macro-dashboard`).

---

## The 11 Sector ETFs

| Sector | ETF | Description |
|--------|-----|-------------|
| Technology | **XLK** | Software, hardware, semis, IT services |
| Financials | **XLF** | Banks, insurance, capital markets |
| Health Care | **XLV** | Pharma, biotech, medical devices, insurers |
| Consumer Discretionary | **XLY** | Retail, autos, hotels, restaurants |
| Communication Services | **XLC** | Meta, Google, Netflix, telecom |
| Industrials | **XLI** | Aerospace, defense, machinery, transports |
| Consumer Staples | **XLP** | Food, beverage, household products |
| Energy | **XLE** | Oil & gas, equipment, services |
| Utilities | **XLU** | Electric, gas, water utilities |
| Real Estate | **XLRE** | REITs, real estate services |
| Materials | **XLB** | Chemicals, metals, mining, packaging |

Also track: **SPY** (S&P 500 benchmark), **QQQ** (Nasdaq-100, tech-heavy growth proxy), **IWM** (Russell 2000 small caps), **DIA** (Dow Industrials).

---

## Research Process

### Step 1: Pull Performance Data

Pull YTD, 1-month, 1-week, and today's performance for all 11 sector ETFs + SPY/QQQ/IWM.

```bash
# Yahoo Finance batch quote (single request, all tickers)
curl -s "https://query1.finance.yahoo.com/v7/finance/quote?symbols=XLK,XLF,XLV,XLY,XLC,XLI,XLP,XLE,XLU,XLRE,XLB,SPY,QQQ,IWM,DIA" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['quoteResponse']['result']:
    sym = r['symbol']
    price = r.get('regularMarketPrice', 'N/A')
    change = r.get('regularMarketChangePercent', 0)
    ytd = r.get('fiftyTwoWeekHighChangePercent', 'N/A')  # approximate
    print(f'{sym}|{price}|{change}')
"
```

For accurate YTD and multi-period returns, pull chart data:

```bash
for etf in XLK XLF XLV XLY XLC XLI XLP XLE XLU XLRE XLB SPY QQQ IWM; do
  curl -s "https://query1.finance.yahoo.com/v8/finance/chart/$etf?range=ytd&interval=1d" \
    -H "User-Agent: Mozilla/5.0" -o /tmp/sector_${etf}.json &
done
wait
```

### Step 2: Calculate Relative Strength

For each sector vs SPY:
- **RS Ratio** = sector ETF price / SPY price (normalized to 100 at start of period)
- Rising RS = sector outperforming (accumulate)
- Falling RS = sector underperforming (avoid or short)
- Flat RS = sector performing in line

Compute RS across 1-month and 3-month periods to identify trend direction.

### Step 3: Momentum Rankings

Rank sectors by:
- **1-month return** (short-term momentum)
- **3-month return** (intermediate trend)
- **RS vs SPY trajectory** (slope over 3 months)

Score each sector: +2 for top quartile, +1 for second, -1 for third, -2 for bottom. Sum scores for a composite momentum rank.

### Step 4: Analyze Fund Flows (if data available)

Search for recent sector ETF flow data:
- "sector ETF fund flows this week"
- "XLK inflows outflows June 2026"
- "ETF fund flow report sector"

Look for: largest weekly inflows/outflows, sustained flow trends (3+ weeks), divergence between flows and price.

### Step 5: Classify Rotation Regime

| Regime | Signals | Positioning |
|--------|---------|-------------|
| **Risk-On / Cyclical** | XLK, XLY, XLI, XLF leading. Defensives (XLP, XLU) lagging. Small caps (IWM) outperforming. | Overweight cyclical, growth, small caps |
| **Risk-Off / Defensive** | XLP, XLU, XLV leading. Cyclicals (XLY, XLI, XLE) lagging. Bonds rallying. | Overweight defensives, quality, large caps |
| **Rotation in Progress** | Last month's leaders underperforming this week. Multiple sectors changing rank by 3+ positions. | Reduce position sizes, wait for clarity |
| **Broad Rally** | All sectors positive, SPY at highs, low dispersion | Ride the trend, equal weight |
| **Broad Selloff** | All sectors negative, SPY breaking support, high correlation | Cash / hedges / defensives only |

---

## Output Format

```markdown
# 🔄 Sector Rotation Dashboard

**Date:** {TODAY'S DATE} | **SPY:** ${X} ({+X.X%} YTD) | **QQQ:** ${X} | **IWM:** ${X}

---

## 📊 Performance Heatmap

| Sector | ETF | Today | 1-Week | 1-Month | 3-Month | YTD | RS vs SPY |
|--------|-----|-------|--------|---------|---------|-----|-----------|
| Tech | XLK | +X.X% | +X.X% | +X.X% | +X.X% | +X.X% | 📈 Rising |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

## 🏆 Momentum Rankings

| Rank | Sector | ETF | Momentum Score | 1-Mo Return | RS Trend | Signal |
|------|--------|-----|---------------|-------------|----------|--------|
| 1 | {Sector} | {ETF} | +6 | +X.X% | 📈 | **Accumulate** |
| 2 | {Sector} | {ETF} | +4 | +X.X% | 📈 | Overweight |
| ... | ... | ... | ... | ... | ... | ... |
| 11 | {Sector} | {ETF} | -6 | -X.X% | 📉 | Avoid |

---

## 💰 Fund Flows (This Week)

| Sector | ETF | Net Flow | % of AUM | Trend (4-wk) | Signal |
|--------|-----|----------|----------|-------------|--------|
| ... | ... | +$X.XB | +X.X% | Inflows ↑ | Accumulation |
| ... | ... | -$X.XB | -X.X% | Outflows ↓ | Distribution |

---

## 🔀 Rotation Analysis

**Current Regime:** {Risk-On / Risk-Off / Rotation in Progress / Broad Rally / Selloff}

**What's happening:** {2-3 paragraphs describing the current rotation dynamics — what's leading, what's lagging, what's turning, what it means}

**Divergences to watch:**
- {Any sector where price direction diverges from fund flows}
- {Any sector showing relative strength despite bad absolute performance}

---

## 🎯 Actionable Takeaways

1. **Overweight:** {2-3 sectors with strongest momentum + flow confirmation}
2. **Underweight / Avoid:** {2-3 sectors with weakest momentum + outflows}
3. **Watch for reversal:** {1-2 sectors where momentum is peaking or troughing — potential rotation candidate}
4. **Hedge:** {Pair trade ideas — e.g., long XLF / short XLK if rotation is confirmed}
```

---

## Important Instructions

1. **Real ETF data only.** Pull prices from Yahoo Finance or similar. Never fabricate returns.
2. **Momentum ≠ value.** A sector can be expensive and still have strong momentum. This skill measures momentum, not valuation. Flag both.
3. **Flow data is supplementary.** ETF flow data isn't always available. If you can't find it, skip that section rather than guessing.
4. **Correlation context.** Note when all sectors are moving together (high correlation = macro-driven) vs diverging (low correlation = alpha opportunity).
5. **Size matters.** XLK and XLY are heavily concentrated (top 3 holdings dominate). Note concentration risk when recommending these sectors.
6. **Be decisive but humble.** Recommend positions based on data, but acknowledge that sector rotation signals can reverse quickly.

## Common Pitfalls

1. **Chasing last month's leader.** If a sector is #1 in 1-month return but #9 in 1-week, it's already rolling over. Look at the trajectory, not just the rank.
2. **Ignoring macro overlay.** Sector rotation signals are weaker during macro-driven moves (Fed events, election uncertainty). Note the macro context.
3. **Equal-weighting all signals.** Fund flows > RS trend > absolute returns. Money doesn't lie — flows are the strongest signal.
4. **Not checking underlying holdings.** XLK is 40% Apple + Microsoft. A "tech rotation" signal might just be AAPL+MSFT moving. Check concentration.
5. **Over-trading on weekly data.** Sector trends take months to play out. Weekly rebalancing based on this data is too frequent.

## Verification Checklist

- [ ] All 11 sector ETFs + SPY/QQQ/IWM/DIA data pulled from real source
- [ ] Performance calculated for all time periods (today, 1wk, 1mo, 3mo, YTD)
- [ ] RS vs SPY calculated and trend direction noted
- [ ] Momentum scores computed and sectors ranked
- [ ] Fund flow data included if available (not fabricated if missing)
- [ ] Rotation regime classified with supporting evidence
- [ ] Actionable takeaways are specific (which sectors + why)
- [ ] Concentration risk flagged for top-heavy sector ETFs
- [ ] Macro context noted (Fed, earnings season, geopolitical events)