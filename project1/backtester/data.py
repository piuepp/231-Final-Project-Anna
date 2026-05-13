import pandas as pd
import numpy as np


class DataLoader:
    def __init__(self, csv_path: str):
        raw = pd.read_csv(csv_path, parse_dates=["date"])
        self.prices = (
            raw.pivot(index="date", columns="ticker", values="close")
            .sort_index()
        )
        self.tickers = list(self.prices.columns)
        self.dates = list(self.prices.index)

    def get_prices(self, tickers=None) -> pd.DataFrame:
        if tickers is None:
            return self.prices
        return self.prices[tickers]

    def get_returns(self, tickers=None) -> pd.DataFrame:
        prices = self.get_prices(tickers)
        return prices.pct_change()
