---
name: congress-trading
description: "Use when the user wants to track stock trades made by US senators and representatives under the STOCK Act — unusual activity, top traders, sector concentration, or specific politician trades. Triggered by 'congress trading', 'what are politicians buying', 'Pelosi trades', 'senate stock trades', 'congressional insider trading', 'STOCK Act disclosures', 'politician portfolio tracker', 'who in Congress is trading NVDA', or any request about political figure stock trading activity."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [congress, trading, STOCK-Act, politicians, disclosures, insider-trading, senate, house]
    related_skills: [deepstock, sp500, insider-tracker]
---

# Congress Trading Tracker

## Overview

Track stock trades disclosed by US members of Congress under the STOCK Act of 2012. Identify unusual trading patterns — cluster buying, well-timed trades ahead of policy changes, top-performing politicians, and sector-level congressional positioning. This data is public, legally mandated, and closely watched for signals about which industries and companies are attracting political attention.

## When to Use

- "what are members of Congress buying"
- "show me Pelosi's latest trades"
- "congressional trading activity this quarter"
- "which politicians are trading NVDA"
- "most active congressional traders"
- "what sectors is Congress buying"
- "senate stock trades this month"
- "any unusual congressional buying patterns"
- "compare Democrat vs Republican trades"

**Don't use for:** corporate insider trading (use `insider-tracker`), investment advice (these are disclosures, not recommendations), or real-time trade alerts (disclosures are filed with 30-45 day delay).

---

## Research Process

### Step 1: Pull Recent Disclosures

Congressional trade disclosures are available from multiple public sources. The most accessible:

**Primary source — Senate Financial Disclosures:**
Search for recent filings using web search with specific queries:
- "senate stock trade disclosures June 2026"
- "STOCK Act filing site:senate.gov 2026"
- "Periodic Transaction Report senator stock"

**Aggregator sites (easier to parse):**
- Capitol Trades (capitoltrades.com) — tracks and aggregates all congressional trades
- House Stock Watcher — tracks House members
- Senate Stock Watcher — tracks Senate members
- Quiver Quantitative — congressional trading dashboard
- Unusual Whales — includes congress trading section

**Direct scraping approach:**

```bash
# Search for recent congressional trade roundups
curl -s "https://www.capitoltrades.com/trades" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  | python3 -c "
import sys, re, json
html = sys.stdin.read()
# Look for embedded JSON data with trade information
matches = re.findall(r'\"trades\":\\[(.*?)\\]', html)
# Parse and extract ticker, politician, amount, date, type (buy/sell)
print(matches[:5] if matches else 'No embedded data found')
"
```

**Alternative approach — web search + manual extraction:**
When automated scraping is unreliable, use web search to find roundup articles, then extract the data manually:

```
"congressional stock trades" "this week" OR "this month" OR "June 2026"
"members of congress" "disclosed" "stock purchase" OR "stock sale"
"Nancy Pelosi stock trades" "latest"
```

### Step 2: Categorize and Analyze

For each trade found, record:

| Field | Example |
|-------|---------|
| Politician | Nancy Pelosi (D-CA) |
| Chamber | House / Senate |
| Party | Democrat / Republican / Independent |
| Committee | Financial Services, Armed Services, etc. |
| Ticker | NVDA |
| Transaction | Buy / Sell / Option exercise |
| Amount range | $100K–$250K (STOCK Act uses ranges) |
| Filing date | June 10, 2026 |
| Trade date | May 15, 2026 |
| Sector | Technology |

### Step 3: Identify Patterns

**Cluster buying:** 3+ members of Congress buying the same stock within 30 days. This is the strongest signal — suggests information flow from committee hearings or briefings.

**Committee-relevant trades:** A member of the Armed Services Committee buying defense stocks. A member of the Finance Committee trading banks. These are the most scrutinized trades.

**Unusual timing:** Trades made just before major policy announcements or regulatory actions affecting that company or sector.

**Top traders by volume:** Which politicians trade the most? High volume can signal either insight or recklessness.

**Sector concentration:** Are trades clustering in specific sectors (tech, defense, energy, healthcare)?

### Step 4: Performance Analysis (if data available)

Some aggregators track estimated returns of congressional portfolios. If available:
- Top 3 performing politicians (trailing 12 months)
- Politicians who consistently beat SPY
- Politicians whose trades are most inversely correlated with their policy positions

---

## Output Format

