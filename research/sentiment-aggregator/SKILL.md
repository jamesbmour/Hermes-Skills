---
name: sentiment-aggregator
description: "Use when the user wants to gauge market sentiment on a stock, sector, or the overall market — aggregating news sentiment, analyst rating changes, social media buzz, put/call ratios, short interest, and fear/greed indicators. Triggered by 'sentiment check on TSLA', 'market sentiment today', 'what's the mood on tech stocks', 'analyst sentiment NVDA', 'fear and greed index', 'most upgraded stocks this week', 'sentiment analysis AAPL', or any request for multi-source sentiment assessment."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sentiment, news-sentiment, analyst-ratings, social-media, fear-greed, put-call-ratio]
    related_skills: [deepstock, sp500, macro-dashboard, insider-tracker]
---

# Sentiment Aggregator

## Overview

Aggregate sentiment signals from multiple independent sources into a composite view. No single sentiment source is reliable alone — news can be noise, social media can be manipulated, analyst ratings lag. But when 3+ sources align in the same direction, it's a meaningful signal. This skill gathers, normalizes, and combines them.

## When to Use

- "sentiment check on TSLA"
- "market sentiment today — fear or greed"
- "what's the mood on tech stocks"
- "analyst sentiment for NVDA"
- "most upgraded stocks this week"
- "put/call ratio for SPY"
- "sentiment analysis AAPL"
- "which stocks are analysts turning bullish on"
- "social sentiment vs analyst sentiment — any divergences"

**Don't use for:** deep fundamental analysis (use `deepstock`), technical signals (use `technical-scanner`), or specific trade recommendations (sentiment is a input, not a signal on its own).

---

## Sentiment Sources

### 1. Analyst Ratings (Most Weight)

**Source:** Yahoo Finance quoteSummary — recommendation trend + upgrade/downgrade history.

```bash
# Pull analyst data
curl -s -b /tmp/yahoo_cookies.txt \
  "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{TICKER}?modules=recommendationTrend,upgradeDowngradeHistory&crumb={CRUMB}" \
  -H "User-Agent: Mozilla/5.0"
```

**What to extract:**
- Current consensus: strongBuy / buy / hold / sell / strongSell counts
- Mean recommendation (1.0 = Strong Buy, 5.0 = Strong Sell)
- Trend: is consensus improving or deteriorating? (compare current month vs 3 months ago)
- Recent actions (last 30 days): upgrades, downgrades, initiations, target changes

**Sentiment score:** Normalize to -100 (universal sell) to +100 (universal buy).

### 2. News Sentiment

**Source:** Google News, financial headlines, press releases.

Search for recent headlines and assess tone:
```bash
# Search for recent news
"\"{TICKER}\" news today" → extract 10-15 headlines
```

**Classify each headline:** positive (+1), neutral (0), negative (-1).

**Headline signals:**
- Positive: "beats estimates," "raises guidance," "new product," "upgrade," "partnership," "expansion"
- Negative: "misses estimates," "cuts guidance," "layoffs," "downgrade," "lawsuit," "investigation," "recall"
- Neutral: "reports earnings" (without beat/miss), "appoints new executive," "announces dividend"

**Compute:** Net sentiment = (positives - negatives) / total headlines × 100.

### 3. Options Market (Put/Call Ratio)

**Source:** Yahoo Finance options data or search for current put/call ratio.

**Interpretation:**
- Put/Call < 0.7: Bullish (more calls than puts — traders betting on upside)
- Put/Call 0.7–1.0: Neutral
- Put/Call > 1.0: Bearish (more puts than calls — hedging or betting on downside)
- Put/Call > 1.5: Very bearish / potential contrarian buy signal

**Trend direction:** Is the ratio rising (bearish shift) or falling (bullish shift)?

### 4. Short Interest

**Source:** Yahoo Finance key statistics — shortPercentOfFloat, shortRatio (days to cover).

