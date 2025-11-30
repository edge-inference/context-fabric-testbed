# Planned Optimizations

## 1. Port Cython Pathfinding (High Priority for Jetson)
- **Current State**: The testbed uses `networkx` (pure Python) for A* pathfinding.
- **Goal**: Port `warehouse/perf/astar_fast.pyx` from the simulation.
- **Why**: 
    - NetworkX is O(N) or slower per step due to Python overhead.
    - Simulation uses a custom **Conflict Index** (spatial hash) in Cython for O(1) collision checks.
- **Steps**:
    1. Copy `astar_fast.pyx` to `src/common/perf/`.
    2. Update `src/common/setup.py` to handle Cython compilation.
    3. Switch `agent_node.py` to use `astar_fast`.

## 2. Shared Memory & Vectorized Merging
- **Current State**: `dsm_node` uses Python dictionaries and loops for merging gossip.
- **Goal**: Switch to **NumPy Arrays** and **Vectorized Operations** (like simulation).
- **Why**: 
    - Merging dictionaries is O(N) in Python (slow).
    - Simulation uses `mask = other.ts > self.ts; self.val[mask] = other.val[mask]` which is C-speed.
    - Enables Zero-Copy if we map Shared Memory between containers (advanced).

## 3. Efficient Gossip
- **Current State**: Broadcasts full JSON-like updates (via ROS msgs).
- **Goal**: Implement delta-based gossip.

## 4. Agent Location Layer
- **Current State**: DSM tracks flow/intent but relies on `AgentState` topic for locations.
- **Goal**: Add explicit `agent_locations` layer to `dsm_node` (Done in `dsm_node.py`, pending verify).

## 5. Event-Driven Task Updates (Watchers) and avoid constant broadcast (make only event driven)
- **Current State**: Agents poll `GetAvailableTasks` periodically.
- **Goal**: Implement `TaskUpdate` topic or Zookeeper-style watchers.
- **Why**: Eliminates polling traffic when no tasks are available.
