# Halal US-Stock Investing Bot

Helps you invest in Sharia-compliant US ETFs through **Sahm** (no leverage, no shorting, no interest).
Sahm has no trading API, so the bot tells you what to buy and you place the orders in the app (about 2 minutes a month).

## Setup (once)
```bash
pip install -r requirements.txt
```

## 1. Test the strategy on past prices
```bash
python -m halal_bot backtest --initial-sar 5000 --monthly-sar 500 --start 2020-01-01
```
Compares plain buy-and-hold with a 200-day trend filter, which moves to cash during downtrends.

## 2. Each month: what to buy
```bash
python -m halal_bot plan --cash-sar 5000 --save
```
Prints whole-share orders (e.g. `BUY 22 x SPUS`). `--save` records them in `holdings.json`
(only use it after you've actually placed the orders). Next month, run it again with your new cash.
It buys whatever is most underweight, so the portfolio stays balanced without selling.

## 3. Optional: screen individual stocks
```bash
python -m halal_bot screen AAPL MSFT NVDA JPM
```
Checks AAOIFI ratios (debt, cash and receivables vs. market cap) and the company's business activity.
It can't check interest income, so confirm with **Sahm's Halal Screening** before buying.

## Portfolio (edit `halal_bot/config.py`)
| ETF | Weight | What it is |
|---|---|---|
| SPUS | 50% | S&P 500 Sharia-screened |
| HLAL | 20% | FTSE USA Shariah |
| UMMA | 15% | Islamic world stocks outside US |
| SPSK | 15% | Global sukuk (steadier) |

## Notes
- Purify dividends: give away the impermissible share (Sahm shows purification rates).
- This is not financial or religious advice. Markets can fall 30%+; only invest money you won't need for years.
