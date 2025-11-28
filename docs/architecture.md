# ROS2 Testbed Architecture: Control Plane + Data Plane

## Overview
This ROS2 testbed implements a **hybrid distributed coordination architecture** with:
- **Control Plane:** ZooKeeper-style task coordination (strong consistency)
- **Data Plane:** Gossip-based DSM for state sharing (eventual consistency)

## Architecture Comparison

| Component | Warehouse Simulation | ROS2 Testbed | Notes |
|:---|:---|:---|:---|
| **Control Plane** | `coord/` (in-process) | `coord` package (ROS2 services) | ZooKeeper-style leases |
| **Data Plane** | `dsm/` (in-process gossip) | `dsm` package (ROS2 topics) | CRDT-based state sharing |
| **Agents** | `world/agent.py` | `agent` package | Task execution logic |

## Package Structure

```
ros2_testbed/src/
├── coord/              # Control Plane (NEW)
│   ├── coord/
│   │   ├── coordinator.py       # ZooKeeper-style coordinator
│   │   ├── lease_manager.py     # TTL-based leases
│   │   ├── task_registry.py     # Authoritative task state
│   │   └── coord_node.py        # ROS2 service wrapper
│   ├── package.xml
│   └── setup.py
├── dsm/                # Data Plane
│   └── dsm/
│       └── dsm_node.py          # Gossip protocol
├── agent/              # Task Execution
│   └── agent/
│       └── agent_node.py        # Agent logic
├── interfaces/         # ROS2 Messages & Services
│   ├── msg/
│   │   ├── TaskInfo.msg         # Task information
│   │   ├── AgentState.msg
│   │   └── DSMUpdate.msg
│   └── srv/
│       ├── GetAvailableTasks.srv
│       ├── ClaimTask.srv
│       ├── CompleteTask.srv
│       └── CreateTask.srv
├── common/             # Shared utilities
│   └── common/
│       └── graph.py
└── launch/             # Launch files
    └── launch/
        └── testbed.launch.py
```

## Communication Patterns

### Control Plane (ROS2 Services - Strong Consistency)
- **Services Provided by Coordinator:**
  - `/coord/get_available_tasks` → List available tasks
  - `/coord/claim_task` → Atomic task claim with lease
  - `/coord/complete_task` → Mark task complete + release lease
  - `/coord/create_task` → Create new task

### Data Plane (ROS2 Topics - Eventual Consistency)
- **Topics:**
  - `/dsm_gossip` → Publish/Subscribe for state updates
  - `/agent_state` → Agent location/status broadcasts

## Deployment on Multiple Jetsons

### Architecture
```
Jetson #1 (device_id=1):
├── Coordinator Node (provides services)
├── DSM Node (gossips with other devices)
└── Agents 10, 11 (call coordinator services)

Jetson #2 (device_id=2):
├── Coordinator Node (provides services)
├── DSM Node (gossips with other devices)
└── Agents 20, 21 (call coordinator services)
```

### Launch Commands

**On Jetson #1:**
```bash
ros2 launch launch testbed.launch.py device_id:=1
```

**On Jetson #2:**
```bash
ros2 launch launch testbed.launch.py device_id:=2
```

## Key Design Decisions

### Why ZooKeeper-Style Control Plane?

**Benefits:**
1. **Strong Consistency:** No two agents claim the same task
2. **Atomic Operations:** Lease acquisition is Compare-And-Swap
3. **TTL-based Expiration:** Failed agents automatically release tasks
4. **Proven Pattern:** Industry-standard approach (used by ZooKeeper, etcd, Consul)

**Trade-offs:**
- Coordinator is a bottleneck (but only for task claims, not state updates)
- Single point of failure per device (can be replicated later)

### Why Gossip-Based Data Plane?

**Benefits:**
1. **Scalability:** No central bottleneck for state updates
2. **Partition Tolerance:** Agents continue working during network splits
3. **Low Latency:** Local reads, no coordinator roundtrip
4. **CRDT Guarantees:** Eventual consistency with conflict resolution

**Trade-offs:**
- Stale reads possible (bounded by gossip frequency)
- Higher complexity (CRDT merge logic)

## Comparison to Open-RMF

| Aspect | Open-RMF | This Testbed |
|:---|:---|:---|
| **Task Coordination** | Centralized Fleet Manager | ZooKeeper-style distributed leases |
| **State Sharing** | Centralized database | Gossip + CRDTs |
| **Consistency** | Strong (all via central) | Hybrid (strong for tasks, eventual for state) |
| **Scalability** | Limited by central bottleneck | Higher (distributed state) |
| **Research Goal** | Production system | Test if gossip reduces overhead |

## Next Steps

1. ✅ Implement Control Plane (Coordinator + Services)
2. ✅ Update launch files
3. ⬜ Update AgentNode to call Coordinator services
4. ⬜ Test on two Jetsons
5. ⬜ Implement leader election for Coordinator (future work)
6. ⬜ Implement actual task generation logic

## Future: Full ZooKeeper Replication

Currently each device runs its own Coordinator (no replication). To make it truly fault-tolerant:

```python
# Future: Replicated Coordinator with leader election
coordinator = DistributedCoordinator(
    peers=['jetson1:5000', 'jetson2:5000'],
    consensus_protocol='raft'  # or 'zab'
)
```

This would allow:
- Automatic failover if coordinator crashes
- Multiple coordinators with leader election
- True ZooKeeper-style distributed consensus

---

**Summary:** This testbed implements the warehouse simulation's hybrid architecture on real hardware, enabling experimental validation of distributed coordination patterns for multi-robot systems.

