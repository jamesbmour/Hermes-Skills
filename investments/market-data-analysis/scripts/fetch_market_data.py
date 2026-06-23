#!/usr/bin/env python3
"""
Fetch S&P 500 market data from Yahoo Finance API and calculate technical indicators.
Outputs JSON with all stocks, sorted by momentum, RSI, and proximity to 52-week extremes.

Usage:
    python fetch_market_data.py [--output /tmp/market_data.json] [--range 6mo]
"""

import urllib.request
import urllib.parse
import json
import ssl
import time
import argparse
import sys

# SSL context (Yahoo certs sometimes fail default verification)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# S&P 500 stock universe by sector
STOCK_UNIVERSE = [
    # Tech
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'AVGO', 'ORCL', 'CRM', 'AMD', 'ADBE',
    'INTC', 'CSCO', 'TXN', 'QCOM', 'IBM',
    # Healthcare
    'UNH', 'LLY', 'JNJ', 'ABBV', 'MRK', 'PFE', 'TMO', 'ABT', 'DHR', 'BMY',
    'AMGN', 'GILD', 'CI', 'HUM', 'VEEV',
    # Financials
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'V',
    'MA', 'CB', 'AIG', 'MET', 'PRU',
    # Consumer Discretionary
    'AMZN', 'TSLA', 'HD', 'MCD', 'NIKE', 'LOW', 'SBUX', 'BKNG', 'TJX', 'GM',
    'F', 'ABNB', 'CMG',
    # Consumer Staples
    'WMT', 'PG', 'KO', 'PEP', 'COST', 'MDLZ', 'CL', 'KMB', 'STZ', 'MO', 'TGT',
    # Energy
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'MPC', 'VLO', 'OXY', 'PXD',
    # Industrials
    'CAT', 'UNP', 'RTX', 'GE', 'BA', 'DE', 'HON', 'UPS', 'LMT', 'MMM', 'FDX', 'EMR',
    # Materials
    'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'DOW', 'DD',
    # Utilities
    'NEE', 'SO', 'DUK', 'AEP', 'EXC', 'SRE',
    # Real Estate
    'PLD', 'AMT', 'EQIX', 'SPG', 'O', 'WELL',
    # Comm Services
    'NFLX', 'DIS', 'CMCSA', 'T', 'VZ', 'TMUS',
]

# Macro indicators
MACRO_SYMBOLS = {
    'SP500': '^GSPC', 'VIX': '^VIX', 'Nasdaq': '^IXIC', 'Dow': '^DJI',
    'Russell2000': '^RUT', 'Gold': 'GC=F', 'Oil': 'CL=F',
    '10Y_Treasury': '^TNX', 'Dollar': 'DX-Y.NYB', 'Bitcoin': 'BTC-USD',
}

# Sector ETFs
SECTOR_ETFS = {
    'Tech': 'XLK', 'Healthcare': 'XLV', 'Financials': 'XLF',
    'ConsDisc': 'XLY', 'ConsStaples': 'XLP', 'Energy': 'XLE',
    'Industrials': 'XLI', 'Materials': 'XLB', 'Utilities': 'XLU',
    'RealEstate': 'XLRE', 'CommServices': 'XLC',
}


def fetch_chart(symbol, range_str='6mo', interval='1d'):
    """Fetch chart data from Yahoo Finance API."""
    encoded = urllib.parse.quote(symbol)
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range={range_str}&interval={interval}'
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=10) as resp:
        return json.loads(resp.read())


def calc_rsi(closes, period=14):
    """Calculate RSI from closes array (oldest→newest)."""
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, period + 1):
        change = closes[-i] - closes[-i-1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)


def calc_sma(closes, period):
    """Calculate Simple Moving Average."""
    if len(closes) < period:
        return None
    return round(sum(closes[-period:]) / period, 2)


def calc_returns(current, closes):
    """Calculate 1D, 1W, 1M, 3M returns."""
    def pct(idx):
        if len(closes) < idx + 1:
            return None
        return round((current / closes[-idx - 1] - 1) * 100, 2)
    return pct(1), pct(5), pct(21), pct(63)