**Interpretation:**
- Short % < 5%: Normal — no signal
- Short % 5–10%: Elevated — bears have conviction
- Short % 10–20%: High — potential squeeze candidate if bullish catalyst emerges
- Short % > 20%: Extreme — crowded short, high squeeze risk
- Days to cover > 5: Hard to exit short, amplifies squeeze potential

**Trend:** Is short interest rising (increasing bearishness) or falling (shorts covering = bullish)?

### 5. Social Media Buzz

**Source:** Web search for Reddit mentions, Stocktwits activity, X/Twitter volume.

Search for ticker mentions and assess:
- **Volume:** Unusual spike in mentions? (2x+ normal daily volume)
- **Tone:** Scan top posts/comments for sentiment
- **Trending:** Is the ticker appearing on WallStreetBets trending, Stocktwits trending?

```bash
# Search for social mentions
"{TICKER} reddit wallstreetbets OR stocks OR investing site:reddit.com"
"{TICKER} stocktwits"
```

### 6. Fear & Greed Index (Market-Wide)

For market-wide sentiment queries, pull the CNN Fear & Greed Index or equivalent:

```bash
# Alternative: compute from components
# 1. Market momentum: SPY vs 125-day MA
# 2. Stock price strength: % of NYSE stocks at 52-week highs vs lows
# 3. Stock price breadth: advancing vs declining volume
# 4. Put/Call ratio (already covered)
# 5. Market volatility: VIX level (VIX < 15 = greed, VIX > 30 = fear)
# 6. Safe haven demand: stocks vs bonds performance spread
# 7. Junk bond demand: high-yield spread vs investment grade
```

**VIX as proxy (simplest):**
- VIX < 12: Extreme Greed
- VIX 12–18: Greed
- VIX 18–25: Neutral
- VIX 25–35: Fear
- VIX > 35: Extreme Fear

---

## Composite Sentiment Score

Combine all sources into a single view:

| Source | Weight | Rationale |
|--------|--------|-----------|
| Analyst ratings | 25% | Institutional, research-backed, but lags price |
| News sentiment | 20% | Real-time but noisy — headlines vs substance |
| Options (P/C ratio) | 20% | Money-backed conviction — real positions |
| Short interest | 15% | Conviction indicator, squeeze risk |
| Social media buzz | 10% | Retail sentiment, early trends, but easily manipulated |
| Fear & Greed / VIX | 10% | Market-wide context |

Normalize each source to -100 to +100 scale. Weight and average for composite score.

---

## Output Format

