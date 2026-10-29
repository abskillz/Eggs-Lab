"""Command line entry point. Run `python -m halal_bot --help`."""
import argparse
import json
from pathlib import Path

from . import config


def cmd_backtest(args):
    from .backtest import run_backtest, summarize
    from .data import load_prices

    prices = load_prices(list(config.TARGET_WEIGHTS), start=args.start)
    initial = args.initial_sar * config.USD_PER_SAR
    monthly = args.monthly_sar * config.USD_PER_SAR
    for label, trend in [("Buy & hold + rebalance", False), ("With 200-day trend filter", True)]:
        s = summarize(run_backtest(prices, config.TARGET_WEIGHTS, initial, monthly, trend, fee=args.fee))
        print(f"\n== {label} (SAR) ==")
        for k, v in s.items():
            if k in ("contributed", "final_value", "profit"):
                v = f"{v / config.USD_PER_SAR:,.0f}"
            print(f"  {k:24} {v}")
    print("\nPast results do not guarantee future returns.")


def cmd_plan(args):
    from .data import load_prices

    path = Path(args.holdings)
    holdings = json.loads(path.read_text()) if path.exists() else {}
    last = load_prices(list(config.TARGET_WEIGHTS), start="2024-01-01").iloc[-1]
    prices = {t: float(last[t]) for t in config.TARGET_WEIGHTS}
    from .planner import plan_orders

    orders, leftover = plan_orders(holdings, prices, args.cash_sar * config.USD_PER_SAR, allow_sell=args.allow_sell)
    print("Place these orders in Sahm (market or limit near the price shown):")
    for t, n in orders.items():
        side = "BUY" if n > 0 else "SELL"
        print(f"  {side} {abs(n):>4} x {t:5} @ ~${prices[t]:.2f}  (~{abs(n) * prices[t] / config.USD_PER_SAR:,.0f} SAR)")
    print(f"Leftover cash: ~{leftover / config.USD_PER_SAR:,.0f} SAR")
    if args.save:
        for t, n in orders.items():
            holdings[t] = holdings.get(t, 0) + n
        path.write_text(json.dumps(holdings, indent=2))
        print(f"Saved new holdings to {path}")


def cmd_screen(args):
    from .screener import screen_ticker

    for t in args.tickers:
        try:
            ok, reasons = screen_ticker(t.upper())
        except Exception as e:  # network or missing data
            print(f"{t.upper():6} ERROR  {e}")
            continue
        print(f"{t.upper():6} {'PASS' if ok else 'FAIL'}  {'; '.join(reasons)}")
    print("\nInterest-income test not covered: confirm in Sahm's Halal Screening.")


def main():
    p = argparse.ArgumentParser(prog="halal_bot")
    sub = p.add_subparsers(required=True)

    b = sub.add_parser("backtest", help="test the strategy on past prices")
    b.add_argument("--initial-sar", type=float, default=5000)
    b.add_argument("--monthly-sar", type=float, default=500)
    b.add_argument("--start", default="2020-01-01")
    b.add_argument("--fee", type=float, default=0.001, help="cost per trade as a fraction")
    b.set_defaults(func=cmd_backtest)

    pl = sub.add_parser("plan", help="what to buy this month")
    pl.add_argument("--cash-sar", type=float, required=True)
    pl.add_argument("--holdings", default="holdings.json")
    pl.add_argument("--allow-sell", action="store_true")
    pl.add_argument("--save", action="store_true", help="record the orders as executed")
    pl.set_defaults(func=cmd_plan)

    s = sub.add_parser("screen", help="Sharia-screen individual stocks")
    s.add_argument("tickers", nargs="+")
    s.set_defaults(func=cmd_screen)

    args = p.parse_args()
    args.func(args)