def analyze_stock(symbol, range_str='6mo'):
    """Fetch and analyze a single stock."""
    try:
        data = fetch_chart(symbol, range_str)
        result = data['chart']['result'][0]
        meta = result['meta']
        quotes = result['indicators']['quote'][0]

        closes = [c for c in quotes.get('close', []) if c is not None]
        volumes = [v for v in quotes.get('volume', []) if v is not None]

        current = meta.get('regularMarketPrice')
        high52 = meta.get('fiftyTwoWeekHigh')
        low52 = meta.get('fiftyTwoWeekLow')

        rsi = calc_rsi(closes)
        sma20 = calc_sma(closes, 20)
        sma50 = calc_sma(closes, 50)

        day, week, month, three_m = calc_returns(current, closes)

        # Volume ratio
        vol_recent = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else None
        vol_avg = sum(volumes[-50:]) / 50 if len(volumes) >= 50 else (sum(volumes) / len(volumes) if volumes else None)
        vol_ratio = round(vol_recent / vol_avg, 2) if vol_recent and vol_avg else None

        dist_high = round((current / high52 - 1) * 100, 2) if high52 else None
        dist_low = round((current / low52 - 1) * 100, 2) if low52 else None
        vs_sma50 = round((current / sma50 - 1) * 100, 2) if sma50 else None

        return {
            'symbol': symbol, 'price': round(current, 2),
            'rsi_14': rsi, 'sma20': sma20, 'sma50': sma50,
            'price_vs_sma50': vs_sma50,
            'day_pct': day, 'week_pct': week, 'month_pct': month, '3month_pct': three_m,
            '52w_high': high52, '52w_low': low52,
            'dist_from_high_pct': dist_high, 'dist_from_low_pct': dist_low,
            'vol_ratio': vol_ratio,
        }
    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}


def fetch_macro():
    """Fetch macro indicators."""
    results = {}
    for name, sym in MACRO_SYMBOLS.items():
        try:
            data = fetch_chart(sym, '5d')
            meta = data['chart']['result'][0]['meta']
            results[name] = {
                'price': meta.get('regularMarketPrice'),
                'prev_close': meta.get('chartPreviousClose'),
                '52w_high': meta.get('fiftyTwoWeekHigh'),
                '52w_low': meta.get('fiftyTwoWeekLow'),
            }
        except Exception as e:
            results[name] = f'Error: {e}'
        time.sleep(0.08)
    return results


def fetch_sectors():
    """Fetch sector ETF performance."""
    results = {}
    for name, etf in SECTOR_ETFS.items():
        try:
            data = fetch_chart(etf, '1mo')
            result = data['chart']['result'][0]
            meta = result['meta']
            quotes = result['indicators']['quote'][0]
            closes = [c for c in quotes.get('close', []) if c is not None]
            current = meta.get('regularMarketPrice')
            month_ago = closes[0] if closes else None
            pct = round((current / month_ago - 1) * 100, 2) if month_ago else None
            results[name] = {
                'etf': etf, 'price': current, '1m_pct': pct,
                '52w_high': meta.get('fiftyTwoWeekHigh'),
                '52w_low': meta.get('fiftyTwoWeekLow'),
            }
        except Exception as e:
            results[name] = f'Error: {e}'
        time.sleep(0.08)
    return results


def screen_buys(stocks):
    """Screen for buy candidates."""
    # Momentum breakouts: near 52H, above SMA50, RSI 50-70
    momentum = sorted(
        [s for s in stocks
         if s.get('dist_from_high_pct') is not None and s['dist_from_high_pct'] > -5
         and s.get('price_vs_sma50') is not None and s['price_vs_sma50'] > 0
         and s.get('rsi_14') is not None and 50 <= s['rsi_14'] <= 70],
        key=lambda x: x.get('3month_pct', 0), reverse=True
    )
    # Oversold: RSI < 35
    oversold = sorted(
        [s for s in stocks if s.get('rsi_14') is not None and s['rsi_14'] < 35],
        key=lambda x: x['rsi_14']
    )
    return momentum[:5], oversold[:5]


