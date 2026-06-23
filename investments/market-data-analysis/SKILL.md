---
name: market-data-analysis
description: Fetch real-time and historical stock market data from Yahoo Finance API, calculate technical indicators (RSI, SMA, momentum, volume ratios), and compile professional equity research briefings with buy/sell recommendations. Use for any financial market analysis, stock screening, or investment reporting task.
tags:
  - finance
  - equities
  - stock-market
  - technical-analysis
  - yahoo-finance
  - briefing
---

# Market Data Analysis & Equity Research Briefing

## When to Use

- Daily/weekly S&P 500 investment briefings
- Stock screening with technical indicators
- Sector rotation analysis
- Any task requiring real-time or historical equity market data
- Identifying buy/sell opportunities from quantitative signals

## Overview

This skill fetches market data from Yahoo Finance's free (unauthenticated) chart API, calculates standard technical indicators, and structures the output as a professional equity research briefing. The Yahoo Finance API requires no API key — only a User-Agent header and proper SSL handling.

## Step 1: Fetch Market Data

### Yahoo Finance Chart API

```
GET https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?range={RANGE}&interval={INTERVAL}
```

**Critical requirements:**
- **User-Agent header required**: `Mozilla/5.0` — without it, Yahoo returns empty responses
- **SSL verification must be disabled**: `ssl.create_default_context()` with `check_hostname=False` and `verify_mode=ssl.CERT_NONE`
- **URL-encode symbols** with special characters: `^GSPC` → `%5EGSPC`, use `urllib.parse.quote()`
- **Rate limit**: 0.08s sleep between requests to avoid being throttled
- **Symbol format**: Tickers like `AAPL`; indices like `^GSPC`, `^VIX`, `^DJI`; futures like `GC=F`, `CL=F`; treasury yields like `^TNX`

### Ranges & Intervals
| Range | Description | Typical Interval |
|-------|-------------|-----------------|
| `1d` | Intraday | `1m`, `5m` |
| `5d` | 5-day | `1d` (or `30m`) |
| `1mo` | 1 month | `1d` |
| `3mo` | 3 months | `1d` |
| `6mo` | 6 months | `1d` |
| `1y` | 1 year | `1d` |
| `max` | Full history | `1d` |

### JSON Response Structure

```python
result = data['chart']['result'][0]
meta = result['meta']
# Key meta fields:
#   regularMarketPrice  — current/last price
#   fiftyTwoWeekHigh    — 52-week high
#   fiftyTwoWeekLow     — 52-week low
#   regularMarketVolume — current volume

quotes = result['indicators']['quote'][0]
# Key arrays (aligned by timestamp):
#   quotes['close']  — daily closes (may contain None for market holidays)
#   quotes['high']   — daily highs
#   quotes['low']    — daily lows
#   quotes['volume'] — daily volumes
```

**Pitfall**: Arrays contain `None` values for market holidays and gaps. Always filter: `closes = [c for c in quotes['close'] if c is not None]`

### Macro Indicators to Fetch

| Symbol | What | Yahoo Ticker |
|--------|------|-------------|
| S&P 500 | Broad market | `^GSPC` |
| VIX | Volatility | `^VIX` |
| Nasdaq | Tech-heavy | `^IXIC` |
| Dow | Blue chips | `^DJI` |
| Russell 2000 | Small caps | `^RUT` |
| Gold | Safe haven | `GC=F` |
| Oil (WTI) | Energy | `CL=F` |
| 10Y Treasury | Rates | `^TNX` |
| Dollar Index | FX | `DX-Y.NYB` |
| Bitcoin | Crypto | `BTC-USD` |

### Sector ETFs (11 S&P Sectors)

`XLK` (Tech), `XLV` (Healthcare), `XLF` (Financials), `XLY` (Consumer Disc), `XLP` (Consumer Staples), `XLE` (Energy), `XLI` (Industrials), `XLB` (Materials), `XLU` (Utilities), `XLRE` (Real Estate), `XLC` (Comm Services)

## Step 2: Calculate Technical Indicators

All formulas assume a list of daily closes ordered oldest→newest.

### RSI (14-day)

```python
if len(closes) >= 15:
    gains, losses = [], []
    for i in range(1, 15):
        change = closes[-i] - closes[-i-1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = sum(gains) / 14
    avg_loss = sum(losses) / 14
    rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss > 0 else 100.0
```

**Interpretation**: RSI < 30 = oversold (potential buy), RSI > 70 = overbought (potential sell). RSI < 10 or > 80 = extreme.

### Simple Moving Averages

```python
sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None
```

**Price vs SMA50**: Positive = uptrend, negative = downtrend. Distance from SMA50 measures extension.

### Returns

```python
day_change   = (current / closes[-2] - 1) * 100    if len(closes) >= 2
week_change  = (current / closes[-6] - 1) * 100    if len(closes) >= 6
month_change = (current / closes[-22] - 1) * 100   if len(closes) >= 22
three_month   = (current / closes[-66] - 1) * 100   if len(closes) >= 66
```

