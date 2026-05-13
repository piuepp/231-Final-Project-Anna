import numpy as np
import pandas as pd
from .base import Strategy


class MomentumStrategy(Strategy):
    """Buy when price is above its N-day moving average, else hold cash."""

    def __init__(self, ticker: str, window: int = 20):
        self.ticker = ticker
        self.window = window

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        series = prices[self.ticker].dropna()
        if len(series) < self.window:
            return {self.ticker: 0.0}
        ma = series.iloc[-self.window:].mean()
        weight = 1.0 if series.iloc[-1] > ma else 0.0
        return {self.ticker: weight}

    def __repr__(self):
        return f"Momentum(ticker={self.ticker}, window={self.window})"


class MeanReversionStrategy(Strategy):
    """
    Buy when price is more than `z_threshold` std below its rolling mean,
    sell (go to cash) when price is above the rolling mean.
    Uses a z-score computed over `window` days.
    """

    def __init__(self, ticker: str, window: int = 20, z_threshold: float = 1.0):
        self.ticker = ticker
        self.window = window
        self.z_threshold = z_threshold
        self._in_position = False

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        series = prices[self.ticker].dropna()
        if len(series) < self.window:
            return {self.ticker: 0.0}
        window_prices = series.iloc[-self.window:]
        mean = window_prices.mean()
        std = window_prices.std()
        if std == 0:
            return {self.ticker: 0.0}
        z = (series.iloc[-1] - mean) / std
        if z < -self.z_threshold:
            self._in_position = True
        elif z > 0:
            self._in_position = False
        return {self.ticker: 1.0 if self._in_position else 0.0}

    def __repr__(self):
        return f"MeanReversion(ticker={self.ticker}, window={self.window}, z={self.z_threshold})"


class RSIStrategy(Strategy):
    """
    Mean-reversion via RSI: buy when RSI < oversold, sell when RSI > overbought.
    Default thresholds: oversold=30, overbought=70.
    """

    def __init__(self, ticker: str, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.ticker = ticker
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        self._in_position = False

    def _rsi(self, series: pd.Series) -> float:
        delta = series.diff().dropna()
        gain = delta.clip(lower=0).rolling(self.period).mean()
        loss = (-delta.clip(upper=0)).rolling(self.period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - 100 / (1 + rs)
        return rsi.iloc[-1]

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        series = prices[self.ticker].dropna()
        if len(series) < self.period + 1:
            return {self.ticker: 0.0}
        rsi = self._rsi(series)
        if np.isnan(rsi):
            return {self.ticker: 0.0}
        if rsi < self.oversold:
            self._in_position = True
        elif rsi > self.overbought:
            self._in_position = False
        return {self.ticker: 1.0 if self._in_position else 0.0}

    def __repr__(self):
        return f"RSI(ticker={self.ticker}, period={self.period}, oversold={self.oversold}, overbought={self.overbought})"


class BollingerBandStrategy(Strategy):
    """
    Buy when price crosses below the lower Bollinger Band,
    sell when price crosses above the middle band (SMA).
    """

    def __init__(self, ticker: str, window: int = 20, n_std: float = 2.0):
        self.ticker = ticker
        self.window = window
        self.n_std = n_std
        self._in_position = False

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        series = prices[self.ticker].dropna()
        if len(series) < self.window:
            return {self.ticker: 0.0}
        window_prices = series.iloc[-self.window:]
        mid = window_prices.mean()
        std = window_prices.std()
        lower = mid - self.n_std * std
        current_price = series.iloc[-1]
        if current_price < lower:
            self._in_position = True
        elif current_price > mid:
            self._in_position = False
        return {self.ticker: 1.0 if self._in_position else 0.0}

    def __repr__(self):
        return f"BollingerBand(ticker={self.ticker}, window={self.window}, n_std={self.n_std})"


class MACDStrategy(Strategy):
    """
    MACD crossover momentum: buy when MACD line crosses above signal line,
    sell when it crosses below.
    Standard parameters: fast=12, slow=26, signal=9.
    """

    def __init__(self, ticker: str, fast: int = 12, slow: int = 26, signal: int = 9):
        self.ticker = ticker
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self._in_position = False

    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        series = prices[self.ticker].dropna()
        min_len = self.slow + self.signal
        if len(series) < min_len:
            return {self.ticker: 0.0}
        ema_fast = series.ewm(span=self.fast, adjust=False).mean()
        ema_slow = series.ewm(span=self.slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal, adjust=False).mean()
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            self._in_position = True
        else:
            self._in_position = False
        return {self.ticker: 1.0 if self._in_position else 0.0}

    def __repr__(self):
        return f"MACD(ticker={self.ticker}, fast={self.fast}, slow={self.slow}, signal={self.signal})"
