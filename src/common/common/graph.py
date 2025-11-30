import networkx as nx
import numpy as np
import yaml
import os

class WarehouseGraph:
    """
    Discrete graph representation for warehouse navigation.
    Agents move node-to-node (discrete jumps).
    """
    def __init__(self):
        self.nx_graph = nx.Graph()
        self.node_metadata = {}  # node_id -> {x, y, type}

    @classmethod
    def from_yaml(cls, config_path):
        """Load graph from YAML configuration."""
        instance = cls()
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Graph config not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Load nodes
        for node_id, node_data in config.get('nodes', {}).items():
            instance.nx_graph.add_node(node_id)
            instance.node_metadata[node_id] = {
                'x': node_data['x'],
                'y': node_data['y'],
                'type': node_data['type']
            }
        
        # Load edges (undirected by default)
        for edge in config.get('edges', []):
            u = edge['from']
            v = edge['to']
            weight = edge.get('weight', 1.0)
            instance.nx_graph.add_edge(u, v, weight=weight)
        
        return instance

    def get_neighbors(self, node_id):
        """Get list of adjacent nodes."""
        if node_id not in self.nx_graph:
            return []
        return list(self.nx_graph.neighbors(node_id))

    def get_edge_weight(self, u, v):
        """Get base weight of edge (before DSM costs)."""
        if not self.nx_graph.has_edge(u, v):
            return float('inf')
        return self.nx_graph[u][v].get('weight', 1.0)
    
    def get_node_type(self, node_id):
        """Get semantic type of node (storage, corridor, etc.)."""
        return self.node_metadata.get(node_id, {}).get('type', 'unknown')
    
    def get_node_position(self, node_id):
        """Get (x, y) position of node."""
        meta = self.node_metadata.get(node_id, {})
        return (meta.get('x', 0), meta.get('y', 0))
    
    def shortest_path(self, start, goal, cost_function=None):
        """
        Compute shortest path from start to goal.
        
        Args:
            start: Starting node ID
            goal: Goal node ID
            cost_function: Optional function(u, v) -> cost for dynamic costs
                          If None, uses static edge weights
        
        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if start not in self.nx_graph or goal not in self.nx_graph:
            return None
        
        try:
            if cost_function is None:
                # Use static weights
                path = nx.shortest_path(self.nx_graph, start, goal, weight='weight')
            else:
                # Use dynamic costs (e.g., from DSM)
                # Create weight dict for NetworkX
                def weight_func(u, v, d):
                    return cost_function(u, v)
                
                path = nx.shortest_path(self.nx_graph, start, goal, weight=weight_func)
            
            return path
        except nx.NetworkXNoPath:
            return None
    
    def astar_path(self, start, goal, jam_costs=None, flow_costs=None, 
                   conflict_nodes=None,
                   jam_weight=2.0, flow_weight=1.0, conflict_weight=100.0):
        """
        A* pathfinding with DSM-aware costs.
        
        Args:
            start: Starting node ID
            goal: Goal node ID
            jam_costs: Dict[node_id -> jam_value] (0.0-1.0)
            flow_costs: Dict[node_id -> flow_value] (0.0-1.0)
            conflict_nodes: Set[node_id] or Dict[node_id -> count] of occupied nodes
            jam_weight: Multiplier for jam penalty
            flow_weight: Multiplier for flow penalty
            conflict_weight: Multiplier for conflict penalty (intent)
        
        Returns:
            List of node IDs forming the path, or None if no path exists
        """
        if start not in self.nx_graph or goal not in self.nx_graph:
            return None
        
        jam_costs = jam_costs or {}
        flow_costs = flow_costs or {}
        conflict_nodes = conflict_nodes or set()
        
        def heuristic(u, v):
            """Manhattan distance heuristic."""
            u_pos = self.get_node_position(u)
            v_pos = self.get_node_position(v)
            return abs(u_pos[0] - v_pos[0]) + abs(u_pos[1] - v_pos[1])
        
        def cost_func(u, v, edge_data):
            """Dynamic cost incorporating DSM."""
            base_cost = edge_data.get('weight', 1.0)
            
            # Add penalties for congestion
            jam_penalty = jam_costs.get(v, 0.0) * jam_weight
            flow_penalty = flow_costs.get(v, 0.0) * flow_weight
            
            # Add penalty for conflicts (intent)
            conflict_penalty = 0.0
            if isinstance(conflict_nodes, set):
                if v in conflict_nodes:
                    conflict_penalty = conflict_weight
            elif isinstance(conflict_nodes, dict):
                conflict_penalty = conflict_nodes.get(v, 0) * conflict_weight
            
            return base_cost + jam_penalty + flow_penalty + conflict_penalty
        
        try:
            path = nx.astar_path(
                self.nx_graph, 
                start, 
                goal, 
                heuristic=heuristic,
                weight=cost_func
            )
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_all_nodes(self):
        """Get list of all node IDs."""
        return list(self.nx_graph.nodes())
    
    def get_nodes_by_type(self, node_type):
        """Get all nodes of a specific type (e.g., 'storage', 'sortation')."""
        return [
            node_id for node_id, meta in self.node_metadata.items()
            if meta.get('type') == node_type
        ]
    
    def num_nodes(self):
        """Get total number of nodes."""
        return self.nx_graph.number_of_nodes()
    
    def num_edges(self):
        """Get total number of edges."""
        return self.nx_graph.number_of_edges()
