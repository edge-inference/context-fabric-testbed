import rclpy
from rclpy.node import Node
from interfaces.msg import DSMUpdate

class DSMNode(Node):
    """
    Manages Distributed Shared Memory (DSM) for this device.
    Handles gossip transmission and reception.
    """
    def __init__(self):
        super().__init__('dsm_node')
        
        # Parameters
        self.declare_parameter('device_id', 1)
        self.device_id = self.get_parameter('device_id').value
        
        # Local Cache (CRDTs)
        self.jam_signals = {}
        self.flow_traces = {}
        
        # Comms
        self.gossip_pub = self.create_publisher(DSMUpdate, 'dsm_gossip', 10)
        self.create_subscription(DSMUpdate, 'dsm_gossip', self.handle_gossip, 10)
        
        # Gossip Timer (e.g., every 300ms)
        self.create_timer(0.3, self.send_gossip)

    def handle_gossip(self, msg):
        """Merge incoming gossip data."""
        if msg.source_agent_id == self.device_id:
            return # Ignore self
            
        # Basic LWW Merge Logic (Placeholder)
        # In real impl, check timestamps and update self.jam_signals
        self.get_logger().debug(f"Received gossip from {msg.source_agent_id}")

    def send_gossip(self):
        """Broadcast local state changes."""
        # Create delta or full state update
        msg = DSMUpdate()
        msg.source_agent_id = self.device_id
        msg.layer_name = "jam_signal"
        # msg.node_ids = ...
        # msg.values = ...
        # msg.timestamps = ...
        
        self.gossip_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = DSMNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

