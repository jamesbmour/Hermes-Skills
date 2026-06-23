# Yahoo Finance Chart API Reference

## Endpoint

```
GET https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}?range={RANGE}&interval={INTERVAL}
```

## Required Headers

```python
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
```

Without the User-Agent header, Yahoo returns an empty body (0 bytes), causing JSON parse errors like `Expecting value: line 1 column 1 (char 0)`.

## SSL Configuration

```python
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

Yahoo's TLS certificate chain sometimes fails default verification depending on the environment. Disabling verification is necessary for reliability.

## Symbol URL-Encoding

Symbols containing `^` or other special characters must be URL-encoded:

```python
import urllib.parse
encoded = urllib.parse.quote('^GSPC')  # → '%5EGSPC'
url = f'https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=6mo&interval=1d'
```

## Symbol Reference

### Indices
| Symbol | Yahoo Ticker | Notes |
|--------|-------------|-------|
| S&P 500 | `^GSPC` | Broad market benchmark |
| Nasdaq Composite | `^IXIC` | Tech-heavy |
| Dow Jones | `^DJI` | 30 blue chips |
| Russell 2000 | `^RUT` | Small caps |
| VIX | `^VIX` | Volatility index |

### Futures & Commodities
| Symbol | Yahoo Ticker |
|--------|-------------|
| Gold | `GC=F` |
| WTI Oil | `CL=F` |
| Natural Gas | `NG=F` |
| Silver | `SI=F` |
| Copper | `HG=F` |

### Rates & Currencies
| Symbol | Yahoo Ticker |
|--------|-------------|
| 10Y Treasury Yield | `^TNX` |
| 2Y Treasury Yield | `^IRX` |
| Dollar Index | `DX-Y.NYB` |
| EUR/USD | `EURUSD=X` |

### Crypto
| Symbol | Yahoo Ticker |
|--------|-------------|
| Bitcoin | `BTC-USD` |
| Ethereum | `ETH-USD` |

### S&P 500 Sector ETFs
| Sector | ETF |
|--------|-----|
| Technology | `XLK` |
| Healthcare | `XLV` |
| Financials | `XLF` |
| Consumer Discretionary | `XLY` |
| Consumer Staples | `XLP` |
| Energy | `XLE` |
| Industrials | `XLI` |
| Materials | `XLB` |
| Utilities | `XLU` |
| Real Estate | `XLRE` |
| Communication Services | `XLC` |

## Response Structure

```json
{
  "chart": {
    "result": [{
      "meta": {
        "regularMarketPrice": 7472.79,
        "fiftyTwoWeekHigh": 7620.9,
        "fiftyTwoWeekLow": 6059.25,
        "regularMarketVolume": 3673570000,
        "chartPreviousClose": 7500.58
      },
      "timestamp": [1716422400, 1716508800, ...],
      "indicators": {
        "quote": [{
          "close": [7450.0, 7472.79, null, 7500.0],
          "high":  [7480.0, 7530.0, null, 7510.0],
          "low":   [7430.0, 7460.0, null, 7480.0],
          "volume": [3.5e9, 3.7e9, null, 3.2e9],
          "open":  [7440.0, 7500.0, null, 7490.0]
        }]
      }
    }]
  }
}
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Expecting value: line 1 column 1 (char 0)` | Empty response — missing User-Agent | Add `User-Agent: Mozilla/5.0` header |
| HTTP 999 | Rate limited | Add 0.08s sleep between requests |
| `KeyError: 'result'` | Invalid symbol or market closed | Check symbol encoding; verify ticker exists |
| `None` in close array | Market holiday / trading halt | Filter: `[c for c in closes if c is not None]` |
| `IndexError` on closes[-22] | Not enough history | Check `len(closes)` before indexing |

## Deprecated Endpoints

- `/v10/finance/quoteSummary/{symbol}` — No longer returns fundamentals (P/E, market cap, PEG ratio). Use the v8 chart API only for price/OHLCV data. For fundamentals, use Alpha Vantage, Financial Modeling Prep, or SEC EDGAR.