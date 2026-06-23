---
name: macro-dashboard
description: "Use when the user wants a snapshot of key macroeconomic indicators — Fed policy, interest rates, inflation, employment, GDP, yield curve, volatility, PMI, consumer confidence, or commodity prices. Triggered by 'macro snapshot', 'macro dashboard', 'economic indicators today', 'what's the Fed doing', 'inflation check', 'yield curve status', 'jobs report', 'CPI data', 'fed funds rate', 'economic calendar this week', or any request about macro conditions affecting markets."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [macro, economics, fed, inflation, interest-rates, yield-curve, GDP, employment]
    related_skills: [sp500, sector-rotation, deepstock]
---

# Macro Dashboard

## Overview

Pull and present key macroeconomic indicators that drive market conditions. The macro environment is the tide that lifts or sinks all boats — before analyzing individual stocks, understand the regime. This skill gathers data from FRED (Federal Reserve Economic Data), BLS (Bureau of Labor Statistics), BEA (Bureau of Economic Analysis), CME FedWatch, and market pricing.

## When to Use

- "macro snapshot"
- "economic dashboard"
- "what's the macro picture right now"
- "inflation check — latest CPI and PCE"
- "what's the Fed likely to do next"
- "yield curve status — is it still inverted"
- "jobs market health check"
- "economic calendar this week"
- "GDP growth tracker"
- "macro regime — expansion, slowdown, or recession?"

**Don't use for:** individual stock analysis (use `deepstock`), sector rotation (use `sector-rotation`), or market-wide scans (use `sp500`). Macro is the backdrop, not the trade signal.

---

## Key Indicators

### 1. Federal Reserve Policy (Highest Weight)

**Fed Funds Rate:**
- Current target range
- Last change (date, direction, magnitude)
- Next FOMC meeting date
- Market-implied probability of next move (CME FedWatch)

```bash
# CME FedWatch Tool — market-implied rate probabilities
# Search for latest data since the API requires authentication
curl -s "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
# Extract probability data from embedded JSON or table
# Look for probabilities of rate hold/cut/hike
"
```

**Dot Plot (from most recent SEP):**
- Median FOMC member projection for year-end rate
- Distribution: hawks vs doves
- Implied number of cuts/hikes for the year

### 2. Inflation

**CPI (Consumer Price Index):**
- MoM and YoY (headline and core)
- Trend: last 3 prints (accelerating/decelerating/stable)
- Key drivers: shelter, energy, services vs goods

**PCE (Personal Consumption Expenditures):**
- The Fed's preferred inflation gauge
- MoM and YoY (headline and core)
- Distance from 2% target

**Where to get it:** BLS.gov for CPI, BEA.gov for PCE. Search for "CPI June 2026" or "PCE price index latest".

### 3. Employment

**Key metrics:**
- Nonfarm payrolls (monthly change)
- Unemployment rate (U-3)
- Labor force participation rate
- Average hourly earnings (YoY — wage inflation)
- Initial jobless claims (weekly — leading indicator)
- JOLTS job openings (monthly — labor demand)

**Where to get it:** BLS.gov Employment Situation Summary. Search for "jobs report June 2026" or "nonfarm payrolls latest".

### 4. GDP Growth

**Key metrics:**
- GDPNow (Atlanta Fed real-time GDP estimate) — most current
- Actual GDP (quarterly, BEA)
- GDP composition: consumption, investment, government, net exports

```bash
# Atlanta Fed GDPNow
curl -s "https://www.atlantafed.org/cqer/research/gdpnow" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
# Extract the latest GDPNow estimate
match = re.search(r'GDPNow.*?(\\d+\\.\\d+)', html)
if match:
    print(f'GDPNow estimate: {match.group(1)}%')
"
```

### 5. Yield Curve & Interest Rates

**Key rates (from Treasury.gov or Yahoo Finance):**

```bash
# Pull treasury yields from Yahoo Finance
curl -s "https://query1.finance.yahoo.com/v7/finance/quote?symbols=^TNX,^FVX,^TYX,^IRX" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['quoteResponse']['result']:
    sym = r['symbol']
    price = r.get('regularMarketPrice', 'N/A')
    label = {'^IRX': '3-Month', '^FVX': '5-Year', '^TNX': '10-Year', '^TYX': '30-Year'}
    print(f'{label.get(sym, sym)}: {price}%')
"
```

**Yield Curve Spreads:**
- 2s10s spread (2-year minus 10-year): most watched recession signal
- 3m10y spread (3-month minus 10-year): Fed's preferred curve measure
- Status: Normal (positive) / Flat (near zero) / Inverted (negative)
- If inverted: for how long? Is it steepening or deepening?

**Real rates:** TIPS yields, breakeven inflation rates.

### 6. Market Volatility

