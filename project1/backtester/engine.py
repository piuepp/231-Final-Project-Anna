import logging
import pandas as pd
import numpy as np
from .strategies.base import Strategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Daily close backtesting engine.

    On each trading day the engine:
      1. Calls strategy.generate_weights(prices_up_to_today) to get target weights.
      2. Rebalances the portfolio to those weights at today's closing price.
      3. Records the portfolio NAV, weights, and daily return.

    No short selling (weights >= 0), no leverage (sum of weights <= 1).
    Transaction costs are applied as a flat fraction of traded notional.
    """

    def __init__(self, prices: pd.DataFrame, strategy: Strategy,
                 initial_capital: float = 1_000_000.0,
                 transaction_cost: float = 0.0,
                 warmup: int = 0):
        self.prices = prices
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.transaction_cost = transaction_cost
        self.warmup = warmup

    def run(self) -> pd.DataFrame:
        prices = self.prices
        dates = prices.index
        tickers = list(prices.columns)

        cash = self.initial_capital
        holdings: dict[str, float] = {t: 0.0 for t in tickers}

        records = []

        for i, date in enumerate(dates):
            if i < self.warmup:
                nav = cash + sum(holdings[t] * prices.loc[date, t]
                                 for t in tickers if not np.isnan(prices.loc[date, t]))
                records.append({"date": date, "nav": nav, "cash": cash})
                continue

            prices_so_far = prices.iloc[: i + 1]
            raw_weights = self.strategy.generate_weights(prices_so_far, date)

            # Enforce constraints
            target_weights = {t: max(0.0, w) for t, w in raw_weights.items()}
            total = sum(target_weights.values())
            if total > 1.0:
                target_weights = {t: w / total for t, w in target_weights.items()}

            # Current NAV at today's close
            nav = cash
            for t in tickers:
                price = prices.loc[date, t]
                if not np.isnan(price):
                    nav += holdings[t] * price

            # Compute target dollar positions
            target_value = {t: target_weights.get(t, 0.0) * nav for t in tickers}

            # Execute trades
            total_turnover = 0.0
            for t in tickers:
                price = prices.loc[date, t]
                if np.isnan(price):
                    continue
                current_value = holdings[t] * price
                delta_value = target_value[t] - current_value
                shares_delta = delta_value / price
                holdings[t] += shares_delta
                cash -= delta_value
                total_turnover += abs(delta_value)

            # Deduct transaction costs
            cost = total_turnover * self.transaction_cost
            cash -= cost

            # Recompute NAV after trades
            nav = cash
            for t in tickers:
                price = prices.loc[date, t]
                if not np.isnan(price):
                    nav += holdings[t] * price

            records.append({"date": date, "nav": nav, "cash": cash,
                            "turnover": total_turnover, "cost": cost})

            if i % 100 == 0:
                logger.debug(f"{date.date()}  NAV={nav:,.0f}  cash={cash:,.0f}")

        result = pd.DataFrame(records).set_index("date")
        return result
