# Routing and Order Batching

## The Vehicle Routing Problem (VRP)

When a rider carries multiple orders (batch delivery), the platform must decide:
1. Which orders to group together
2. In what sequence to pick up and deliver them

This is a variant of the Vehicle Routing Problem (VRP), specifically:
- **VRPTW**: VRP with Time Windows (each delivery has a deadline)
- **PDPTW**: Pickup and Delivery with Time Windows (rider must pick up before delivering)

VRP is NP-hard. Exact solutions only tractable for <20 stops.

## Batching Decision

Should order A and order B be batched?

Key trade-off:
- Benefit: one rider trip instead of two → lower cost per delivery
- Cost: longer delivery time for both customers (especially the first-delivered order)

Typical batching criteria:
- Orders within the same geographic zone
- Restaurants within X meters of each other
- Estimated added delivery time < threshold (e.g., < 8 minutes)

## Route Optimization Heuristics

**Nearest-Neighbor Heuristic**: always go to the closest unvisited stop.
Simple, fast, ~20-25% above optimal.

**2-opt / 3-opt**: iteratively swap pairs of route edges if the swap improves total distance.
Local search, commonly used in practice.

**Christofides Algorithm**: guarantees 1.5x optimal for TSP (no time windows).
Not directly applicable with time windows.

**Google OR-Tools**: open-source library widely used in industry for VRP.
Uses constraint programming + local search metaheuristics.

## Dynamic Re-routing

Routes aren't fixed — new orders or traffic updates trigger re-optimization.
Meituan re-solves routing for each rider every time a new order arrives in their zone.

Challenge: balancing computation time vs route quality.
Typical constraint: re-routing must complete in < 200ms.

## Stacked Orders

Uber Eats "stacked orders": a rider picks up order 2 while delivering order 1
(if restaurant 2 is on the way). Enabled by ETA prediction models.

## Estimated Time of Arrival (ETA) Prediction

Core ML problem: predict how long a delivery will take.
Features:
- Distance (straight-line and road-network)
- Time of day / day of week
- Historical travel speeds on road segments
- Restaurant historical prep times
- Current weather

Models used: gradient boosting (XGBoost, LightGBM), deep learning on road graphs (GNN).

ETA error directly affects matching quality — wrong ETA leads to suboptimal assignments.
