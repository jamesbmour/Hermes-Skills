# Data Extraction Techniques for Stock Research

When `web_search` / `web_extract` are unavailable (Firecrawl not configured) or sites block text extraction, use `browser_navigate` + `browser_console` with JavaScript DOM extraction. All snippets below use IIFE wrapping to avoid variable redeclaration errors across calls.

## 1. Yahoo Finance Summary Stats (quote page)

```javascript
(() => {
  const items = {};
  document.querySelectorAll('li').forEach(li => {
    const spans = li.querySelectorAll('span, fin-streamer');
    if (spans.length >= 2) {
      const label = spans[0].textContent?.trim();
      const value = spans[spans.length - 1].textContent?.trim();
      if (label && value && label.length < 50) items[label] = value;
    }
  });
  return JSON.stringify(items, null, 2);
})()
```

Returns: Previous Close, Open, Day's Range, 52 Week Range, Volume, Avg. Volume, Market Cap, Beta, P/E, EPS, Earnings Date, Dividend, 1y Target Est.

## 2. Yahoo Finance Full Statistics (key-statistics page)

```javascript
(() => {
  const t = {};
  document.querySelectorAll('table').forEach((table, idx) => {
    const rows = table.querySelectorAll('tr');
    const data = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td, th');
      const rowData = [];
      cells.forEach(cell => rowData.push(cell.textContent?.trim()));
      if (rowData.length > 0) data.push(rowData);
    });
    if (data.length > 0) t['table_' + idx] = data;
  });
  return JSON.stringify(t, null, 2);
})()
```

Returns: Valuation measures (P/E, Forward P/E, P/S, P/B, EV/Revenue, EV/EBITDA), profitability (margins, ROE, ROA), balance sheet (cash, debt, current ratio), short interest, moving averages, dividend data, shares outstanding, float, insider/institutional %.

## 3. Yahoo Finance Analyst Estimates (analysis page)

Same table extraction as above. Returns: Revenue/EPS estimates for current/next quarter and year, EPS surprise history, estimate revision trends (up/down last 7/30 days), growth vs S&P 500.

## 4. Yahoo Finance Holders (holders page)

```javascript
(() => {
  const t = {};
  document.querySelectorAll('table').forEach((table, idx) => {
    const rows = table.querySelectorAll('tr');
    const data = [];
    rows.forEach(row => {
      const cells = row.querySelectorAll('td, th');
      const rowData = [];
      cells.forEach(cell => rowData.push(cell.textContent?.trim()));
      if (rowData.length > 0) data.push(rowData);
    });
    if (data.length > 0) t['table_' + idx] = data;
  });
  return JSON.stringify(t, null, 2);
})()
```

Returns: Major holders breakdown (% insider, % institutional, % float institutional, # institutions), top institutional holders with shares/date/%/value, top mutual fund/ETF holders.

## 5. Yahoo Finance Financials (financials page)

```javascript
(() => {
  const article = document.querySelector('article');
  if (article) return article.textContent.substring(0, 8000);
  return 'no article found';
})()
```

Returns: Full income statement text — Total Revenue, Cost of Revenue, Gross Profit, Operating Income, Net Income, EPS (basic/diluted), EBITDA, shares outstanding. Annual or quarterly via tab toggle.

## 6. Yahoo Finance Historical Prices (history page)

```javascript
(() => {
  const table = document.querySelector('table');
  if (!table) return 'no table';
  const rows = table.querySelectorAll('tr');
  const data = [];
  rows.forEach(row => {
    const cells = row.querySelectorAll('td, th');
    const rowData = [];
    cells.forEach(cell => rowData.push(cell.textContent?.trim()));
    if (rowData.length > 0) data.push(rowData);
  });
  return JSON.stringify(data.slice(0, 30), null, 2);
})()
```

Returns: Most recent 30 days of OHLCV data for technical analysis (MAs, RSI estimation, support/resistance).

## 7. Yahoo Finance News Headlines (news page)

```javascript
(() => {
  const headlines = [];
  document.querySelectorAll('h3').forEach(h => {
    const text = h.textContent?.trim();
    if (text && text.length > 15) headlines.push(text);
  });
  return JSON.stringify(headlines.slice(0, 20), null, 2);
})()
```

Returns: Top 20 recent news headlines for the ticker.

## 8. Yahoo Finance Profile (profile page)

```javascript
(() => {
  const textBlocks = [];
  document.querySelectorAll('p, span, div, h3').forEach(el => {
    const text = el.textContent?.trim();
    if (text && text.length > 20 && text.length < 500) {
      if (!textBlocks.includes(text)) textBlocks.push(text);
    }
  });
  return JSON.stringify(textBlocks.slice(0, 40), null, 2);
})()
```

Returns: Company address, sector, industry, employee count, key executives, governance scores, recent SEC filings (8-K dates), dividend dates.

## 9. MarketBeat Comprehensive Stats

Navigate to `https://www.marketbeat.com/stocks/{EXCHANGE}:{TICKER}/` where EXCHANGE is NYSE or NASDAQ.

```javascript
(() => {
  const dls = document.querySelectorAll('dl, [class*="description-list"]');
  const stats = {};
  dls.forEach(dl => {
    const terms = dl.querySelectorAll('dt');
    const defs = dl.querySelectorAll('dd');
    terms.forEach((term, i) => {
      if (defs[i]) stats[term.textContent?.trim()] = defs[i].textContent?.trim();
    });
  });
  return JSON.stringify(stats, null, 2);
})()
```

Returns: Consensus rating, price targets (avg/high/low), analyst count, EPS, P/E, margins, ROE, debt, short interest, dividend yield, insider/institutional %, beta, and more — all in one call.

Also extract sectioned text for qualitative analysis:

```javascript
(() => {
  const sections = {};
  let current = 'intro';
  document.querySelectorAll('h2, h3, h4, p, li, span, div').forEach(el => {
    const text = el.textContent?.trim();
    if (!text || text.length < 5) return;
    if (el.tagName === 'H2' || el.tagName === 'H3' || el.tagName === 'H4') {
      current = text.substring(0, 60);
      sections[current] = [];
    } else if (text.length > 20 && text.length < 300) {
      if (!sections[current]) sections[current] = [];
      if (!sections[current].includes(text)) sections[current].push(text);
    }
  });
  const relevant = {};
  Object.keys(sections).forEach(key => {
    if (sections[key].length > 0) relevant[key] = sections[key].slice(0, 5);
  });
  return JSON.stringify(relevant, null, 2);
})()
```

Returns: Narrative text for consensus rating, upside potential, analyst coverage, earnings growth, short interest commentary, dividend strength, insider trading, news headlines.

## Key Notes

- **Dismiss modals first**: Yahoo Finance statistics page may show a promo modal. Click the Close button before extracting.
- **IIFE wrapping is mandatory**: `(() => { ... })()` prevents `SyntaxError: Identifier already declared` when running multiple extractions on the same page session.
- **Float and insider ownership**: MarketBeat's description list has `Free Float` and `Percentage Held by Insiders` — critical for thin-float stocks like UI (93% insider, 4.2M float).
- **Peer data**: Navigate to each peer's Yahoo summary page and run snippet #1. Extract just the key fields you need (market cap, P/E, revenue growth) to keep context small.
- **Estimate revision trends**: Yahoo Finance analysis page tables show estimates from 7/30/60/90 days ago vs current — downward revisions are a bearish signal worth flagging.
