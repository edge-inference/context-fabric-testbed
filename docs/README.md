# ROS 2 Warehouse Testbed

Multi-device testbed for distributed warehouse robotics research using ROS 2, with support for both standard and deterministic coordination.

## Features

- **Dual Coordination Modes:**
  - **ZooKeeper-Style:** Standard ROS 2 services (nondeterministic)
  - **Lingua Franca Federated:** Deterministic distributed coordination
- **Control Plane / Data Plane Separation:**
  - Control Plane: Task allocation via Coordinator
  - Data Plane: State sharing via DSM gossip
- **Multi-Device Support:** Deploy across multiple Jetsons with unique IDs

## Package Structure

```
ros2_testbed/src/
├── coord/          # Control Plane (Task Coordination)
│   ├── coord/      # Python coordinator logic
│   ├── lf/         # Lingua Franca federated coordinator
│   └── scripts/    # Build and run scripts
├── dsm/            # Data Plane (Gossip-based state sharing)
├── agent/          # Agent execution logic
├── interfaces/     # ROS 2 message/service definitions
├── common/         # Shared utilities (graph, etc.)
└── launch/         # Launch files
```

## Quick Start

### Mode 1: ZooKeeper-Style (Standard)

**On Jetson #1:**
```bash
ros2 launch launch testbed.launch.py device_id:=1 mode:=zookeeper
```

**On Jetson #2:**
```bash
ros2 launch launch testbed.launch.py device_id:=2 mode:=zookeeper
```

### Mode 2: Lingua Franca Federated (Deterministic)

**Setup (one time):**
```bash
cd src/coord
./scripts/build_lf.sh
```

**Run:**
1. **Start RTI (on one machine):**
   ```bash
   ./scripts/start_rti.sh
   ```

2. **On Jetson #1:**
   ```bash
   ros2 launch launch testbed.launch.py device_id:=1 mode:=lf
   ```

3. **On Jetson #2:**
   ```bash
   ros2 launch launch testbed.launch.py device_id:=2 mode:=lf
   ```

## Architecture

### ZooKeeper Mode
```
Jetson 1                    Jetson 2
├─ Coordinator (ROS)        ├─ Coordinator (ROS)
├─ DSM Node (Gossip)        ├─ DSM Node (Gossip)
└─ Agents 10, 11            └─ Agents 20, 21
```

### LF Federated Mode
```
        RTI (Logical Time Sync)
         ↓                  ↓
Jetson 1                    Jetson 2
├─ LF Federate 1            ├─ LF Federate 2
├─ ROS Bridge               ├─ ROS Bridge
├─ DSM Node (Gossip)        ├─ DSM Node (Gossip)
└─ Agents 10, 11            └─ Agents 20, 21
```

## Research Contribution

This testbed enables experimental validation of:
1. **Hybrid Coordination:** Centralized task leases + distributed state gossip
2. **Deterministic Execution:** LF federation provides reproducible multi-device experiments
3. **Scalability:** Compare coordination overhead vs. centralized systems (Open-RMF)

## Documentation

- [Architecture Overview](ARCHITECTURE.md)
- [Coordination Modes](src/coord/README.md)

## Requirements

- ROS 2 (Humble or later)
- Python 3.8+
- Lingua Franca compiler (for LF mode): `lfc` in PATH

## License

MIT License

