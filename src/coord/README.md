# ROS 2 Testbed: Two Coordination Modes

This testbed supports **two modes** for the Control Plane:

## Mode 1: ZooKeeper-Style (Standard ROS 2)
- **File:** `coord_node.py`
- **Architecture:** Each Jetson runs independent coordinator
- **Consistency:** Best-effort (nondeterministic)
- **Use Case:** Standard distributed robotics

### Run:
```bash
ros2 launch launch testbed.launch.py device_id:=1 mode:=zookeeper
```

## Mode 2: Lingua Franca Federated (Deterministic)
- **File:** `lf/Coordinator.lf`
- **Architecture:** RTI + Federated coordinators
- **Consistency:** Deterministic (strong logical time ordering)
- **Use Case:** Research on deterministic coordination

### Setup:
```bash
# 1. Build LF program
cd src/coord
./scripts/build_lf.sh

# 2. Start RTI (on one machine or external server)
./lf/src-gen/Coordinator/bin/RTI

# 3. On Jetson 1:
ros2 launch launch testbed.launch.py device_id:=1 mode:=lf

# 4. On Jetson 2:
ros2 launch launch testbed.launch.py device_id:=2 mode:=lf
```

## Architecture Comparison

| Aspect | ZooKeeper Mode | LF Federated Mode |
|:---|:---|:---|
| **Determinism** | No (network/scheduling dependent) | Yes (logical time ordering) |
| **Reproducibility** | Low | High (exact replay possible) |
| **Fault Tolerance** | Manual failover | RTI crash stops system |
| **Complexity** | Low (standard ROS 2) | Medium (requires LF compiler) |
| **Research Value** | Baseline | Novel contribution |

## How LF Federation Works

```
RTI (Logical Time Coordinator)
    ↓ synchronizes
Fed1 (Jetson 1) ←→ Fed2 (Jetson 2)
    ↓                   ↓
ROS Bridge          ROS Bridge
    ↓                   ↓
Agents 10,11        Agents 20,21
```

### Key Guarantee:
If Agent 10 and Agent 20 both claim Task A at nearly the same time:
- **ZooKeeper Mode:** Winner depends on network latency (random)
- **LF Mode:** Winner determined by logical time ordering (deterministic)

## Files

### ZooKeeper Mode:
- `coord/coordinator.py` - Core logic
- `coord/coord_node.py` - ROS 2 wrapper

### LF Mode:
- `lf/Coordinator.lf` - Federated reactor
- `coord/lf_bridge_node.py` - ROS 2 to LF bridge
- `scripts/build_lf.sh` - Build script

## Research Impact

Using LF federation allows you to claim:
> "We implemented a warehouse coordination system with **deterministic distributed task allocation**, enabling exact reproducibility of multi-robot experiments across physical hardware."

This is a significant advantage over standard ROS 2 approaches.

