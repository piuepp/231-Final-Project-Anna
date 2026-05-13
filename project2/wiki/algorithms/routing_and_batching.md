summary: Vehicle routing, order batching, and ETA prediction for multi-stop deliveries.

# Routing and Order Batching

Once orders are assigned to riders, the platform must determine *how* each rider
travels — especially when carrying multiple orders simultaneously.

## The Vehicle Routing Problem (VRP)

When a rider handles several orders, the system faces a variant of the
[[Vehicle Routing Problem]]:

- **VRPTW** (with Time Windows): each delivery has a deadline.
- **PDPTW** (Pickup and Delivery with Time Windows): rider must visit the restaurant
  *before* the customer address.

VRP is NP-hard. Exact solvers are practical only for very small instances (<20 stops);
heuristics are used in production.

## Order Batching

Should orders A and B be bundled into a single rider trip?

**Benefits**: fewer total trips → lower cost per delivery, higher rider utilization.
**Cost**: the second-delivered customer waits longer.

Typical batching criteria:
- Restaurants within X meters of each other
- Customer addresses in the same geographic zone
- Estimated added delivery time below a threshold (e.g., < 8 minutes)

Batching is a revenue/experience trade-off that platforms tune carefully.

## Route Optimization Heuristics

### Nearest-Neighbor
Always travel to the closest unvisited stop. Simple and fast; ~20–25% above optimal.

### 2-opt / 3-opt
Iteratively swap pairs of route edges if the swap reduces total distance.
Classic local-search method. Runs in milliseconds for typical delivery routes (3–5 stops).

### Google OR-Tools
Open-source library combining constraint programming with metaheuristic local search.
Widely used in industry for production-grade VRP solving.

## Dynamic Re-routing

Routes are not fixed. When a new order arrives or traffic changes, the platform
re-optimizes affected riders' routes in real time.

**Constraint**: re-routing must complete in < 200ms to avoid delaying other decisions.

## Stacked Orders (Uber Eats)

A rider picks up a second order *while* delivering the first, if the second restaurant
is conveniently on the way. Enabled entirely by accurate [[ETA Prediction]].

## ETA Prediction

**The core ML problem underlying all routing and matching decisions.**

If ETA estimates are wrong, assignments are made on incorrect cost estimates,
leading to late deliveries.

**Typical features**:
- Straight-line and road-network distance
- Time of day, day of week
- Historical travel speeds on road segments (from GPS traces)
- Restaurant historical prep time distributions
- Current weather and traffic conditions

**Models used**: LightGBM / XGBoost for tabular features; GNNs for road-graph embeddings.

ETA models are typically retrained daily or weekly on fresh GPS data.

## See Also
- [[Bipartite Matching]]
- [[Order Batching]]
- [[Dispatch Overview]]
- [[ML and Reinforcement Learning]]
- [[ETA Prediction]]
