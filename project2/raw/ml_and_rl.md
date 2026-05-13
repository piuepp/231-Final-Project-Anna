# Machine Learning and Reinforcement Learning in Dispatch

## Why ML?

Classical optimization (IP, VRP solvers) works well for a single snapshot in time
but struggles with:
- Uncertainty (traffic, prep times, demand)
- Long-horizon decisions (pre-positioning riders for future demand)
- Scale (real-time decisions for millions of orders)

ML approaches learn to handle uncertainty from historical data.

## Demand Forecasting

**Goal**: predict how many orders will arrive in each zone in the next 15/30/60 minutes.

**Features**: time of day, day of week, weather, local events, historical patterns.

**Models**: LSTM / Transformer (time series), gradient boosting (tabular features).

Used for: pre-positioning idle riders ("go to zone X, we expect demand there in 20 min").

## Supply-Demand Balancing

If too many riders are in one zone and too few in another:
- Short-term: incentive payments to move riders (surge bonus)
- Medium-term: targeted rider acquisition in high-demand areas

ML models predict where imbalances will occur, allowing proactive adjustments.

## Reinforcement Learning for Dispatch

### Setup
- **State**: current positions of all riders, pending orders, predicted demand
- **Action**: matching decisions (which rider to which order)
- **Reward**: delivery time, rider utilization, customer satisfaction

### Approaches

**DiDi (ride-hailing, closely related)**: published RL-based dispatch (KDD 2018).
Uses deep Q-network (DQN) to learn order-dispatching policies. Orders per driver
increased by ~16% in simulation.

**Meituan**: uses a two-stage system — fast greedy matching for immediate orders,
RL for pre-positioning and zone-level decisions.

**Challenges with RL**:
- Credit assignment: a bad delivery time might be due to assignment 10 minutes ago
- Non-stationarity: rider/customer behavior changes over time
- Safety: can't fully explore in production (bad assignments hurt real customers)

## Graph Neural Networks (GNN) in Dispatch

Model the city as a road graph. GNNs can:
- Learn road segment travel speeds from historical GPS data
- Embed spatial relationships between restaurants, customers, riders
- Enable joint optimization over the full graph

Emerging research direction; few production deployments confirmed publicly.

## Fairness and Rider Welfare

ML-driven dispatch optimizes platform metrics, but can lead to:
- Unequal income distribution among riders
- Overworking high-rated riders
- Geographic discrimination (poor areas get slower delivery)

Active research area: constrained optimization with fairness objectives.
