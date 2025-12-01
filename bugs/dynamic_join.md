# LF RTI Dynamic Join/Leave Limitation

## Problem
LF RTI with **centralized coordination** does NOT support late-joining federates by design.

**Why:**
- Fixed topology at compile time (number of federates baked in)
- TAG (Time Advance Grant) protocol assumes all federates participate from time 0
- Designed for HPC clusters and fixed cyber-physical systems, NOT dynamic fleets

## Solutions:

### Option 1: Accept Limitation (Simplest)
- Restart RTI when any federate restarts
- Fine for lab/research environments

### Option 2: Switch to Decentralized Coordination
**Change in `coordinator.lf`:**
```lf
target Python {
  coordination: decentralized,  // Was: centralized
  ...
}
```
**Benefits:**
- No RTI needed - federates communicate peer-to-peer
- Better fault tolerance, no single point of failure
- Potentially better dynamic join/leave support

**Trade-offs:**
- Uses STP (safe-to-process) delays instead of TAG
- May have slightly weaker ordering guarantees
- Requires testing to verify determinism is maintained

### Option 3: Federate Pool (Moderate Effort)

**Architecture:**
```
Central System (Always Running)
├─ RTI
└─ Federate Pool (always connected)
   ├─ Fed1 (slot 1) ──┐
   ├─ Fed2 (slot 2)   ├─ ROS 2 Services
   ├─ Fed3 (slot 3)   │  (claim, complete)
   └─ Fed4 (slot 4) ──┘
         ↓
   Robots (dynamic)
   ├─ Robot 1 (Jetson) → registers for slot 1
   ├─ Robot 2 (Jetson) → registers for slot 2
   └─ Robot N (Jetson) → can join/leave freely
```

**How it works:**
- Run 4-8 "slot" federates always connected to RTI
- Robots register for slots dynamically via ROS 2 (`/pool/register`)
- Pool routes robot requests through assigned slots
- When robot leaves, slot becomes available for another robot

**Benefits:** Keeps LF determinism, allows dynamic membership
**Drawbacks:** Limited to pool size, extra network hop

### Option 4: Hybrid with Fallback
- Use LF when available for strong consistency
- Fall back to ROS 2 coordination when LF unavailable
- Best of both worlds for production

## Recommendation

**Try Option 2 first** (decentralized coordination) - one line change, potentially solves the problem.

If decentralized mode doesn't provide strong enough guarantees, then implement Option 3 (federate pool) for production deployments.