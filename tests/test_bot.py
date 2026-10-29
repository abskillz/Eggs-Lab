import numpy as np
import pandas as pd

from halal_bot.backtest import run_backtest, summarize
from halal_bot.planner import plan_orders
from halal_bot.screener import screen_fundamentals

W = {"A": 0.6, "B": 0.4}


def fake_prices(days=600):
    idx = pd.bdate_range("2022-01-03", periods=days)
    rng = np.random.default_rng(0)
    return pd.DataFrame(
        {"A": 100 * np.exp(np.cumsum(rng.normal(0.0004, 0.01, days))),
         "B": 50 * np.exp(np.cumsum(rng.normal(0.0002, 0.005, days)))},
        index=idx,
    )


def test_backtest_contributions_and_no_negative_cash():
    res = run_backtest(fake_prices(), W, initial=1000, monthly=100)
    months = fake_prices().index.to_period("M").nunique()
    assert res["contributed"].iloc[-1] == 1000 + 100 * (months - 1)
    assert (res["value"] > 0).all()
    assert set(summarize(res)) >= {"final_value", "worst_drawdown"}


def test_flat_prices_preserve_money():
    p = pd.DataFrame({"A": 10.0, "B": 20.0}, index=pd.bdate_range("2023-01-02", periods=100))
    res = run_backtest(p, W, initial=1000, monthly=100)
    assert np.isclose(res["value"].iloc[-1], res["contributed"].iloc[-1])


def test_trend_filter_goes_to_cash_in_downtrend():
    idx = pd.bdate_range("2023-01-02", periods=300)
    p = pd.DataFrame({"A": np.linspace(100, 40, 300), "B": np.linspace(50, 20, 300)}, index=idx)
    filtered = run_backtest(p, W, 1000, 0, trend_filter=True)["value"].iloc[-1]
    plain = run_backtest(p, W, 1000, 0)["value"].iloc[-1]
    assert filtered > plain


def test_plan_buys_whole_shares_within_cash():
    orders, left = plan_orders({}, {"A": 30.0, "B": 25.0}, 1000, weights=W)
    spent = orders.get("A", 0) * 30 + orders.get("B", 0) * 25
    assert spent + left == 1000 and 0 <= left < 25
    assert orders["A"] * 30 > orders["B"] * 25


def test_plan_tops_up_underweight():
    orders, _ = plan_orders({"A": 100}, {"A": 10.0, "B": 10.0}, 200, weights=W)
    assert orders == {"B": 20}


def test_screen_rules():
    ok, _ = screen_fundamentals({"marketCap": 1000, "sector": "Technology", "industry": "Software"},
                                {"debt": 100, "cash": 50, "receivables": 50})
    assert ok
    ok, reasons = screen_fundamentals({"marketCap": 1000, "sector": "Financial Services", "industry": "Banks - Regional"},
                                      {"debt": 500})
    assert not ok and len(reasons) == 2