```markdown
# 🏛 Congress Trading Dashboard

**Period:** {date range} | **Total trades found:** {N} | **Data source:** {source}

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| Total trades disclosed | {N} |
| Buys vs Sells | {X} buys / {Y} sells |
| Most active trader | {Name} ({N} trades) |
| Most traded ticker | {TICKER} ({N} trades) |
| Top sector | {Sector} ({X}% of activity) |
| Largest single trade | {Name} {bought/sold} ${amount} of {TICKER} |

---

## 🔥 Notable Trades

| Date | Politician | Party | Ticker | Action | Amount | Committee | Context |
|------|-----------|-------|--------|--------|--------|-----------|---------|
| {date} | {Name} | {D/R} | {TICKER} | {Buy/Sell} | {range} | {committee} | {1-line significance} |

---

## 🐝 Cluster Activity

**{TICKER} — {N} members traded within {X} days:**
- {Name} ({party}, {committee}) — {bought/sold} ${range} on {date}
- {Name} ({party}, {committee}) — {bought/sold} ${range} on {date}

**Why it matters:** {1-2 sentences on what committee overlap, timing, or policy context makes this cluster significant}

---

## 🏢 Most Traded Sectors

| Sector | # of Trades | # of Politicians | Top Ticker | Signal |
|--------|------------|-----------------|------------|--------|
| {Sector} | {N} | {N} | {TICKER} | {bullish/bearish/mixed} |

---

## 👤 Top Individual Traders

| Politician | Party | Trades | Top Holdings | Estimated Return | Committee Relevance |
|------------|-------|--------|-------------|------------------|-------------------|
| {Name} | {D/R} | {N} | {tickers} | {+X% vs SPY +Y%} | {relevant committees} |

---

## ⚠️ Important Context

1. **45-day disclosure delay.** These trades happened 30-45 days ago. The information advantage may have already played out.
2. **Amounts are ranges.** STOCK Act disclosures use broad ranges ($1K–$15K, $50K–$100K, $100K–$250K, etc.) — not exact amounts.
3. **Spouse and dependent trades included.** A disclosure may reflect a spouse's independent decision, not the politician's.
4. **Not all trades are informed.** Some politicians are bad traders. Track record matters more than individual trades.
5. **Ethics investigations.** Some politicians have been investigated for STOCK Act violations. Note this context when relevant.

---

## 🎯 Key Takeaways

1. **Strongest signal:** {What pattern stands out most — cluster, sector concentration, well-timed trade}
2. **Fade potential:** {Any trades that look like chasing, late entries, or political posturing rather than informed positioning}
3. **Watch for:** {Upcoming policy events that could drive or explain the trading pattern}
```

---

## Important Instructions

1. **Use multiple sources.** No single aggregator is complete. Cross-reference Capitol Trades, Senate/House disclosure databases, and news roundups.
2. **Context is everything.** A senator buying defense stocks means more if they sit on the Armed Services Committee. Always note committee assignments.
3. **Don't overhype.** Congressional trading data is public, delayed, and ranges-based. "Pelosi bought NVDA calls" is interesting but not a trading signal in isolation.
4. **Bipartisan analysis.** Track both parties equally. If Democratic trades cluster in green energy and Republican trades in oil & gas, say so — but don't editorialize.
5. **Mention the delay.** Always remind the user that disclosures lag 30-45 days behind actual trades.
6. **Real data only.** Pull from actual sources. If data is sparse (quiet filing period), say so rather than padding.

## Common Pitfalls

1. **Treating every trade as informed.** Members of Congress underperform the market on average. Track record matters.
2. **Ignoring committee context.** The key insight isn't "a politician bought a stock" — it's "a member of the committee overseeing that industry bought the stock."
3. **Single-source reliance.** Different aggregators have different coverage. Capitol Trades is solid but not exhaustive.
4. **Not checking trade date vs filing date.** The filing date is when they disclosed. The trade date is when they actually traded. The gap is where the information asymmetry lives.
5. **Overweighting one politician.** Even the best-known congressional trader (Pelosi) makes losing trades. Look for patterns across multiple members.
6. **Forgetting the disclosure format.** Trades are reported in broad ranges — "$100,001–$250,000" not "$187,500." Don't fabricate precision.

## Verification Checklist

- [ ] Trades pulled from at least 2 independent sources
- [ ] Each trade includes: politician, party, chamber, committee, ticker, action, amount range, trade date, filing date
- [ ] Committee assignments checked for context
- [ ] Cluster activity identified and analyzed
- [ ] Sector concentration noted
- [ ] 45-day disclosure delay explicitly mentioned
- [ ] Amounts correctly shown as ranges, not precise figures
- [ ] Bipartisan coverage (both parties represented)
- [ ] Key takeaways are specific and supported by the data
