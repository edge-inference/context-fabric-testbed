import networkx as nx
import numpy as np
import yaml

class WarehouseGraph:
    """
    Lightweight graph representation for ROS2 nodes.
    Loads from the same YAML config format as the simulation.
    """
    def __init__(self):
        self.nx_graph = nx.Graph()
        self.node_metadata = {}

    @classmethod
    def from_yaml(cls, config_path):
        """Load graph from YAML configuration."""
        instance = cls()
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # This implementation should match the logic in world/graph.py
        # For the template, we assume pre-computed adjacency or standard grid gen
        # Placeholder for actual loading logic
        return instance

    def get_neighbors(self, node_id):
        return list(self.nx_graph.neighbors(node_id))

    def get_edge_weight(self, u, v):
        return self.nx_graph[u][v].get('weight', 1.0)

