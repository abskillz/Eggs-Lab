"""Portfolio settings. Edit these to change what the bot invests in."""

USD_PER_SAR = 1 / 3.75  # SAR is pegged to USD

# Sharia-compliant ETFs listed in the US, with target weights (must sum to 1.0).
TARGET_WEIGHTS = {
    "SPUS": 0.50,  # SP Funds S&P 500 Sharia Industry Exclusions ETF
    "HLAL": 0.20,  # Wahed FTSE USA Shariah ETF
    "UMMA": 0.15,  # Wahed Dow Jones Islamic World ETF (non-US)
    "SPSK": 0.15,  # SP Funds Dow Jones Global Sukuk ETF (sukuk, lower volatility)
}

# Rebalance only when a holding drifts more than this from its target weight.
REBALANCE_BAND = 0.05

# Trend filter: hold an ETF only while its price is above this moving average (in trading days).
TREND_WINDOW = 200

# AAOIFI-style financial screens for individual stocks.
MAX_DEBT_TO_MCAP = 0.30
MAX_CASH_TO_MCAP = 0.30
MAX_RECEIVABLES_TO_MCAP = 0.49

# Business lines that fail the Sharia activity screen.
EXCLUDED_INDUSTRY_KEYWORDS = [
    "bank", "insurance", "credit", "mortgage", "capital markets", "asset management",
    "alcohol", "brewer", "winer", "distiller", "tobacco", "gambling", "casino",
    "resorts & casinos", "adult", "pork", "defense", "entertainment",
]