def screen_sells(stocks):
    """Screen for sell/short candidates."""
    # Overbought: RSI > 72
    overbought = sorted(
        [s for s in stocks if s.get('rsi_14') is not None and s['rsi_14'] > 72],
        key=lambda x: x['rsi_14'], reverse=True
    )
    # Structural decline: below SMA50, near 52L, negative momentum
    decliners = sorted(
        [s for s in stocks
         if s.get('dist_from_low_pct') is not None and s['dist_from_low_pct'] < 10
         and s.get('price_vs_sma50') is not None and s['price_vs_sma50'] < 0],
        key=lambda x: x.get('3month_pct', 0)
    )
    return overbought[:5], decliners[:5]


def main():
    parser = argparse.ArgumentParser(description='Fetch S&P 500 market data and screen for opportunities')
    parser.add_argument('--output', '-o', default='/tmp/market_data.json', help='Output JSON file path')
    parser.add_argument('--range', '-r', default='6mo', help='Data range (1mo, 3mo, 6mo, 1y)')
    args = parser.parse_args()

    print('Fetching macro indicators...')
    macro = fetch_macro()
    for name, data in macro.items():
        if isinstance(data, dict):
            print(f'  {name}: {data["price"]}')

    print('\nFetching sector ETFs...')
    sectors = fetch_sectors()
    for name, data in sorted(sectors.items(), key=lambda x: x[1].get('1m_pct', -999) if isinstance(x[1], dict) else -999, reverse=True):
        if isinstance(data, dict):
            print(f'  {name} ({data["etf"]}): {data["1m_pct"]:+.2f}% (1M)')

    print(f'\nFetching {len(STOCK_UNIVERSE)} stocks...')
    all_stocks = []
    errors = []
    for sym in STOCK_UNIVERSE:
        result = analyze_stock(sym, args.range)
        if 'error' not in result:
            all_stocks.append(result)
        else:
            errors.append((sym, result['error']))
        time.sleep(0.08)

    print(f'  Success: {len(all_stocks)}, Errors: {len(errors)}')
    if errors:
        for sym, err in errors[:5]:
            print(f'    {sym}: {err[:80]}')

    # Screen
    buy_momentum, buy_oversold = screen_buys(all_stocks)
    sell_overbought, sell_decliners = screen_sells(all_stocks)

    print('\n=== BUY CANDIDATES (Momentum) ===')
    for s in buy_momentum:
        print(f'  {s["symbol"]}: ${s["price"]} | RSI: {s["rsi_14"]} | 3M: {s["3month_pct"]:+.1f}% | % from 52H: {s["dist_from_high_pct"]:+.1f}%')

    print('\n=== BUY CANDIDATES (Oversold) ===')
    for s in buy_oversold:
        print(f'  {s["symbol"]}: ${s["price"]} | RSI: {s["rsi_14"]} | 1M: {s["month_pct"]:+.1f}% | % from 52H: {s["dist_from_high_pct"]:+.1f}%')

    print('\n=== SELL CANDIDATES (Overbought) ===')
    for s in sell_overbought:
        print(f'  {s["symbol"]}: ${s["price"]} | RSI: {s["rsi_14"]} | 1M: {s["month_pct"]:+.1f}% | % from 52H: {s["dist_from_high_pct"]:+.1f}%')

    print('\n=== SELL CANDIDATES (Downtrend) ===')
    for s in sell_decliners:
        print(f'  {s["symbol"]}: ${s["price"]} | RSI: {s["rsi_14"]} | 3M: {s["3month_pct"]:+.1f}% | % from 52L: {s["dist_from_low_pct"]:+.1f}%')

    # Save full data
    output = {
        'macro': macro,
        'sectors': sectors,
        'stocks': all_stocks,
        'screening': {
            'buy_momentum': buy_momentum,
            'buy_oversold': buy_oversold,
            'sell_overbought': sell_overbought,
            'sell_decliners': sell_decliners,
        }
    }
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f'\nFull data saved to {args.output}')


if __name__ == '__main__':
    main()