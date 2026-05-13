# Order-Rider Matching Algorithms

## Greedy Matching

The simplest approach: for each new order, assign it to the nearest available rider.
Fast (O(n)), but globally suboptimal — greedy choices can create conflicts.

**Variants:**
- Nearest-idle rider
- Nearest rider with lowest current workload
- Nearest rider with highest ETA confidence

## Bipartite Matching

Model the problem as a bipartite graph:
- Left nodes: unassigned orders
- Right nodes: available riders
- Edge weight: estimated delivery time (or cost)

Goal: find a minimum-weight perfect matching.

**Hungarian Algorithm**: solves optimal bipartite matching in O(n^3). Used for small
batches (< a few hundred pairs). Classic academic solution.

**Auction Algorithm**: a market-inspired alternative where orders "bid" for riders.
Converges faster in practice for dense graphs.

## Batch Matching with Time Windows

Instead of matching instantly, accumulate orders for a short window (e.g., 3-5 seconds)
and solve a batch matching problem. This enables globally better assignments at the cost
of slight delay.

Meituan's approach (published 2021): batch matching every 3 seconds over a city-wide graph.

## Integer Programming Formulation

Variables: x_{ij} ∈ {0,1}, x_{ij}=1 if rider i is assigned to order j.

Objective: minimize sum_{ij} c_{ij} * x_{ij}
Subject to:
  - Each order assigned to at most one rider
  - Each rider assigned to at most one order (or at most K orders if batching)
  - Feasibility constraints (time windows, capacity)

Exact IP is NP-hard for large instances; approximation algorithms or LP relaxation used.

## Online vs Offline

- **Offline**: all orders known in advance. Theoretically optimal but not realistic.
- **Online**: orders arrive sequentially. Competitive ratio measures how well online
  algorithms perform relative to offline optimum.
  Competitive ratio of simple greedy ≈ 0.5 in worst case.

## Practical Considerations

- Rider location is GPS-estimated and has error.
- Travel time depends on traffic (time of day, weather, events).
- Restaurants have variable prep times — matching too early wastes rider time waiting.