```markdown
# 🎭 Sentiment Analysis: {TICKER or MARKET}

**Date:** {TODAY'S DATE} | **Price:** ${X} | **Composite Score:** {+XX} (Bullish / Neutral / Bearish)

---

## 📊 Composite Sentiment

| Source | Reading | Score | Signal |
|--------|---------|-------|--------|
| Analyst Consensus | {X} buys / {Y} holds / {Z} sells (rating: {X.XX}) | {+XX} | Bullish / Neutral / Bearish |
| News Sentiment | {X} positive / {Y} negative / {Z} neutral | {+XX} | Bullish / Neutral / Bearish |
| Put/Call Ratio | {X.XX} | {+XX} | Bullish / Neutral / Bearish |
| Short Interest | {X.X%} of float ({X.X} days to cover) | {+XX} | Bullish / Neutral / Bearish |
| Social Buzz | {volume description} | {+XX} | Bullish / Neutral / Bearish |
| **Composite** | — | **{+XX}** | **{BULLISH / NEUTRAL / BEARISH}** |

---

## 🔍 Source Detail

### Analyst Consensus
- Current: {X} Strong Buy, {Y} Buy, {Z} Hold, {W} Sell, {V} Strong Sell
- Mean target: ${X} ({+X%}/{ -X%} vs current)
- 3-month trend: consensus {improving/deteriorating/stable} (mean rating {X.XX} → {Y.YY})
- Recent: {firm upgraded/downgraded to ${target} on {date} — {note}}

### News Pulse
**Last 7 days — {N} headlines analyzed:**
- 🟢 Positive: {summary of top positive themes}
- 🔴 Negative: {summary of top negative themes}
- ⚪ Neutral: {summary if material}

### Options Market
- Put/Call Ratio (current): {X.XX}
- Trend: {rising/falling/stable} over last {period}
- Interpretation: {what the ratio suggests + any contrarian read}

### Short Interest
- % of Float: {X.X%} | Days to Cover: {X.X}
- Trend vs last month: {X.X% → Y.Y%} ({rising/falling})
- Squeeze Risk: {LOW / MODERATE / HIGH / EXTREME}

### Social Buzz
- Mention volume: {X} mentions (vs {Y} average — {+X%} above normal)
- Dominant tone: {bullish/neutral/bearish}
- Trending on: {platforms if applicable}
- Notable narratives: {what retail is saying}

---

## ⚠️ Divergences

{If sources disagree significantly, highlight the divergence}

> **Example:** Analysts are cautiously bullish (rating 2.1) but the put/call ratio has spiked to 1.4 — options traders are hedging heavily. Social media is euphoric. This mix of institutional caution + retail euphoria + options hedging often precedes volatility.

---

## 🎯 Key Takeaways

1. **Strongest signal:** {Which source is most decisive and why}
2. **Weakest signal:** {Which source is noisy or contradictory}
3. **Directional bias:** {Overall, sentiment is {supportive/hostile/ambivalent} toward this stock/sector/market}
4. **Watch for:** {What would change the sentiment picture — earnings, Fed decision, technical level}
```

---

## Important Instructions

1. **Weight analyst and options data highest.** These represent real money and institutional research. News and social media are secondary.
2. **Divergence is the signal.** When analysts say "buy" but options traders are buying puts, that's more informative than when everyone agrees.
3. **Contrarian interpretation.** Extreme bullish sentiment can be a sell signal. Extreme bearish sentiment can be a buy signal. Flag extreme readings explicitly.
4. **Ticker-level vs market-level.** Ticker-level uses all sources. Market-level drops short interest and analyst ratings (use VIX + P/C ratio + breadth + macro).
5. **Real data only.** Pull actual analyst consensus, actual put/call ratios, actual short interest. Never fabricate sentiment readings.
6. **Timestamp everything.** Sentiment changes fast. Note when each data point was captured.

## Common Pitfalls

1. **Overweighting social media.** Reddit can pump a stock from euphoria alone — and dump it just as fast. Social sentiment is the least reliable source. Weight it accordingly (10%).
2. **Treating analyst consensus as truth.** Analysts are slow to downgrade and have sell-side bias. A "Hold" from Wall Street often means "Sell" in plain English.
3. **Ignoring the trend.** A put/call ratio of 0.8 that was 0.5 last week (rising fast) is more bearish than a ratio of 1.2 that was 1.4 last week (falling). Direction matters more than level.
4. **Sentiment without price context.** Bullish sentiment at all-time highs is normal. Bullish sentiment after a 30% drawdown is a stronger signal. Always note the price context.
5. **Composite overconfidence.** A +65 composite score sounds precise but is built on noisy inputs. Present the composite with humility — and always show the individual components so the user can judge for themselves.

## Verification Checklist

- [ ] All sentiment sources pulled from real data (not fabricated)
- [ ] Analyst consensus includes trend (current vs 3 months ago)
- [ ] News headlines actually searched and classified (not estimated)
- [ ] Put/call ratio pulled from actual options data
- [ ] Short interest includes both % of float and days to cover
- [ ] Divergences between sources explicitly highlighted
- [ ] Composite score calculated with stated weights
- [ ] Price context noted (ATH, near support, in drawdown, etc.)
- [ ] Extreme readings flagged as potential contrarian signals
- [ ] Data timestamps included
