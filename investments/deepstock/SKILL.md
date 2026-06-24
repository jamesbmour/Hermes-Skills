---
name: deepstock
description: "Use when the user asks for deep research on a specific stock ticker (or multiple tickers) — full fundamental, technical, news, filings, and sentiment analysis culminating in a BUY/HOLD/SELL verdict with a concrete trading strategy. Triggered by 'analyze NVDA', 'deep dive on AAPL', 'should I buy TSLA', 'research MSFT and GOOGL', 'tell me everything about META', or similar."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [deep-research, fundamental-analysis, technical-analysis, stock-research, equity-analysis, ticker, trading-strategy]
    related_skills: [sp500, polymarket, sec-edgar]
---

# Deep Stock Research & Trading Verdict

Perform exhaustive research on one or more tickers, then deliver a comprehensive investment thesis with a clear BUY, HOLD, or SELL verdict and an actionable trading strategy.

## When to Use

- User asks for deep analysis of a specific stock: "analyze NVDA", "deep dive MSFT"
- User asks whether to buy/sell/hold: "should I buy AAPL?", "is it time to sell TSLA?"
- User wants everything about a company: "tell me everything about META", "full research on PLTR"
- User wants to compare tickers: "compare GOOGL vs MSFT", "which is better: AMD or NVDA?"
- Single ticker: produce a full report for that ticker
- Multiple tickers: produce a full report for each, then a comparative summary at the end

Do NOT use for: sector-wide scans (use `sp500` skill), simple price quotes, crypto assets (separate domain), or macro-only analysis.

## Research Process

Execute research across these pillars. For each pillar, use web_search and terminal tools to gather real data — never fabricate.

### Pillar 1: Price & Technicals
- Current price, pre-market / after-hours if active
- 52-week range, YTD performance, 1-month and 3-month returns
- Key moving averages (20-day, 50-day, 200-day) and current position relative to them
- RSI (14-day), MACD, Bollinger Bands, volume profile
- Support and resistance levels
- Average true range (ATR) for position sizing
- Beta vs S&P500
- Chart patterns: breakouts, breakdowns, consolidations, trend direction

### Pillar 2: Fundamentals & Filings
- Market cap, enterprise value, P/E (trailing and forward), PEG ratio
- Revenue and EPS growth (YoY, QoQ), revenue and earnings surprises vs estimates
- Profit margins: gross, operating, net — and trend direction
- Return on equity (ROE), return on invested capital (ROIC)
- Debt-to-equity ratio, current ratio, free cash flow yield
- Dividend yield and payout ratio (if applicable)
- Latest 10-K/10-Q highlights: revenue segments, risk factors, management discussion
- Recent 8-K filings: material events, guidance changes, M&A, executive changes
- Key numbers from the most recent earnings call

### Pillar 3: News & Sentiment
- Major news catalysts from the last 30 days (product launches, partnerships, lawsuits, regulatory actions)
- Current dominant narrative: what is the market saying about this stock right now?
- Social sentiment indicators (Reddit/Stocktwits mentions, X/Twitter volume if accessible)
- Upcoming catalysts: earnings date, product events, FDA dates, contract decisions
- Macro factors affecting the sector

### Pillar 4: Wall Street & Insider Activity
- Analyst consensus: number of buys/holds/sells, mean price target, high/low targets
- Recent analyst actions: upgrades, downgrades, initiations, target changes (last 30 days)
- Insider trading: recent buys and sells by officers and directors (Form 4 filings)
- Institutional ownership: % held by institutions, recent 13F activity, major holders
- Short interest: % of float, days to cover, trend direction

### Pillar 5: Peer & Sector Context
- Key competitors and relative performance
- Market share and competitive moat assessment
- Sector health and rotation signals
- Where this stock sits in its industry lifecycle

## Output Format

Deliver the analysis in this structure:

---

# 🔬 Deep Research: {TICKER} — {COMPANY NAME}

