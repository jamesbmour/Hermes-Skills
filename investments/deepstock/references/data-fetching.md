# Data Fetching Recipes for Deep Stock Research

These are the exact, battle-tested commands for fetching and parsing stock data in terminal environments.

---

## Step 1: Yahoo Finance — Price & Technicals

### Fetch

```bash
wget -q -O /tmp/{ticker}.json --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?range=1y&interval=1d"
```

### Parse (Python one-liner in terminal)

```python
python3 -c "
import json
with open('/tmp/{ticker}.json') as f: d=json.load(f)
r=d['chart']['result'][0]; m=r['meta']; q=r['indicators']['quote'][0]
c=[x for x in q['close'] if x is not None]
v=[x for x in q['volume'] if x is not None]
h=[x for x in q['high'] if x is not None]
l=[x for x in q['low'] if x is not None]
# Basic data
print(f'PRICE:{m[\"regularMarketPrice\"]}')
print(f'PREV:{m.get(\"chartPreviousClose\")}')
print(f'52H:{m.get(\"fiftyTwoWeekHigh\")}')
print(f'52L:{m.get(\"fiftyTwoWeekLow\")}')
print(f'CLOSE:{c[-1]}')
print(f'VOL:{v[-1]}')
print(f'AVGVOL50:{sum(v[-50:])//50}')
# Key reference closes
print(f'C-1:{c[-2]}')
print(f'C-6:{c[-6]}')
print(f'C-22:{c[-22]}')
print(f'C-66:{c[-66]}')
# SMAs
for p in [20,50,200]:
    if len(c)>=p: print(f'SMA{p}:{sum(c[-p:])/p:.2f}')
# RSI 14
gains=[]; losses=[]
for i in range(-14,0):
    ch=c[i]-c[i-1]; gains.append(max(ch,0)); losses.append(abs(min(ch,0)))
ag=sum(gains)/14; al=sum(losses)/14
print(f'RSI14:{100-100/(1+ag/al) if al>0 else 100:.1f}')
# MACD
def ema(d,p):
    m=2/(p+1); e=[d[0]]
    for i in range(1,len(d)): e.append(d[i]*m+e[-1]*(1-m))
    return e
e12=ema(c,12); e26=ema(c,26)
mc=[e12[i]-e26[i] for i in range(len(e12))]
sg=ema(mc,9)
print(f'MACD:{mc[-1]:.2f} SIG:{sg[-1]:.2f} HIST:{mc[-1]-sg[-1]:.2f}')
# ATR
trs=[]
for i in range(-14,0): trs.append(max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])))
atr=sum(trs)/14
print(f'ATR:{atr:.2f} ATR%:{atr/c[-1]*100:.2f}')
# Returns
print(f'1D:{(c[-1]/c[-2]-1)*100:.2f}%')
print(f'1W:{(c[-1]/c[-6]-1)*100:.2f}%')
print(f'1M:{(c[-1]/c[-22]-1)*100:.2f}%')
print(f'3M:{(c[-1]/c[-66]-1)*100:.2f}%')
# Day range
print(f'H:{h[-1]} L:{l[-1]}')
"
```

---

## Step 2: Finviz — Fundamentals

### Fetch

```bash
wget -q -O /tmp/{ticker}_finviz.html --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://finviz.com/quote.ashx?t={TICKER}"
```

### Parse

```python
python3 -c "
import re
with open('/tmp/{ticker}_finviz.html') as f: html=f.read()
cells = re.findall(r'snapshot-td2[^>]*>(.*?)</td>', html, re.DOTALL)
vals = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
# Every 2 cells = key (even index) + value (odd index)
for i in range(0, len(vals)-1, 2):
    print(f'{vals[i]}: {vals[i+1]}')
"
```

Key fields in the snapshot (indices may shift slightly):
- 2: P/E — 3: value
- 14: Forward P/E — 15: value
- 26: PEG — 27: value
- 4: EPS (ttm) — 5: value
- 12: Market Cap — 13: value
- 48: Sales — 49: value
- 36: Income — 37: value
- 90: Gross Margin — 91: value
- 102: Oper. Margin — 103: value
- 114: Profit Margin — 115: value
- 66: ROE — 67: value
- 54: ROA — 55: value
- 78: ROIC — 79: value
- 128: Beta — 129: value
- 130: Target Price — 131: value
- 118: Recom (analyst rating) — 119: value
- 134: Debt/Eq — 135: value
- 146: LT Debt/Eq — 147: value
- 110: Quick Ratio — 111: value
- 122: Current Ratio — 123: value
- 116: RSI (14) — 117: value
- 32: Short Float — 33: value
- 44: Short Ratio — 45: value
- 6: Insider Own — 7: value
- 18: Insider Trans — 19: value
- 30: Inst Own — 31: value
- 42: Inst Trans — 43: value
- 74: P/FCF — 75: value
- 148: Earnings (date) — 149: value
- 86: EV/EBITDA — 87: value

---

## Step 3: MarketBeat — Analyst Consensus

### Fetch

```bash
wget -q -O /tmp/{ticker}_analyst.html --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://www.marketbeat.com/stocks/NASDAQ/{TICKER}/price-target/"
```

### Quick parse for price target

```bash
grep -oP 'price target is \$[0-9.]+' /tmp/{ticker}_analyst.html
```

---

## Step 4: Finviz Screener — Peers

### Fetch

```bash
wget -q -O /tmp/peers.html --header="User-Agent: Mozilla/5.0" --timeout=15 \
  "https://finviz.com/screener.ashx?v=111&f=ind_{industry},cap_midover&o=-marketcap&c=0,1,2,6,7,8,9"
```

Replace `{industry}` with the sector/industry filter value (e.g., `applicationsoftware`, `semiconductors`).

### Parse

```python
python3 -c "
import re
with open('/tmp/peers.html') as f: html=f.read()
tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.DOTALL)
for ti, table in enumerate(tables):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
    for ri, row in enumerate(rows):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        texts = []
        for c in cells:
            t = re.sub(r'<[^>]+>', '', c).strip()
            if t: texts.append(t)
        if texts:
            print(f'{\" | \".join(texts[:8])}')
"
```

---

## Troubleshooting

### Empty response from Yahoo Finance
- Missing `--header="User-Agent: Mozilla/5.0"` is the #1 cause
- Rate limiting: add `sleep 0.5` between multiple fetches

### `curl` timing out or blocked
- **Don't use curl.** Use `wget` with `--timeout=15`. It's more reliable in containerized environments.
- `curl | python3` pipes are flagged as HIGH risk by security scanners — always download to file first, then parse.

### Large HTML files
- Finviz pages are ~280KB. Don't try to read them with `read_file` — parse with `python3` in `terminal()` instead.

### Finviz rate limiting
- If you get blocked, wait 30 seconds and retry. Finviz data is 5-15 minutes delayed.