### Volume Ratio

```python
vol_recent = sum(volumes[-5:]) / 5    # last 5 days
vol_avg    = sum(volumes[-50:]) / 50  # 50-day average
vol_ratio  = vol_recent / vol_avg     # >1 = above-average volume
```

### Distance from 52-Week Extremes

```python
dist_from_high = (current / high52 - 1) * 100  # negative = below high
dist_from_low  = (current / low52 - 1) * 100   # positive = above low
```

## Step 3: Screen for Buy/Sell Candidates

### Buy Selection Criteria (blend two approaches)

**Momentum Breakouts** (trend following):
- Distance from 52-week high: > −5% (near highs)
- Price above SMA50 (uptrend confirmed)
- RSI 50–70 (strong but not overbought)
- Positive 1-month and 3-month returns
- Sort by 3-month return descending

**Oversold Value Plays** (mean reversion):
- RSI < 35 (oversold)
- Fundamentally sound (dividend yield, buybacks, strong franchise)
- Sector context matters — energy oversold might be value, tech oversold might be a falling knife
- Sort by RSI ascending

### Sell/Short Selection Criteria

**Overbought + Extended** (mean reversion shorts):
- RSI > 72 (overbought)
- Price significantly above SMA50 (> +7%)
- Near 52-week high
- Sort by RSI descending

**Structural Decliners** (trend-following shorts):
- Price below SMA50 (downtrend)
- Near 52-week low (within 10%)
- Negative 1-month and 3-month returns
- In weak sectors (bottom 3-month sector performance)
- Sort by 3-month return ascending

### Selection Methodology
- Pick 5 from each sub-approach for a balanced 10-long / 10-short list
- Cross-reference with sector performance: favor longs in leading sectors, shorts in lagging sectors
- A stock can appear on both lists (e.g., CAT at 52W high with RSI 72) — note as a hedge/inflection point

## Step 4: Briefing Format

```
# S&P 500 Daily Investment Briefing
## Date — Pre-Market

### I. Market Overview
- Index table (S&P, Nasdaq, Dow, Russell, VIX, 10Y, Gold, Oil, Dollar, BTC)
- Sector performance heatmap (1-month, sorted)
- Sentiment assessment

### II. 10 Best Buy Opportunities
- Table: Ticker, Price, RSI, 1M/3M returns, % from 52H, vs SMA50, thesis
- Split: 5 momentum breakouts + 5 oversold value

### III. 10 Best Sell/Short Opportunities
- Table: Ticker, Price, RSI, 1M/3M returns, % from 52L/H, vs SMA50, thesis
- Split: 5 overbought + 5 structural decliners

### IV. Risk Factors & Catalysts
### V. Disclaimer
```

## Pitfalls

1. **Yahoo Finance API returns empty body without User-Agent**: Always set `User-Agent: Mozilla/5.0` header. Empty JSON / `Expecting value` parse error = missing User-Agent or rate-limited.
2. **None values in OHLCV arrays**: Market holidays, trading halts. Filter with list comprehensions before calculations.
3. **Symbol URL-encoding**: `^GSPC` must be encoded as `%5EGSPC`. Use `urllib.parse.quote()`.
4. **RSI calculation variable name typos**: Common bugs include `lossions` instead of `losses`, `len(closes >= 20)` instead of `len(closes) >= 20`. Always test with a known stock first.
5. **Yahoo v10 quoteSummary API appears deprecated**: The `/v10/finance/quoteSummary/{symbol}` endpoint no longer returns fundamentals data. Use only the v8 chart API. For P/E, market cap, and other fundamentals, use a different data source (Alpha Vantage, Financial Modeling Prep, etc.).
6. **Rate limiting**: Yahoo will throttle or return 999 errors if too many requests fire too fast. 0.08s sleep between requests works reliably for 100+ stocks.
7. **Ollama Cloud model names**: Available models can be discovered via `GET https://ollama.com/v1/models` with `Authorization: Bearer {OLLAMA_API_KEY}`. Model IDs include version suffixes (e.g., `deepseek-v4-pro`, not `deepseek-v3.1-pro`).

## Automated Scheduling

To set up a recurring daily briefing via cron job:

```
cronjob action=create
  schedule: "0 7 * * 1-5"   (7:00 AM Mon–Fri)
  model: deepseek-v4-pro via ollama-cloud
  toolsets: [terminal, file, web]
  deliver: origin (or specific channel)
```

The cron prompt must be fully self-contained (no session context). Include the full stock universe, API details, and output format in the prompt itself.

## Reference Files

- `references/yahoo-finance-api.md` — API endpoint details, symbol mappings, response structure, and troubleshooting
- `scripts/fetch_market_data.py` — Reusable script to fetch and analyze S&P 500 stock data
- `references/sp500-stock-universe.md` — Full list of 95+ tickers by sector used for screening