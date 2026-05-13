summary: Bipartite matching, Hungarian algorithm, and batch matching methods for order-rider assignment.

# Order-Rider Matching Algorithms

Matching is the heart of dispatch: given a set of pending orders and available riders,
find the best assignment. The problem is formally a weighted [[Bipartite Matching]] task.

## Greedy Matching

The simplest baseline: assign each new order to the nearest available rider immediately.

- **Time complexity**: O(n) per order
- **Quality**: fast but globally suboptimal — greedy choices create conflicts
- **Use case**: acceptable when order volume is low or latency budget is very tight

## Bipartite Matching

Model the problem as a bipartite graph:
- Left nodes: unassigned orders
- Right nodes: available riders
- Edge weight: estimated delivery cost (typically predicted [[ETA Prediction|delivery time]])

**Goal**: minimum-weight perfect matching.

### Hungarian Algorithm
The classical exact solution to bipartite matching.
- Time complexity: O(n³)
- Practical for batches up to a few hundred order-rider pairs
- Produces the globally optimal assignment for a static snapshot

### Auction Algorithm
A market-inspired alternative: orders iteratively "bid" for riders.
Converges faster than Hungarian for dense, large graphs.
Better suited to real-time incremental updates.

## Batch Matching with Time Windows

Rather than matching each order the moment it arrives, the platform accumulates
orders for a short window (typically 3–5 seconds) and solves a single batch problem.

**Benefits**: globally better assignments, enables [[Order Batching]]
**Cost**: introduces a small delay before assignment

Meituan's published system (2021) runs city-wide batch matching every 3 seconds
and reports significant improvements in both delivery time and rider utilization
compared to greedy baselines.

## Integer Programming Formulation

Let $x_{ij} \in \{0,1\}$ equal 1 if rider $i$ is assigned to order $j$.

$$\min \sum_{i,j} c_{ij} x_{ij}$$

Subject to:
- $\sum_j x_{ij} \leq K_i$ for all riders $i$ (capacity constraint, $K_i = 1$ or more if batching)
- $\sum_i x_{ij} = 1$ for all orders $j$ (each order assigned exactly once)
- Feasibility: $x_{ij} = 0$ if assignment is infeasible (time window violated)

Exact IP is NP-hard at scale; LP relaxation or approximation algorithms used in practice.

## Online vs. Offline

- **Offline**: all orders known upfront. Theoretically optimal, not realistic.
- **Online**: orders arrive sequentially. Performance measured by *competitive ratio*
  (online quality ÷ offline optimum). Simple greedy achieves ≈ 0.5 in worst case.

## Practical Challenges

- **GPS error**: rider locations are estimated from noisy GPS signals.
- **Prep time uncertainty**: matching too early means the rider waits at the restaurant.
- **Traffic variability**: edge weights in the matching graph change over time.

## See Also
- [[Vehicle Routing Problem]]
- [[Order Batching]]
- [[ETA Prediction]]
- [[Dispatch Overview]]
- [[Reinforcement Learning for Dispatch]]
