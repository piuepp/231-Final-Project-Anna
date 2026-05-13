import numpy as np
import pandas as pd


TRADING_DAYS = 252


def cumulative_return(nav: pd.Series) -> float:
    return nav.iloc[-1] / nav.iloc[0] - 1


def annualized_return(nav: pd.Series) -> float:
    n_years = len(nav) / TRADING_DAYS
    return (1 + cumulative_return(nav)) ** (1 / n_years) - 1


def annualized_volatility(nav: pd.Series) -> float:
    daily_returns = nav.pct_change().dropna()
    return daily_returns.std() * np.sqrt(TRADING_DAYS)


def sharpe_ratio(nav: pd.Series, risk_free_rate: float = 0.0) -> float:
    ann_ret = annualized_return(nav)
    ann_vol = annualized_volatility(nav)
    if ann_vol == 0:
        return np.nan
    return (ann_ret - risk_free_rate) / ann_vol


def max_drawdown(nav: pd.Series) -> float:
    rolling_max = nav.cummax()
    drawdown = (nav - rolling_max) / rolling_max
    return drawdown.min()


def win_rate(nav: pd.Series) -> float:
    daily_returns = nav.pct_change().dropna()
    return (daily_returns > 0).mean()


def compute_all(nav: pd.Series, risk_free_rate: float = 0.0) -> dict:
    return {
        "Cumulative Return": f"{cumulative_return(nav):.2%}",
        "Annualized Return": f"{annualized_return(nav):.2%}",
        "Annualized Volatility": f"{annualized_volatility(nav):.2%}",
        "Sharpe Ratio": f"{sharpe_ratio(nav, risk_free_rate):.4f}",
        "Max Drawdown": f"{max_drawdown(nav):.2%}",
        "Win Rate": f"{win_rate(nav):.2%}",
    }