**VIX (CBOE Volatility Index):**
```bash
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=1mo&interval=1d" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
data = json.load(sys.stdin)
quotes = data['chart']['result'][0]['indicators']['quote'][0]
closes = [c for c in quotes['close'] if c is not None]
print(f'VIX: {closes[-1]:.2f}')
print(f'1-Month Range: {min(closes):.2f} - {max(closes):.2f}')
"
```

**VIX Regime:**
- < 12: Extreme complacency
- 12–18: Low volatility (bull market normal)
- 18–25: Moderate concern
- 25–35: High fear
- > 35: Extreme fear / crisis

### 7. Leading Indicators

**PMI (Purchasing Managers Index):**
- Manufacturing PMI (ISM)
- Services PMI (ISM)
- Above 50 = expansion, below 50 = contraction

**Consumer Sentiment:**
- University of Michigan Consumer Sentiment Index
- Conference Board Consumer Confidence

**Housing:**
- Building permits, housing starts, existing home sales
- 30-year mortgage rate

### 8. Commodities & Currency

- **Crude oil** (WTI): energy costs flow into everything
- **Gold**: fear gauge + inflation hedge
- **Copper**: "Dr. Copper" — industrial demand proxy
- **DXY (US Dollar Index)**: strong dollar = headwind for multinationals, commodities, EM
- **Bitcoin**: risk appetite proxy

```bash
# Batch pull key commodities + DXY
curl -s "https://query1.finance.yahoo.com/v7/finance/quote?symbols=CL=F,GC=F,HG=F,DX-Y.NYB,BTC-USD" \
  -H "User-Agent: Mozilla/5.0"
```

### 9. This Week's Economic Calendar

Search for "economic calendar this week" to list upcoming data releases:
- Day, time, indicator, consensus estimate, prior reading
- Flag high-impact events (FOMC, CPI, NFP, GDP)

---

## Output Format

```markdown
# 🌐 Macro Dashboard

**Date:** {TODAY'S DATE} | **Regime:** {Expansion / Slowdown / Recession / Recovery}

---

## 🏦 Federal Reserve

| Indicator | Current | Signal |
|-----------|---------|--------|
| Fed Funds Rate | {X.XX%}–{Y.YY%} | — |
| Last Move | {+/- XX bps} on {date} | — |
| Next Meeting | {date} | — |
| Market-Implied: Hold | {X%} | — |
| Market-Implied: Cut | {X%} | — |
| Market-Implied: Hike | {X%} | — |
| Dot Plot (Year-End) | {X.XX%} | {X} cuts implied |

**FOMC Outlook:** {1-2 sentences on what the market is pricing and what would change it}

---

## 📈 Growth & Inflation

| Indicator | Latest | Prior | Trend | Status |
|-----------|--------|-------|-------|--------|
| GDP (QoQ Annualized) | {X.X%} | {Y.Y%} | {accel/decel} | {hot/ok/weak} |
| GDPNow (Current Q) | {X.X%} | — | — | {tracking} |
| CPI (YoY) | {X.X%} | {Y.Y%} | {↑/↓/→} | {hot/ok/cool} |
| Core CPI (YoY) | {X.X%} | {Y.Y%} | {↑/↓/→} | {hot/ok/cool} |
| PCE (YoY) | {X.X%} | {Y.Y%} | {↑/↓/→} | {distance from 2%} |
| Core PCE (YoY) | {X.X%} | {Y.Y%} | {↑/↓/→} | {distance from 2%} |

---

## 👷 Employment

| Indicator | Latest | Prior | Trend | Status |
|-----------|--------|-------|-------|--------|
| Nonfarm Payrolls | +{X}K | +{Y}K | {↑/↓/→} | {hot/ok/weak} |
| Unemployment Rate | {X.X%} | {Y.Y%} | {↑/↓/→} | {low/ok/high} |
| Labor Force Participation | {X.X%} | {Y.Y%} | {↑/↓/→} | — |
| Avg Hourly Earnings (YoY) | {X.X%} | {Y.Y%} | {↑/↓/→} | {wage pressure?} |
| Initial Claims (Weekly) | {X}K | {Y}K | {↑/↓/→} | {low/ok/elevated} |

---

## 📉 Yield Curve

| Maturity | Yield | 1-Mo Ago | Change |
|----------|-------|----------|--------|
| 3-Month | {X.XX%} | {Y.YY%} | {+/-X} bps |
| 2-Year | {X.XX%} | {Y.YY%} | {+/-X} bps |
| 10-Year | {X.XX%} | {Y.YY%} | {+/-X} bps |
| 30-Year | {X.XX%} | {Y.YY%} | {+/-X} bps |

**Key Spreads:**
| Spread | Current | Status | Recession Signal? |
|--------|---------|--------|------------------|
| 2s10s | {+/-X} bps | {Normal/Flat/Inverted} | {Yes (X months) / No} |
| 3m10y | {+/-X} bps | {Normal/Flat/Inverted} | {Yes / No} |

---

## ⚡ Market Stress & Leading Indicators

| Indicator | Current | Regime |
|-----------|---------|--------|
| VIX | {X.XX} | {Complacency / Low / Moderate / Fear / Extreme} |
| Manufacturing PMI | {X.X} | {Expanding/Contracting} |
| Services PMI | {X.X} | {Expanding/Contracting} |
| Consumer Sentiment (UMich) | {X.X} | {Optimistic/Neutral/Pessimistic} |
| Mortgage Rate (30yr) | {X.XX%} | — |

---

## 🛢 Commodities & Currency

| Asset | Price | 1-Mo Change | Signal |
|-------|-------|------------|--------|
| Crude Oil (WTI) | ${X.XX} | {+/-X%} | {inflation pressure?} |
| Gold | ${X} | {+/-X%} | {risk appetite?} |
| Copper | ${X.XX} | {+/-X%} | {industrial demand?} |
| DXY (USD) | {X.XX} | {+/-X%} | {headwind/tailwind?} |
| Bitcoin | ${X} | {+/-X%} | {risk appetite?} |

---

## 📅 This Week's Calendar

| Day | Time | Event | Consensus | Prior | Impact |
|-----|------|-------|-----------|-------|--------|
| {Mon} | {time} | {indicator} | {X.X} | {Y.Y} | ⭐⭐⭐ |
| ... | ... | ... | ... | ... | ... |

---

## 🎯 Regime Assessment

**Current Regime: {label}**

{2-3 paragraphs tying all indicators together into a coherent macro narrative. What's the dominant theme? What regime are we in — Goldilocks, stagflation, soft landing, recession, overheating? What does this mean for equities, bonds, commodities?}

**Implications for positioning:**
- **Equities:** {bullish/neutral/bearish — and which sectors benefit}
- **Bonds:** {duration preference — short/long, credit quality}
- **Commodities:** {inflation hedge? growth play? avoid?}
- **Cash:** {opportunity cost assessment}
- **Key risks to the regime:** {what would change the picture}

---

*Data sourced from FRED, BLS, BEA, CME FedWatch, Yahoo Finance, and Treasury.gov. Indicators are as of most recent release dates. This is informational — not investment advice.*
```

