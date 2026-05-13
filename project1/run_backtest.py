"""
Entry point for running all backtesting experiments.

Usage:
    python run_backtest.py

Outputs saved to ./results/
"""

import os
import logging
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backtester.data import DataLoader
from backtester.engine import BacktestEngine
from backtester import metrics
from backtester.strategies import (
    MomentumStrategy,
    MeanReversionStrategy,
    RSIStrategy,
    BollingerBandStrategy,
    MACDStrategy,
    SMAcrossoverStrategy,
    TrailingReturnStrategy,
    RiskAdjustedMomentumStrategy,
    RegimeFilteredMomentumStrategy,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DATA_PATH = "nasdaq100_daily_5y.csv"
RESULTS_DIR = "results"
INITIAL_CAPITAL = 1_000_000.0
SINGLE_STOCK = "NVDA"

os.makedirs(RESULTS_DIR, exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────

def run_strategy(prices, strategy, initial_capital=INITIAL_CAPITAL):
    engine = BacktestEngine(prices, strategy, initial_capital=initial_capital)
    result = engine.run()
    return result["nav"]


def metrics_table(nav_dict: dict) -> pd.DataFrame:
    rows = []
    for name, nav in nav_dict.items():
        m = metrics.compute_all(nav)
        m["Strategy"] = name
        rows.append(m)
    df = pd.DataFrame(rows).set_index("Strategy")
    return df


def plot_nav(nav_dict: dict, title: str, filename: str):
    fig, ax = plt.subplots(figsize=(12, 5))
    for name, nav in nav_dict.items():
        (nav / nav.iloc[0]).plot(ax=ax, label=name)
    ax.set_title(title)
    ax.set_ylabel("Normalized NAV (base=1)")
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, filename)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved plot: {path}")


def log_and_save(df: pd.DataFrame, title: str, filename: str):
    path = os.path.join(RESULTS_DIR, filename)
    df.to_csv(path)
    print(f"\n{'='*60}")
    print(title)
    print('='*60)
    print(df.to_string())
    logger.info(f"Saved metrics: {path}")


# ── Deliverable 3: Single Stock ───────────────────────────────────────────────

def run_single_stock(loader: DataLoader):
    logger.info(f"=== Deliverable 3: Single Stock ({SINGLE_STOCK}) ===")
    prices = loader.get_prices([SINGLE_STOCK])

    strategies = {
        "Momentum(20)": MomentumStrategy(SINGLE_STOCK, window=20),
        "Momentum(50)": MomentumStrategy(SINGLE_STOCK, window=50),
        "MeanReversion(20,z=1)": MeanReversionStrategy(SINGLE_STOCK, window=20, z_threshold=1.0),
        "RSI(14,30/70)": RSIStrategy(SINGLE_STOCK, period=14, oversold=30, overbought=70),
        "BollingerBand(20,2σ)": BollingerBandStrategy(SINGLE_STOCK, window=20, n_std=2.0),
        "MACD(12,26,9)": MACDStrategy(SINGLE_STOCK, fast=12, slow=26, signal=9),
    }

    nav_dict = {}
    for name, strat in strategies.items():
        logger.info(f"  Running {name}...")
        nav_dict[name] = run_strategy(prices, strat)

    table = metrics_table(nav_dict)
    log_and_save(table, f"Deliverable 3: Single Stock ({SINGLE_STOCK})", "d3_single_stock_metrics.csv")
    plot_nav(nav_dict, f"Single Stock Strategies — {SINGLE_STOCK}", "d3_single_stock_nav.png")


# ── Deliverable 4: Portfolio Backtesting ──────────────────────────────────────

def run_portfolio(loader: DataLoader):
    logger.info("=== Deliverable 4: Portfolio Backtesting ===")
    prices = loader.get_prices()

    strategies = {
        "SMAcross_Uniform": SMAcrossoverStrategy(short_window=20, long_window=50, weighting="uniform"),
        "SMAcross_RiskAdj": SMAcrossoverStrategy(short_window=20, long_window=50, weighting="risk_adjusted"),
        "TrailingRet_Uniform": TrailingReturnStrategy(lookback=30, top_k=10, weighting="uniform"),
        "TrailingRet_RiskAdj": TrailingReturnStrategy(lookback=30, top_k=10, weighting="risk_adjusted"),
    }

    nav_dict = {}
    for name, strat in strategies.items():
        logger.info(f"  Running {name}...")
        nav_dict[name] = run_strategy(prices, strat)

    table = metrics_table(nav_dict)
    log_and_save(table, "Deliverable 4: Portfolio Backtesting", "d4_portfolio_metrics.csv")
    plot_nav(nav_dict, "Portfolio Strategies — All Nasdaq-100", "d4_portfolio_nav.png")


# ── Deliverable 5: Beat Benchmarks ───────────────────────────────────────────

def run_beat_benchmark(loader: DataLoader):
    logger.info("=== Deliverable 5: Beat Benchmark Strategies ===")
    prices = loader.get_prices()

    strategies = {
        "Benchmark1_SMAcross": SMAcrossoverStrategy(short_window=20, long_window=50, weighting="uniform"),
        "Benchmark2_TrailingRet": TrailingReturnStrategy(lookback=30, top_k=10, weighting="uniform"),
        "New1_RiskAdjMomentum": RiskAdjustedMomentumStrategy(lookback=30, vol_window=30, top_k=10),
        "New2_RegimeMomentum": RegimeFilteredMomentumStrategy(lookback=30, vol_window=30, top_k=10, regime_window=100, bull_threshold=0.4),
    }

    nav_dict = {}
    for name, strat in strategies.items():
        logger.info(f"  Running {name}...")
        nav_dict[name] = run_strategy(prices, strat)

    table = metrics_table(nav_dict)
    log_and_save(table, "Deliverable 5: Beat Benchmark Strategies", "d5_benchmark_metrics.csv")
    plot_nav(nav_dict, "New vs Benchmark Strategies — All Nasdaq-100", "d5_benchmark_nav.png")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Loading data...")
    loader = DataLoader(DATA_PATH)
    logger.info(f"Loaded {len(loader.tickers)} tickers, {len(loader.dates)} trading days "
                f"({loader.dates[0].date()} to {loader.dates[-1].date()})")

    run_single_stock(loader)
    run_portfolio(loader)
    run_beat_benchmark(loader)

    logger.info("All experiments complete. Results saved to ./results/")
