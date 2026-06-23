---
name: sp500
description: "Use when the user wants an S&P500 daily investment briefing — identifies the 10 best buy and 10 best sell/short opportunities with detailed trade plans. Triggered by 'SP500 briefing', 'daily market research', 'investment briefing', 'what should I trade today', or similar."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [sp500, investing, trading, equity-research, stock-market, daily-briefing]
    related_skills: [polymarket]
---

# S&P500 Daily Investment Briefing

Act as a professional equity research analyst preparing a daily investment briefing for a sophisticated investor. Research, compile, and deliver a comprehensive S&P500 investment briefing identifying the 10 best buy opportunities and 10 best sell/short opportunities for today's trading session.

## When to Use

- User asks for today's S&P500 trading ideas, stock picks, or market briefing
- User says "run the SP500 briefing", "daily research", "what should I buy/sell"
- User wants a comprehensive market scan with actionable trade plans
- User wants the same output the cron job produces, on demand

Do NOT use for: simple stock quotes, single-company deep dives, portfolio reviews, or non-equity assets.

## Research Process

### 1. Market Overview
Research today's macro environment — futures, overnight moves, key economic data releases, Fed speak, geopolitical events, sector rotation signals. Check major financial news sources for the morning's dominant narratives.

### 2. S&P500 Screening
Identify today's top candidates by researching:
- Pre-market movers and volume anomalies
- Earnings reports (yesterday after close, today before open)
- Analyst upgrades/downgrades from major firms
- Technical breakouts/breakdowns on daily charts
- Unusual options activity (large block trades, put/call skew)
- Relative strength vs the index over 5-day and 20-day periods
- Sector-level momentum and rotation signals

### 3. Selection Criteria
For each candidate, evaluate:
- Fundamental catalyst (earnings, guidance, M&A, regulatory)
- Technical setup (support/resistance levels, moving averages, RSI, MACD)
- Volume profile and institutional flow
- Risk/reward ratio for the trade

## Output Format

Deliver the briefing in this exact format:

---

# 📈 S&P500 Daily Investment Briefing
**Date:** [TODAY'S DATE]
**Market Tone:** [BULLISH / BEARISH / NEUTRAL] — [1-2 sentence macro summary]

---

## 🔥 TOP 10 BUYS

For each of the 10 stocks, provide:

### {N}. {TICKER} — {COMPANY NAME}
**Sector:** {SECTOR}
**Catalyst:** {1-2 sentence reason for today's trade}
**Entry Price:** ${PRICE} (limit order)
**Stop Loss:** ${PRICE} (-{X.X}%)
**Target:** ${PRICE} (+{X.X}%)
**R:R Ratio:** 1:{X.X}

**Trading Strategy:**
- Entry conditions and timing
- Position sizing recommendation
- Key levels to watch (support/resistance)
- When to take partial profits
- Risk management notes

---

## 🔻 TOP 10 SELLS / SHORTS

For each of the 10 stocks, provide:

### {N}. {TICKER} — {COMPANY NAME}
**Sector:** {SECTOR}
**Catalyst:** {1-2 sentence reason to sell/short}
**Entry Price:** ${PRICE} (limit order)
**Stop Loss:** ${PRICE} (-{X.X}%)  [for shorts, this is the cover stop]
**Target:** ${PRICE} (+{X.X}%)
**R:R Ratio:** 1:{X.X}

**Trading Strategy:**
- Entry conditions and timing
- Position sizing recommendation
- Key levels to watch
- When to cover / take profits
- Risk management notes

---

## 📊 S&P500 INDEX LEVELS
- **Previous Close:** ${LEVEL}
- **Key Support:** ${LEVEL} / ${LEVEL} / ${LEVEL}
- **Key Resistance:** ${LEVEL} / ${LEVEL} / ${LEVEL}
- **VIX:** {LEVEL}

## ⚠️ TODAY'S RISK EVENTS
- List key economic data releases with times
- Earnings reports to watch
- Any geopolitical or macro risk factors

---

## Important Instructions

1. Use actual research — search financial news, check real data sources. Never fabricate prices, levels, or catalysts.
2. If you cannot find reliable data for a stock, reduce the count rather than guessing. Quality over quantity.
3. Prices should reflect pre-market or yesterday's close levels. Clearly state which you're using.
4. Stop losses should be technically meaningful (below a support level, above a resistance level) — not arbitrary percentages.
5. The R:R ratio (reward-to-risk) should be at least 1:2 for buys and 1:2 for shorts. If the setup doesn't offer this, flag it and explain why it's still worth considering.
6. Include a disclaimer at the bottom: "This is AI-generated research for informational purposes only. Not financial advice. Always do your own due diligence before trading."
7. Be specific and actionable — the reader should be able to place orders based on your analysis.
8. Write with the tone of a sharp, experienced sell-side research analyst — direct, data-driven, no fluff.

## Tools

Use `web_search` (or `terminal` with curl) to research real-time data from financial news sources (Bloomberg, Reuters, CNBC, MarketWatch, Yahoo Finance, Finviz, etc.). Search for:
- "S&P500 futures today"
- "pre-market movers [today's date]"
- "analyst upgrades downgrades [today's date]"
- "earnings reports [today's date]"
- "unusual options activity [today's date]"
- "[TICKER] stock price technical analysis"
- "VIX today"
- "economic calendar [today's date]"
- "FOMC Fed meeting [current month/year]"
- "sector rotation [current month]"

Use `terminal` for any data processing or formatting as needed.

## Common Pitfalls

1. **Fabricating data** — Never guess prices, levels, or catalysts. If a source is unavailable, narrow the list rather than making up numbers. The user will check.
2. **Stale data** — Always verify whether you're looking at yesterday's close, pre-market, or live prices. State your source clearly.
3. **Ignoring macro** — Don't jump straight to stock picks. The Market Overview section sets the context and informs sector selection.
4. **Weak stops** — Stops must be technically meaningful (below support, above resistance). Arbitrary -5% stops are lazy.
5. **Poor R:R** — Flag setups below 1:2. Recommend reduced position size or skipping the trade.
6. **Missing risk events** — Always check the economic calendar. FOMC, CPI, NFP days demand extra caution.
7. **Ignoring short interest** — For shorts, high short interest means squeeze risk. Always note the float short %.
8. **Overconfidence** — Include the disclaimer. You are not a fiduciary.

## Verification Checklist

- [ ] Market overview includes futures, overnight moves, and key macro narratives
- [ ] All 10 buys have specific entry/stop/target prices and a trading strategy
- [ ] All 10 sells/shorts have specific entry/stop/target prices and a trading strategy
- [ ] R:R ratios are calculated and flagged if below 1:2
- [ ] S&P500 index levels section includes support, resistance, and VIX
- [ ] Risk events section covers economic calendar and earnings
- [ ] Disclaimer is included
- [ ] Tone is sharp, data-driven, actionable — no fluff