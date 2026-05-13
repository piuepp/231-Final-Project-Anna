import numpy as np
import pandas as pd
from .base import Strategy


def _uniform_weights(selected: list) -> dict:
    if not selected:
        return {}
    w = 1.0 / len(selected)
    return {t: w for t in selected}


def _risk_adjusted_weights(selected: list, vol_series: pd.Series) -> dict:
    if not selected:
        return {}
    inv_vol = {t: 1.0 / vol_series[t] for t in selected if vol_series[t] > 0}
    if not inv_vol:
        return _uniform_weights(selected)
    total = sum(inv_vol.values())
    return {t: v / total for t, v in inv_vol.items()}


class SMAcrossoverStrategy(Strategy):
    """
    Benchmark 1: select stocks where SMA(short) > SMA(long), allocate uniformly.
    Optionally use risk-adjusted weighting.
    """

    def __init__(self, short_window: int = 20, long_window: int = 50,
                 weighting: str = "uniform", vol_window: int = 20):
        self.short_window = short_window
        self.long_window = long_window
        self.weighting = weighting
        self.vol_window = vol_window

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        if len(prices) < self.long_window:
            return {}
        short_ma = prices.iloc[-self.short_window:].mean()
        long_ma = prices.iloc[-self.long_window:].mean()
        selected = [t for t in prices.columns if short_ma[t] > long_ma[t]]
        if self.weighting == "risk_adjusted":
            returns = prices.pct_change().iloc[-self.vol_window:]
            vol = returns.std()
            return _risk_adjusted_weights(selected, vol)
        return _uniform_weights(selected)

    def __repr__(self):
        return f"SMAcrossover(short={self.short_window}, long={self.long_window}, weighting={self.weighting})"


class TrailingReturnStrategy(Strategy):
    """
    Benchmark 2: select top-K stocks by trailing return over `lookback` days,
    allocate uniformly. Optionally use risk-adjusted weighting.
    """

    def __init__(self, lookback: int = 30, top_k: int = 10,
                 weighting: str = "uniform", vol_window: int = 20):
        self.lookback = lookback
        self.top_k = top_k
        self.weighting = weighting
        self.vol_window = vol_window

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        if len(prices) < self.lookback + 1:
            return {}
        trailing_ret = prices.iloc[-1] / prices.iloc[-self.lookback - 1] - 1
        trailing_ret = trailing_ret.dropna()
        selected = list(trailing_ret.nlargest(self.top_k).index)
        if self.weighting == "risk_adjusted":
            returns = prices.pct_change().iloc[-self.vol_window:]
            vol = returns.std()
            return _risk_adjusted_weights(selected, vol)
        return _uniform_weights(selected)

    def __repr__(self):
        return f"TrailingReturn(lookback={self.lookback}, top_k={self.top_k}, weighting={self.weighting})"


class UniformPortfolioStrategy(Strategy):
    """
    Wraps any signal function with uniform weighting.
    The signal_fn receives prices DataFrame and returns a list of selected tickers.
    """

    def __init__(self, signal_fn, name: str = "UniformPortfolio"):
        self.signal_fn = signal_fn
        self._name = name

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        selected = self.signal_fn(prices)
        return _uniform_weights(selected)

    def __repr__(self):
        return self._name


class RiskAdjustedPortfolioStrategy(Strategy):
    """
    Wraps any signal function with risk-adjusted (inverse-vol) weighting.
    """

    def __init__(self, signal_fn, vol_window: int = 20, name: str = "RiskAdjustedPortfolio"):
        self.signal_fn = signal_fn
        self.vol_window = vol_window
        self._name = name

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        selected = self.signal_fn(prices)
        if not selected:
            return {}
        returns = prices.pct_change().iloc[-self.vol_window:]
        vol = returns.std()
        return _risk_adjusted_weights(selected, vol)

    def __repr__(self):
        return self._name
