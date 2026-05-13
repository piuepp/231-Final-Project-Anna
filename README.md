# INDENG 231 Final Project — Anna Chen

Two projects built for INDENG 231. Due May 15, 2026.

---

## Project 1: Backtesting Simulation for Trading Strategies (70%)

A modular backtesting system for daily-close trading strategies on the Nasdaq-100 universe (101 stocks, Apr 2021 – Apr 2026).

### Structure

```
project1/
├── run_backtest.py          # Entry point — run this to reproduce all results
├── requirements.txt
├── nasdaq100_daily_5y.csv   # Raw data
├── results/                 # Output charts and tables (auto-generated)
└── backtester/
    ├── data.py              # DataLoader
    ├── engine.py            # Backtesting engine
    ├── metrics.py           # Sharpe, drawdown, win rate, etc.
    └── strategies/
        ├── base.py          # Abstract Strategy base class
        ├── single_stock.py  # Momentum, Mean Reversion, RSI, Bollinger, MACD
        ├── portfolio.py     # SMA crossover, Trailing return
        └── advanced.py      # Two new strategies (Deliverable 5)
```

### How to Run

```bash
cd project1

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run all experiments
python run_backtest.py
```

Results are saved to `project1/results/` as CSV tables and PNG charts.

### Strategies Tested

| Deliverable | Strategies |
|---|---|
| D3 — Single Stock (NVDA) | Momentum (MA-20, MA-50), Mean Reversion, RSI, Bollinger Band, MACD |
| D4 — Portfolio | SMA Crossover + Trailing Return, each with Uniform & Risk-Adjusted weighting |
| D5 — Beat Benchmarks | Risk-Adjusted Momentum (Sharpe 1.16), Regime-Filtered Momentum (Sharpe 1.16) |

Both new strategies in D5 outperform Benchmark 1 (Sharpe 0.61) and Benchmark 2 (Sharpe 1.01).

### Adding a New Strategy

Subclass `Strategy` and implement one method:

```python
from backtester.strategies.base import Strategy

class MyStrategy(Strategy):
    def generate_weights(self, prices: pd.DataFrame, current_date) -> dict:
        # Return {ticker: weight}, weights in [0,1], sum <= 1
        ...
```

No other changes needed.

---

## Project 2: LLM-Powered Knowledge Base (30%)

A pipeline that uses an LLM to compile raw source documents into a linked markdown wiki, with a Q&A CLI for querying the knowledge base.

**Topic**: Food delivery platform dispatch algorithms (order-rider matching, routing, batching, ML/RL approaches).

### Structure

```
project2/
├── ingest.py        # Compile raw/ sources into wiki via LLM
├── qa.py            # Q&A CLI against the wiki
├── raw/             # Source documents
└── wiki/
    ├── INDEX.md     # Auto-maintained article index
    ├── concepts/    # Overview and ML articles
    └── algorithms/  # Matching, routing, batching articles
```

### How to Run

**Q&A (no API key needed — uses keyword search fallback):**
```bash
cd project2
python qa.py "How does batch matching work?"
python qa.py "How does reinforcement learning apply to dispatch?"
python qa.py "How do platforms pre-position idle riders before demand spikes?"

# Or interactive mode
python qa.py
```

**Ingest new sources (requires Anthropic API key):**
```bash
export ANTHROPIC_API_KEY="your-key-here"
python ingest.py          # process all files in raw/
```

### Wiki Articles

| Article | Summary |
|---|---|
| `concepts/dispatch_overview.md` | The three sub-problems of dispatch and industry landscape |
| `algorithms/matching_algorithms.md` | Greedy, Hungarian, auction, and batch matching |
| `algorithms/routing_and_batching.md` | VRP, order batching trade-offs, ETA prediction |
| `concepts/ml_and_rl.md` | Demand forecasting, RL (DiDi/Meituan), GNNs, fairness |
