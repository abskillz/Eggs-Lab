"""Turns current holdings + new cash into whole-share buy orders to place in Sahm."""
import math

from . import config


def plan_orders(holdings, prices, new_cash_usd, weights=None, allow_sell=False):
    """holdings: {ticker: shares}; prices: {ticker: USD price}.

    Buys whole shares, filling the most underweight ETF first, so cash leftover is small.
    Sells only when allow_sell is set (selling triggers fees; buying the laggards is usually enough).
    """
    weights = weights or config.TARGET_WEIGHTS
    held = {t: holdings.get(t, 0) for t in weights}
    total = new_cash_usd + sum(held[t] * prices[t] for t in weights)
    orders = {t: 0 for t in weights}

    if allow_sell:
        for t, w in weights.items():
            excess = held[t] * prices[t] - total * w
            if excess > prices[t]:
                n = math.floor(excess / prices[t])
                orders[t] -= n
                new_cash_usd += n * prices[t]

    cash = new_cash_usd
    while True:
        value = {t: (held[t] + orders[t]) * prices[t] for t in weights}
        gaps = {t: total * w - value[t] for t, w in weights.items() if prices[t] <= cash}
        if not gaps:
            break
        t = max(gaps, key=gaps.get)
        orders[t] += 1
        cash -= prices[t]
    return {t: n for t, n in orders.items() if n}, round(cash, 2)
