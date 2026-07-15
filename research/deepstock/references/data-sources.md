# Deepstock — Verified Data Sources & Extraction Techniques

Tested July 2026. Use these when the skill's listed web sources are blocked or web_search/web_extract tools are unavailable.

## Working Without Web Tools (web_search / web_extract)

If Firecrawl/web tools are not configured, use `terminal` (curl) + `browser` tools instead. The full report can still be produced.

## Yahoo Finance — v8 Chart API (NO AUTH REQUIRED)

**Endpoint:** `https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=1y&interval=1d`

Works with just a `User-Agent` header. Returns JSON with:
- `meta.regularMarketPrice` — current price
- `meta.fiftyTwoWeekHigh` / `meta.fiftyTwoWeekLow`
- `meta.regularMarketVolume`
- `timestamp[]` + `indicators.quote[0].{close,high,low,volume}[]` — full OHLCV series

Calculate from this data:
- Moving averages (20/50/200-day): `sum(closes[-N:])/N`
- RSI (14-day): average gains/losses over last 14 deltas
- ATR (14-day): max of (H-L, |H-Cprev|, |L-Cprev|) averaged
- Bollinger Bands: SMA20 ± 2×stddev
- MACD: EMA12 - EMA26, signal = 9-day EMA of MACD line
- YTD/1m/3m returns: compare closes at offsets

**Example curl+python pattern:**
```bash
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/ORCL?range=1y&interval=1d" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
data = json.load(sys.stdin)
result = data['chart']['result'][0]
meta = result['meta']
closes = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
print('Price:', meta['regularMarketPrice'])
print('20MA:', sum(closes[-20:])/20)
# ... etc
"
```

Use `range=6mo` for Bollinger/MACD (enough data for 200-day isn't needed there).

## Yahoo Finance — v10 quoteSummary API (BROKEN — DO NOT USE)

**Endpoint:** `https://query2.finance.yahoo.com/v10/finance/quoteSummary/{TICKER}?modules=...`

Returns `{"error":{"code":"Unauthorized","description":"Invalid Crumb"}}`. Yahoo now requires a crumb token + cookie. Do not waste time on this endpoint.

## Yahoo Finance — Browser Extraction (RELIABLE METHOD)

Navigate to Yahoo Finance pages and extract data via `browser_console` JavaScript evaluation:

1. `browser_navigate` to the Yahoo Finance page (e.g., `https://finance.yahoo.com/quote/{TICKER}/key-statistics`)
2. If an AlphaSpace ad dialog appears, close it first
3. Extract table data via console:

```javascript
// Extract all table rows from statistics page
var tables = document.querySelectorAll('table');
var allData = [];
tables.forEach(function(table) {
  var rows = table.querySelectorAll('tr');
  rows.forEach(function(row) {
    var cells = row.querySelectorAll('td, th');
    var rowData = [];
    cells.forEach(function(cell) { rowData.push(cell.textContent.trim()); });
    if (rowData.length > 1) allData.push(rowData.join(' | '));
  });
});
JSON.stringify({data: allData}, null, 2);
```

For financials/analysis pages, extract `article.innerText`:
```javascript
var article = document.querySelector('article') || document.querySelector('main');
JSON.stringify({text: article ? article.innerText.substring(0, 10000) : ''});
```

**Key Yahoo Finance pages to visit (in order):**
- `/quote/{TICKER}` — summary (price, volume, beta, P/E, EPS, 1y target, div yield)
- `/quote/{TICKER}/key-statistics` — full valuation, financial, trading stats
- `/quote/{TICKER}/financials` — income statement (annual, TTM)
- `/quote/{TICKER}/analysis` — analyst estimates, earnings history, EPS revisions
- `/quote/{TICKER}/holders` — institutional ownership, insider transactions
- `/quote/{TICKER}/news` — recent headlines

**Pitfall:** AlphaSpace promotional modal may appear on navigation. Close it (click the Close button ref) before proceeding.

## SEC EDGAR — Submissions JSON (NO AUTH, JUST USER-AGENT)

**Endpoint:** `https://data.sec.gov/submissions/CIK{10-digit-CIK}.json`

Requires only a `User-Agent` header with contact info. Returns recent filings (form types, dates, accession numbers).

Common CIK numbers:
- ORCL: 0001341439
- AAPL: 0000320193
- MSFT: 0000789019
- GOOGL: 0001652044
- AMZN: 0001018724
- META: 0001326801
- TSLA: 0001318605
- NVDA: 0001045810

**Extract filings by type:**
```bash
curl -s "https://data.sec.gov/submissions/CIK0001341439.json" \
  -H "User-Agent: Your Name your@email.com" | python3 -c "
import json, sys
data = json.load(sys.stdin)
recent = data['filings']['recent']
for i in range(len(recent['form'])):
    if recent['form'][i] in ['10-K', '10-Q', '8-K', '4']:
        print(f\"{recent['filingDate'][i]} | {recent['form'][i]} | {recent['accessionNumber'][i]}\")
"
```

- Form 4 = insider trades
- 10-K = annual report
- 10-Q = quarterly report
- 8-K = material events (earnings, M&A, guidance changes)

## Finviz — BLOCKED BY CLOUDFLARE

`https://finviz.com/quote.ashx?t={TICKER}` triggers Cloudflare bot detection ("Just a moment..."). Do not attempt via browser. Skip Finviz and use Yahoo Finance + SEC EDGAR instead.

## Peer Comparison Data

Use the v8 chart API for peer prices:
```bash
for ticker in MSFT CRM SAP IBM; do
  curl -s "https://query1.finance.yahoo.com/v8/finance/chart/$ticker?range=1d&interval=1d" \
    -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
meta = json.load(sys.stdin)['chart']['result'][0]['meta']
print(f'$ticker: {meta[\"regularMarketPrice\"]}')
"
done
```

For peer fundamentals (P/E, margins, debt), navigate to each peer's `/key-statistics` page via browser and extract tables.

## Technical Indicator Calculation Reference

All calculable from the v8 chart API OHLCV data:

| Indicator | Formula |
|---|---|
| SMA(N) | `sum(closes[-N:]) / N` |
| RSI(14) | `100 - 100/(1 + avg_gain_14/avg_loss_14)` |
| ATR(14) | `avg of max(H-L, abs(H-Cprev), abs(L-Cprev)) over 14 bars` |
| Bollinger | `SMA20 ± 2 * stdev(closes[-20:])` |
| MACD | `EMA12 - EMA26`; Signal = EMA9 of MACD |
| EMA(N) | `price * (2/(N+1)) + prev_EMA * (1 - 2/(N+1))` |
| YTD Return | `(current / first_close_of_year - 1) * 100` |
