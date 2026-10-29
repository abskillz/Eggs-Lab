"""Price download. Needs internet access to Yahoo Finance."""
import pandas as pd


def load_prices(tickers, start="2020-01-01"):
    """Daily adjusted close prices, one column per ticker."""
    import yfinance as yf

    df = yf.download(list(tickers), start=start, auto_adjust=True, progress=False)["Close"]
    if isinstance(df, pd.Series):
        df = df.to_frame(tickers[0])
    return df.dropna(how="all").ffill()
