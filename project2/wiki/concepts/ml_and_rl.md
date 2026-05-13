summary: How demand forecasting, reinforcement learning, and GNNs are applied to modern dispatch systems.

# Machine Learning and Reinforcement Learning in Dispatch

Classical optimization handles a single snapshot well but struggles with uncertainty
and long-horizon decisions. ML approaches learn to handle both from historical data.

## Demand Forecasting

**Goal**: predict how many orders will arrive in each geographic zone over the
next 15, 30, or 60 minutes.

**Why it matters**: accurate forecasts allow the platform to pre-position idle riders
*before* demand spikes, reducing wait times for customers and idle time for riders.

**Features**: time of day, day of week, weather, local events, historical order patterns.

**Models**: LSTMs and Transformers for time-series patterns; gradient boosting for
tabular feature interactions.

## Supply-Demand Balancing

When too many riders cluster in one zone and too few cover another:
- **Short-term**: push notifications + bonus payments incentivize riders to relocate.
- **Medium-term**: targeted rider recruitment campaigns in persistently underserved areas.

ML predicts where imbalances will occur, enabling proactive rather than reactive responses.

## Reinforcement Learning for Dispatch

### Problem Formulation
- **State**: positions of all riders, pending orders, current ETA estimates, predicted demand map.
- **Action**: matching decisions (which rider ← which order) or pre-positioning commands.
- **Reward**: delivery time reduction, rider utilization, customer satisfaction score.

### Industry Examples

**DiDi (KDD 2018)**: published RL-based order dispatching for ride-hailing.
Uses a deep Q-network (DQN). Reported ~16% improvement in orders-per-driver in simulation.
Directly influenced food delivery dispatch research.

**Meituan**: two-stage system — fast [[Bipartite Matching]] for immediate order assignment,
RL for zone-level pre-positioning of idle riders.

### Challenges

| Challenge | Description |
|---|---|
| Credit assignment | A late delivery may be caused by a bad assignment decision made 15 minutes earlier |
| Non-stationarity | Rider and customer behavior shifts across hours, seasons, and city growth |
| Safety | Cannot fully explore in production — bad assignments hurt real customers |
| Scale | City-wide state space is enormous; approximations required |

## Graph Neural Networks (GNNs)

Food delivery naturally maps onto graphs: restaurants, customers, and riders are nodes;
road segments are edges.

**Applications**:
- Learning travel-time embeddings from GPS traces (better [[ETA Prediction]])
- Encoding spatial context for matching decisions
- Joint optimization across the full road network

GNNs for dispatch are an active research area; few confirmed production deployments.

## Fairness and Rider Welfare

ML-optimized dispatch maximizes platform-level metrics but can create side effects:
- Income inequality: top-rated riders receive more orders, earning more than others.
- Overwork: high-utilization riders may be pushed beyond healthy working hours.
- Geographic bias: less profitable zones receive slower or less reliable service.

Active research area: constrained optimization with explicit fairness objectives
(e.g., Gini coefficient on rider income as a constraint).

## See Also
- [[Demand Forecasting]]
- [[Bipartite Matching]]
- [[ETA Prediction]]
- [[Dispatch Overview]]
- [[Vehicle Routing Problem]]
