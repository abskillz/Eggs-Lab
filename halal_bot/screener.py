"""AAOIFI-style Sharia screen for individual US stocks.

Yahoo data does not show interest income, so the impermissible-income test (< 5% of revenue)
is not covered here. Always confirm with Sahm's Halal Screening before buying.
"""
from . import config


def screen_fundamentals(info, balance):
    """Return (passed, reasons) given a yfinance-style info dict and balance-sheet values."""
    reasons = []
    industry = f"{info.get('sector', '')} {info.get('industry', '')}".lower()
    for word in config.EXCLUDED_INDUSTRY_KEYWORDS:
        if word in industry:
            reasons.append(f"business activity: {industry.strip()}")
            break

    mcap = info.get("marketCap") or 0
    if mcap <= 0:
        return False, reasons + ["no market cap data"]

    checks = [
        ("debt", balance.get("debt", 0), config.MAX_DEBT_TO_MCAP),
        ("cash & interest-bearing securities", balance.get("cash", 0), config.MAX_CASH_TO_MCAP),
        ("receivables", balance.get("receivables", 0), config.MAX_RECEIVABLES_TO_MCAP),
    ]
    for name, value, limit in checks:
        ratio = (value or 0) / mcap
        if ratio > limit:
            reasons.append(f"{name}/market cap {ratio:.0%} > {limit:.0%}")
    return not reasons, reasons


def _latest(sheet, *rows):
    for row in rows:
        if row in sheet.index:
            value = sheet.loc[row].dropna()
            if len(value):
                return float(value.iloc[0])
    return 0.0


def screen_ticker(ticker):
    import yfinance as yf

    t = yf.Ticker(ticker)
    bs = t.balance_sheet
    balance = {
        "debt": _latest(bs, "Total Debt"),
        "cash": _latest(bs, "Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"),
        "receivables": _latest(bs, "Receivables", "Accounts Receivable"),
    }
    return screen_fundamentals(t.info, balance)
