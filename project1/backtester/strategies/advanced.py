import pandas as pd
from .base import Strategy


class RiskAdjustedMomentumStrategy(Strategy):
    """
    New Strategy 1: Risk-Adjusted Momentum.

    Ranks each stock by its Sharpe-like score: trailing return divided by
    rolling volatility over the same window.  Selects the top-K stocks by
    this score and allocates uniformly.

    Unlike pure trailing-return ranking (Benchmark 2), the risk-adjusted
    score penalises stocks that achieved high returns at the cost of extreme
    volatility, leading to a lower-vol portfolio with a higher Sharpe ratio.
    """

    def __init__(self, lookback: int = 30, vol_window: int = 30, top_k: int = 10):
        self.lookback = lookback
        self.vol_window = vol_window
        self.top_k = top_k

    def generate_weights(self, prices: pd.DataFrame, current_date=None) -> dict:
        if len(prices) < max(self.lookback + 1, self.vol_window + 1):
            return {}
        ret = (prices.iloc[-1] / prices.iloc[-self.lookback - 1] - 1).dropna()
        vol = prices.pct_change(fill_method=None).iloc[-self.vol_window:].std().dropna()
        common = ret.index.intersection(vol.index)
        if common.empty:
            return {}
        score = ret[common] / vol[common]
        top = list(score.nlargest(self.top_k).index)
        w = 1.0 / len(top)
        return {t: w for t in top}

    def __repr__(self):
        return (f"RiskAdjustedMomentum(lookback={self.lookback}, "
                f"vol_window={self.vol_window}, top_k={self.top_k})")


class RegimeFilteredMomentumStrategy(Strategy):
    """
    New Strategy 2: Market-Regime Filtered Risk-Adjusted Momentum.

    Adds a market-regime gate on top of the risk-adjusted momentum signal:
    if fewer than `bull_threshold` of stocks are trading above their
    `regime_window`-day SMA, the portfolio holds all cash (defensive mode).

    When the regime is bullish, selects top-K stocks by risk-adjusted
    momentum score and weights them by inverse volatility.

    The regime filter substantially reduces drawdown during sustained
    downturns (e.g., 2022 Nasdaq bear market) while retaining the
    full upside of momentum in bull markets, boosting the Sharpe ratio.
    """

    def __init__(self, lookback: int = 30, vol_window: int = 30, top_k: int = 10,
                 regime_window: int = 100, bull_threshold: float = 0.4):
        self.lookback = lookback
        self.vol_window = vol_window
        self.top_k = top_k
        self.regime_window = regime_window
        self.bull_threshold = bull_threshold

    def generate_weights(self, prices: pd.DataFrame, current_date=None) -> dict:
        min_len = max(self.lookback + 1, self.vol_window + 1, self.regime_window)
        if len(prices) < min_len:
            return {}

        current = prices.iloc[-1]
        sma = prices.iloc[-self.regime_window:].mean()
        valid = [t for t in prices.columns
                 if not pd.isna(current[t]) and not pd.isna(sma[t])]
        if not valid:
            return {}
        bull_frac = sum(current[t] > sma[t] for t in valid) / len(valid)
        if bull_frac < self.bull_threshold:
            return {}  # Defensive: hold cash

        ret = (prices.iloc[-1] / prices.iloc[-self.lookback - 1] - 1).dropna()
        vol = prices.pct_change(fill_method=None).iloc[-self.vol_window:].std().dropna()
        common = ret.index.intersection(vol.index)
        if common.empty:
            return {}
        score = ret[common] / vol[common]
        top = list(score.nlargest(self.top_k).index)

        vol_top = vol[top]
        vol_top = vol_top[vol_top > 0].dropna()
        if vol_top.empty:
            w = 1.0 / len(top)
            return {t: w for t in top}
        total = sum(1.0 / v for v in vol_top.values)
        return {t: (1.0 / vol_top[t]) / total for t in vol_top.index}

    def __repr__(self):
        return (f"RegimeFilteredMomentum(lookback={self.lookback}, top_k={self.top_k}, "
                f"regime_window={self.regime_window}, bull_threshold={self.bull_threshold})")


# Backward-compat aliases
MultiFactorStrategy = RiskAdjustedMomentumStrategy
TrendRiskParityStrategy = RegimeFilteredMomentumStrategy
