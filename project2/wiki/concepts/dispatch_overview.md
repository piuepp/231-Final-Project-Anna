summary: The core problem of real-time order-to-rider assignment in food delivery platforms.

# Food Delivery Dispatch: Overview

Dispatch is the real-time engine that connects customers, restaurants, and riders.
Every few seconds, the platform must answer: *which rider should take which order,
and how should that rider travel to complete it?*

## The Three Sub-Problems

Dispatch is not a single problem but a pipeline of three tightly coupled decisions:

### 1. Order-Rider Matching
Decide which available rider takes which pending order. This is a [[Bipartite Matching]]
problem solved repeatedly in real time. Criteria include proximity, rider workload,
and predicted [[ETA Prediction|delivery time]].

### 2. Route Sequencing
When a rider carries multiple orders ([[Order Batching]]), the platform must determine
the optimal pickup-and-delivery sequence. This is a variant of the
[[Vehicle Routing Problem]] (VRPTW — with time windows).

### 3. Zone Management and Pre-positioning
Idle riders must be strategically placed *before* demand spikes hit.
This requires [[Demand Forecasting]] to predict where and when orders will arrive.

## Why Dispatch Is Hard

- **Scale**: Platforms like Meituan handle over 50 million orders per day.
- **Real-time constraint**: matching decisions must complete in under a few hundred milliseconds.
- **Uncertainty**: restaurant prep times, road traffic, and rider behavior are all stochastic.
- **Multi-objective trade-offs**: fast delivery vs. low cost vs. rider fairness.

## Industry Context

| Platform | Region | Notable Approach |
|---|---|---|
| Meituan | China | Batch matching every 3s; RL for pre-positioning |
| Uber Eats | Global | Marketplace dynamics; stacked orders |
| DoorDash | US | Dasher scheduling optimization |
| Grab | Southeast Asia | Multi-modal (food + ride-hailing) |

## Key Performance Metrics

- **ETA accuracy**: how close is the predicted delivery time to the actual?
- **Order completion rate**: fraction of orders successfully delivered.
- **Rider utilization**: fraction of rider time spent actively delivering (not idle).
- **Customer rating**: downstream satisfaction signal.

## See Also
- [[Bipartite Matching]]
- [[Vehicle Routing Problem]]
- [[Demand Forecasting]]
- [[Reinforcement Learning for Dispatch]]
- [[ETA Prediction]]
