---
name: technical-scanner
description: "Use when the user wants to screen stocks by technical criteria — golden/death crosses, RSI extremes, moving average breakouts, volume spikes, 52-week highs/lows, Bollinger squeezes, or trend reversals. Triggered by 'scan for golden crosses', 'find oversold stocks', 'screen for breakouts', 'stocks above 200-day MA', 'volume spike scanner', 'technical screener S&P 500', or any request to find stocks matching a technical pattern."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [technical-analysis, screener, scanner, breakout, RSI, moving-average, volume, chart-patterns]
    related_skills: [deepstock, sp500, sector-rotation]
---

# Technical Scanner

## Overview

Screen for stocks matching specific technical patterns and criteria. Uses web-based screeners (Finviz, Yahoo Finance) and direct data pulls to find actionable technical setups across any universe — S&P 500, Nasdaq 100, a specific sector, or a user-provided watchlist.

## When to Use

- "scan for golden crosses this week"
- "find oversold S&P 500 stocks"
- "screen for stocks breaking out above resistance"
- "show me stocks with volume 2x above average"
- "new 52-week highs in the Nasdaq"
- "scan for Bollinger band squeezes"
- "find stocks down 5%+ today with high volume"
- "RSI below 30 in the Dow"

**Don't use for:** deep fundamental analysis (use `deepstock`), market-wide briefings (use `sp500`), or single-stock technical analysis (the model can do that inline).

---

## Available Screeners

### 1. Moving Average Crossovers

**Golden Cross** (50-day MA crosses above 200-day MA):
```bash
# Finviz screener URL
curl -s "https://finviz.com/screener.ashx?v=111&f=ta_pattern_goldencross" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import sys, re
html = sys.stdin.read()
# Extract ticker rows from the screener table
tickers = re.findall(r'screener-body-table-nw.*?>(\w+)<', html, re.DOTALL)
# Fallback: parse the ticker column
if not tickers:
    tickers = re.findall(r'<a href=\"quote\.ashx\?t=(\w+)\"', html)
print('\n'.join(tickers[:50]))
"
```

**Death Cross** (50-day MA crosses below 200-day MA): change filter to `ta_pattern_deathcross`.

**Price above/below moving averages:**
- Above 20-day: `ta_sma20_pa` | Below: `ta_sma20_pb`
- Above 50-day: `ta_sma50_pa` | Below: `ta_sma50_pb`
- Above 200-day: `ta_sma200_pa` | Below: `ta_sma200_pb`

### 2. RSI Extremes

- Oversold (RSI < 30): `ta_rsi_os30`
- Overbought (RSI > 70): `ta_rsi_ob70`
- Oversold (RSI < 40): `ta_rsi_os40`
- Overbought (RSI > 60): `ta_rsi_ob60`

### 3. Volume Signals

- Volume 2x+ above average: `sh_rel_vol_o2`
- Volume 5x+ above average: `sh_rel_vol_o5`
- Volume 10x+ above average: `sh_rel_vol_o10`
- Unusually high volume (top 5% of average range): use `sh_avgvol` + `sh_rel_vol` combo

### 4. Price Action

- New 52-week high: `ta_highlow52w_nh`
- New 52-week low: `ta_highlow52w_nl`
- Gap up today: `ta_gap_u`
- Gap down today: `ta_gap_d`
- 5%+ gain today: `sh_price_o5`
- 10%+ gain today: `sh_price_o10`
- 5%+ loss today: `sh_price_u5`
- 10%+ loss today: `sh_price_u10`

### 5. Bollinger Bands

- Price near lower band (potential bounce): `ta_bband20_sb`
- Price near upper band (potential pullback): `ta_bband20_sa`
- Narrow bands (squeeze — low ATR or tight Bollinger width): combine `ta_bband20` with low ATR filter

### 6. Trend & Momentum

- Bullish trend (price above 20, 50, and 200 SMA): combine `ta_sma20_pa,ta_sma50_pa,ta_sma200_pa`
- Bearish trend: `ta_sma20_pb,ta_sma50_pb,ta_sma200_pb`
- Strong momentum (ADX > 25): filter `ta_adx` with adx value

### 7. Custom Combination Screens

Combine filters with commas in the URL. Finviz supports AND logic across filters.

**Example — Oversold + High Volume + Above 200 MA:**
```
f=ta_rsi_os30,sh_rel_vol_o2,ta_sma200_pa
```

**Full URL pattern:**
```
https://finviz.com/screener.ashx?v=111&f={FILTERS}&ft=4&o=-change
```

Where `ft=4` limits to S&P 500, `ft=3` for Nasdaq 100. Omit for all stocks.

---

## Output Format

```markdown
## 🔍 Technical Scan: {PATTERN DESCRIPTION}

**Scan:** {what was screened for}
**Universe:** {S&P 500 / Nasdaq 100 / All US / specific sector}
**Results:** {N} stocks found
**Time:** {timestamp}

| Ticker | Price | Change % | Volume (vs avg) | RSI | 20MA | 50MA | 200MA | Notes |
|--------|-------|----------|-----------------|-----|------|------|-------|-------|
| AAPL   | $X    | +X.X%    | 1.5x            | 45  | $X   | $X   | $X    | {specifics} |

**Quick Takes:**
- **Most compelling:** {2-3 tickers with the strongest signals}
- **Watch out for:** {any that look like traps — low float, earnings soon, etc.}
```

---

## Important Instructions

1. **Use Finviz as primary screener.** It's free, fast, and covers the full US market. The URL-based screener works without JavaScript.
2. **Enrich with Yahoo Finance.** After getting tickers from Finviz, pull additional data (precise RSI, exact MA values, float, short interest) from Yahoo Finance to validate.
3. **Filter by liquidity.** Unless the user asks otherwise, only show stocks with average volume above 500K and price above $5. Low-liquidity stocks produce false signals.
4. **Flag earnings.** Check if any scanned stocks have earnings in the next 5 days. Technical signals are unreliable around earnings — flag them.
5. **Context matters.** A golden cross on a $500B mega-cap is more significant than on a $500M micro-cap. Note market cap tier.
6. **Real data only.** Run the screener URL, extract tickers, pull prices from Yahoo Finance. Never fabricate technical values.
7. **Present clearly.** The user wants actionable scan results, not raw JSON. Clean table + quick takes.

## Common Pitfalls

1. **Finviz rate limiting.** If you get blocked, wait 30 seconds and retry with a different User-Agent.
2. **Stale screener data.** Finviz data can be 5-15 minutes delayed. Always note this.
3. **Too many results.** If a scan returns 200+ tickers, add a market cap or volume filter to narrow it down. Present top 25.
4. **False signals without confirmation.** A single RSI reading isn't enough — combine with volume and trend for stronger signals.
5. **Ignoring the macro context.** A golden cross during a bear market is less reliable than during a bull market. Add a one-line macro note.

## Verification Checklist

- [ ] Screener URL correctly constructed with intended filters
- [ ] Tickers extracted and validated (not empty, not garbage)
- [ ] Yahoo Finance data pulled to enrich and verify
- [ ] Results filtered for liquidity (vol > 500K, price > $5) unless user overrides
- [ ] Earnings flagged for stocks reporting within 5 days
- [ ] Market cap tier noted (mega/large/mid/small/micro)
- [ ] Top 25 results in clean table format
- [ ] Quick takes highlight the 2-3 most actionable setups
- [ ] Data timestamp included