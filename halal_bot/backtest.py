"""Monthly-contribution backtest. Cash account only: no leverage, no shorting, no interest."""
import numpy as np
import pandas as pd

from . import config


def run_backtest(prices, weights, initial, monthly, trend_filter=False, fee=0.0):
    """Simulate investing `initial` then `monthly` at each month start (in the prices' currency).

    With trend_filter, an ETF's share of money sits in cash while it trades below its moving average.
    Returns a DataFrame with daily portfolio value and total amount contributed.
    """
    prices = prices[list(weights)].dropna()
    ma = prices.rolling(config.TREND_WINDOW, min_periods=1).mean()
    month_starts = set(prices.groupby(prices.index.to_period("M")).head(1).index)

    shares = pd.Series(0.0, index=prices.columns)
    cash, contributed = 0.0, 0.0
    target = pd.Series(weights)
    rows = []
    for i, (day, px) in enumerate(prices.iterrows()):
        if day in month_starts:
            add = initial if contributed == 0 else monthly
            cash += add
            contributed += add
            total = cash + (shares * px).sum()
            active = target.copy()
            if trend_filter:
                active[px < ma.loc[day]] = 0.0
            desired = total * active / px
            current_w = (shares * px) / total
            drift = (current_w - active).abs().max()
            if drift > config.REBALANCE_BAND or i == 0 or trend_filter:
                trade_value = ((desired - shares) * px).abs().sum()
                cash += ((shares - desired) * px).sum() - trade_value * fee
                shares = desired
            else:
                buy = cash * active / active.sum() if active.sum() else active * 0
                shares += buy / px * (1 - fee)
                cash -= buy.sum()
        rows.append((day, cash + (shares * px).sum(), contributed))
    return pd.DataFrame(rows, columns=["date", "value", "contributed"]).set_index("date")


def summarize(result):
    value, contributed = result["value"], result["contributed"]
    years = max((value.index[-1] - value.index[0]).days / 365.25, 1e-9)
    # Drawdown measured on value net of new contributions, so deposits don't hide losses.
    growth = (value / contributed).replace([np.inf, -np.inf], np.nan).dropna()
    drawdown = (growth / growth.cummax() - 1).min()
    return {
        "years": round(years, 1),
        "contributed": round(contributed.iloc[-1], 2),
        "final_value": round(value.iloc[-1], 2),
        "profit": round(value.iloc[-1] - contributed.iloc[-1], 2),
        "return_on_contributions": f"{value.iloc[-1] / contributed.iloc[-1] - 1:.1%}",
        "worst_drawdown": f"{drawdown:.1%}",
    }