**Date:** {TODAY'S DATE}
**Sector:** {SECTOR} | **Industry:** {INDUSTRY}
**Current Price:** ${PRICE} | **Market Cap:** ${CAP}

---

## 📊 TECHNICAL ANALYSIS

| Indicator | Value | Signal |
|---|---|---|
| 20-day MA | ${X} | Above/Below — {bullish/bearish} |
| 50-day MA | ${X} | Above/Below — {bullish/bearish} |
| 200-day MA | ${X} | Above/Below — {bullish/bearish} |
| RSI (14) | {X} | {overbought/neutral/oversold} |
| MACD | {description} | {bullish/bearish} |
| Volume | {vs average} | {above/below average} |
| Beta | {X.XX} | {volatility note} |
| ATR | {X.X%} | {position sizing hint} |

**Chart Story:** {1-2 paragraphs describing the technical picture — trend, key levels, patterns, volume behavior}

**Key Levels:**
- Support: ${X} / ${X} / ${X}
- Resistance: ${X} / ${X} / ${X}

---

## 📈 FUNDAMENTAL SNAPSHOT

| Metric | Value | vs Sector |
|---|---|---|
| P/E (TTM) | {X.X} | {premium/discount/in-line} |
| Forward P/E | {X.X} | {note} |
| PEG Ratio | {X.X} | {note} |
| Revenue Growth (YoY) | {X.X%} | {note} |
| EPS Growth (YoY) | {X.X%} | {note} |
| Gross Margin | {X.X%} | {trend} |
| Operating Margin | {X.X%} | {trend} |
| Net Margin | {X.X%} | {trend} |
| ROE | {X.X%} | {note} |
| Debt/Equity | {X.X} | {note} |
| FCF Yield | {X.X%} | {note} |
| Div. Yield | {X.X%} | {if applicable} |

**Financial Health:** {2-3 sentences on balance sheet strength, cash position, debt load, FCF generation}

**Earnings Quality:** {1-2 sentences on consistency, surprises, guidance trends, accounting red flags}

---

## 📰 NEWS & CATALYSTS

**Last 30 Days — Key Headlines:**
- {Headline 1} — {1-line impact assessment}
- {Headline 2} — {1-line impact assessment}
- {Headline 3} — {1-line impact assessment}
- (etc., top 5-7 stories)

**Current Narrative:** {2-3 sentences on what's driving the stock right now — the story the market is pricing in}

**Upcoming Catalysts:**
- {Date/Event} — {potential impact direction: positive/negative/neutral}
- {Date/Event} — {potential impact direction}

---

## 🏛 WALL STREET & INSIDERS

**Analyst Consensus:**
- Buys: {N} | Holds: {N} | Sells: {N}
- Mean Target: ${X} ({+X%}/{ -X%} vs current)
- High Target: ${X} | Low Target: ${X}

**Recent Analyst Actions:**
- {Date} — {Firm} {upgrades/downgrades/initiates} {TICKER} to ${target} — {note}

**Insider Activity (Last 3 Months):**
- {N} insider buys totaling ${X} (if any)
- {N} insider sales totaling ${X} (if any)
- **Insider Signal:** {bullish/neutral/bearish — explain why}

**Institutional Ownership:**
- % Held by Institutions: {X%}
- Top Holders: {name} ({X%}), {name} ({X%}), {name} ({X%})
- **Institutional Flow:** {accumulating/distributing/neutral}

**Short Interest:**
- % of Float: {X%} | Days to Cover: {X.X}
- **Short Signal:** {bearish alert / neutral / squeeze potential}

---

## 🔍 COMPETITIVE LANDSCAPE

| Competitor | Market Cap | P/E | Rev Growth | Comment |
|---|---|---|---|---|
| {TICKER} | ${X}B | {X} | {X%} | {1-line competitive note} |
| {TICKER} | ${X}B | {X} | {X%} | {1-line competitive note} |
| {TICKER} | ${X}B | {X} | {X%} | {1-line competitive note} |

**Moat Assessment:** {2-3 sentences on competitive advantages, barriers to entry, threats}

---

## ⚖️ BULL CASE vs BEAR CASE

**Bull Case:** {3-5 bullet points of the strongest arguments for owning this stock}

**Bear Case:** {3-5 bullet points of the strongest arguments against owning this stock}

---

## 🎯 VERDICT

## **{BUY / HOLD / SELL}**

**Conviction Level:** {HIGH / MEDIUM / LOW}

**Thesis (1 paragraph):** {Synthesize everything above into a clear, decisive investment thesis. Why this verdict? What's the key insight the market is missing or pricing correctly?}

---

### 📋 Trading Strategy

**Recommended Action:** {BUY / SELL SHORT / WAIT FOR PULLBACK / SELL EXISTING / DO NOTHING}

| Parameter | Value |
|---|---|
| Entry Price | ${X} ({limit order / market order / wait for pullback to ${X}}) |
| Stop Loss | ${X} (-{X.X}%) |
| Target 1 | ${X} (+{X.X}%) — partial profit {X%} |
| Target 2 | ${X} (+{X.X}%) — remaining position |
| R:R Ratio | 1:{X.X} |
| Position Size | {X% of portfolio} |
| Time Horizon | {days/weeks/months} |

**Entry Conditions:**
- {Specific conditions for entering the trade}
- {What must happen before pulling the trigger}

**Stop Management:**
- {When to trail stop to breakeven}
- {Key levels that would invalidate the trade}

**Exit Signals:**
- {What would make you exit early}
- {Fundamental or technical invalidation triggers}

---

*This is AI-generated research for informational purposes only. Not financial advice. Always do your own due diligence before trading. Prices as of {source and timestamp}.*

---

## Important Instructions

1. **Real data only.** Never fabricate a price, ratio, analyst rating, or filing detail. If you can't find reliable data for a metric, mark it "N/A — data unavailable" rather than guessing.
2. **Be decisive.** The user wants a verdict. After weighing all evidence, commit to BUY, HOLD, or SELL. Wishy-washy analysis is useless. If the evidence is truly mixed, say HOLD with medium conviction and explain exactly what would tip the balance.
3. **Conviction matters.** A HIGH conviction call means the signal is clear across technicals, fundamentals, news, and insiders. LOW conviction means mixed signals and higher uncertainty — size down or wait.
4. **Risk first.** Every verdict must include a concrete stop loss and position size. No trade plan without risk management.
5. **Multi-ticker mode.** If the user gives multiple tickers, produce a full report for each, then add a final section: "🏆 HEAD-TO-HEAD: {TICKER1} vs {TICKER2}" with a comparison table and a clear winner recommendation.
6. **Tone.** Sharp, direct, analyst-grade. No cheerleading. If a stock is trash, say so and explain why. If it's a buy, don't hedge — commit.
7. **Disclaimer required.** Always include the disclaimer at the bottom.

## Research Sources

### Data Fetching — Use `wget`, NOT `curl`

**CRITICAL:** `curl` frequently times out or gets blocked by security scanners in terminal environments. **Use `wget` instead** for ALL HTTP data fetches. The User-Agent header is MANDATORY (Yahoo Finance and Finviz return empty responses without it).

See `references/data-fetching.md` for complete fetch-and-parse recipes.

**Step 1: Price & Technicals (Yahoo Finance v8 chart API)**

```bash
wget -q -O /tmp/{ticker}.json --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=1y&interval=1d"
```
Parse with Python to extract price, 52W range, calculate SMA20/50/200, RSI(14), MACD, ATR, and returns.

**Step 2: Fundamentals (Finviz quote page)**

```bash
wget -q -O /tmp/{ticker}_finviz.html --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://finviz.com/quote.ashx?t={TICKER}"
```
Extract with regex: `re.findall(r'snapshot-td2[^>]*>(.*?)</td>', html, re.DOTALL)` — every 2 cells = key + value. Covers P/E, Forward P/E, PEG, EPS, revenue, margins, ROE, ROIC, D/E, short float, beta, analyst target, recommendation, insider/institutional ownership, and more.

**Step 3: Analyst consensus (MarketBeat)**

```bash
wget -q -O /tmp/{ticker}_analyst.html --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://www.marketbeat.com/stocks/NASDAQ/{TICKER}/price-target/"
```

**Step 4: Peers (Finviz screener)**

```bash
wget -q -O /tmp/peers.html --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://finviz.com/screener.ashx?v=111&f=ind_{industry_filter},cap_midover&o=-marketcap"
```

**Reference URLs:**
- Yahoo Finance: `https://finance.yahoo.com/quote/{TICKER}`
- Finviz: `https://finviz.com/quote.ashx?t={TICKER}`
- MarketBeat: `https://www.marketbeat.com/stocks/NASDAQ/{TICKER}/price-target/`
- SEC EDGAR: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={TICKER}`

## Common Pitfalls

1. **Stale data.** Stock prices and ratios change daily. Always check the timestamp on your data. If using yesterday's close, state it.
2. **Cherry-picking catalysts.** Don't list 5 positive headlines and 1 negative. Present the full picture — the user will notice bias.
3. **Verdict without conviction.** "Could go either way" is not analysis. If you can't decide, you haven't done enough research.
4. **Stop losses without technical basis.** Don't say "stop at -5%." The stop must be below a meaningful support level with a clear reason.
5. **Ignoring market cap context.** A $200B mega-cap trades differently than a $2B small-cap. Adjust position sizing and volatility expectations accordingly.
6. **Overweighting news.** News is sentiment, not truth. The most important sections are fundamentals and technicals — news provides context, not the thesis.
7. **Missing the short case.** Even for a BUY verdict, the bear case section must be honest and substantive. If you can't articulate a real bear case, you haven't understood the risks.
8. **No peer context.** A stock that looks cheap at 15x earnings might be expensive if peers trade at 10x. Always benchmark.
9. **Using `curl` instead of `wget`.** `curl` frequently times out, gets blocked by security scanners (especially when piped to Python), or returns empty responses in terminal environments. `curl | python3` pipes are flagged as high-risk. Always use `wget -q -O /tmp/file --header="User-Agent: Mozilla/5.0"` instead — it's more reliable and avoids the pipe-to-interpreter security block.
10. **Large Python scripts in execute_code timing out.** The `execute_code` tool has a 300s timeout. For data fetching, use individual `wget` commands in `terminal()` calls (which return quickly), then a small focused `terminal(python3 ...)` call to parse the downloaded files. Avoid chaining fetch+parse in `execute_code` — the network calls can hang.

## Verification Checklist

- [ ] All data points sourced from real research, not fabricated
- [ ] Technical section includes all key indicators (MAs, RSI, MACD, volume, support/resistance)
- [ ] Fundamental table is complete with sector benchmarks
- [ ] News section covers last 30 days with upcoming catalysts
- [ ] Analyst consensus, insider activity, institutional ownership, and short interest all covered
- [ ] Competitive landscape includes at least 2-3 peers with actual data
- [ ] Bull case and bear case are both substantive (3+ points each)
- [ ] Verdict is clear (BUY/HOLD/SELL) with conviction level stated
- [ ] Trading strategy includes entry, stop, targets, position size, and time horizon
- [ ] All price levels are technically meaningful, not arbitrary
- [ ] R:R ratio is calculated and flagged if below 1:2
- [ ] Disclaimer is included
- [ ] Multi-ticker analysis includes head-to-head comparison if applicable
- [ ] Tone is sharp, decisive, and analyst-grade