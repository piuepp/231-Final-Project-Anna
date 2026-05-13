# Food Delivery Dispatch: An Overview

## What is Dispatch?

Dispatch is the real-time process of deciding which courier (rider) should be assigned
to which order, and in what sequence. It runs continuously — typically every few seconds —
as new orders arrive and riders become available.

The core challenge: match orders to riders under hard time constraints (customers expect
food in 30-45 minutes), uncertain travel times (traffic), and dynamic supply/demand
(dinner rush vs. 3am).

## Three Sub-Problems

1. **Order-Rider Matching**: which rider takes which order?
2. **Route Sequencing**: if a rider carries multiple orders (batching), in what order
   should they pick up and deliver?
3. **Zone Management**: how should the platform pre-position idle riders to meet
   predicted demand?

## Why It's Hard

- Scale: Uber Eats, Meituan, DoorDash each handle millions of orders per day.
- Real-time: assignment decisions must be made in milliseconds.
- Stochasticity: restaurant prep times, traffic, rider behavior are all uncertain.
- Multi-objective: minimize delivery time, maximize rider utilization, minimize platform cost.

## Industry Players

- **Meituan** (China): largest by volume, pioneered AI-based dispatch at scale.
- **Uber Eats** (global): uses marketplace dynamics and surge pricing.
- **DoorDash** (US): known for Dasher (rider) scheduling optimization.
- **Grab** (Southeast Asia): multi-modal dispatch (food + ride-hailing).

## Key Metrics

- ETA accuracy (predicted vs actual delivery time)
- Order completion rate
- Rider utilization rate
- Customer satisfaction / rating