---

## Important Instructions

1. **Prioritize data availability over completeness.** Some indicators update monthly, some quarterly. Show what's current — don't show stale data as if it's fresh. If the last CPI print is from May and it's June, say "May CPI (latest)" not just "CPI."
2. **Use FRED for historical data.** The St. Louis FRED database has a free API. For historical trends, this is the best source.
3. **CME FedWatch for rate probabilities.** This is market-implied, not a forecast. It's what traders are pricing, not what will happen.
4. **BLS/BEA for official releases.** For CPI, NFP, GDP — go to the source. News articles summarizing the release are fine as secondary sources.
5. **Yield curve from Treasury or Yahoo Finance.** ^TNX, ^FVX, ^TYX, ^IRX tickers give live yields.
6. **One-line interpretation for each indicator.** Don't just show numbers — say whether each reading is hot/ok/cold, expanding/contracting, normal/inverted.
7. **Regime assessment ties it together.** This is the most valuable part. Anyone can look up CPI. Synthesizing 15 indicators into "we're in a soft landing with sticky services inflation" is the value-add.

## Common Pitfalls

1. **Mixing real-time and stale data.** The 10-year yield is live. GDP is from last quarter. Clearly label each.
2. **Over-updating.** Don't re-pull everything if the user asks again in 30 minutes. Note when key data is unchanged.
3. **Correlation without causation.** "Gold is up, so inflation fears are rising" — maybe, or maybe the dollar is falling. Give the most likely explanation, not the only one.
4. **Regime overconfidence.** The macro regime is always clearer in hindsight. Present the assessment as "current evidence suggests" not "we are definitely in X."
5. **Missing the calendar.** The economic calendar is critical — it tells the user what to watch for THIS WEEK that could change the picture. Don't skip it.
6. **US-centric by default.** Note this covers US macro. If the user wants global (EU, China, Japan), add those sections.

## Verification Checklist

- [ ] Fed funds rate and next meeting date are current
- [ ] CME FedWatch probabilities pulled from real data
- [ ] CPI and PCE show latest available releases (with dates)
- [ ] Employment data from most recent jobs report
- [ ] GDPNow pulled from Atlanta Fed (or most recent GDP print)
- [ ] All yield curve rates are live/latest market data
- [ ] 2s10s and 3m10y spreads calculated correctly
- [ ] VIX is current
- [ ] Commodities and DXY are current market prices
- [ ] Economic calendar lists this week's events with consensus estimates
- [ ] Regime assessment supported by the data presented
- [ ] Each indicator has a one-line interpretation, not just a number
- [ ] Disclaimer included
