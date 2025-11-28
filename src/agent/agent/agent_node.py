import rclpy
from rclpy.node import Node
from interfaces.msg import AgentState, TaskAssignment
from interfaces.srv import TaskService
from common.graph import WarehouseGraph

class AgentNode(Node):
    def __init__(self):
        super().__init__('agent_node')
        
        # Parameters
        self.declare_parameter('agent_id', 1)
        self.declare_parameter('start_node', 0)
        self.declare_parameter('tick_rate_ms', 100)
        
        self.agent_id = self.get_parameter('agent_id').value
        self.current_node = self.get_parameter('start_node').value
        self.state = "IDLE"
        self.path = []
        
        # Publishers
        self.state_pub = self.create_publisher(AgentState, 'agent_state', 10)
        
        # Clients
        self.task_client = self.create_client(TaskService, 'task_service')
        
        # Timer (Heartbeat / Movement)
        period_s = self.get_parameter('tick_rate_ms').value / 1000.0
        self.timer = self.create_timer(period_s, self.tick)
        
        self.get_logger().info(f"Agent {self.agent_id} started at node {self.current_node}")

    def tick(self):
        """Main loop: Movement and State Machine."""
        
        # Optional: Ask Brain for high-level decisions
        # action = self.brain.decide_next_action(self.state, dsm_context=None)
        
        if self.state == "NAVIGATING" and self.path:
            self.move_one_step()
        elif self.state == "IDLE":
            # Logic to request task or check DSM would go here
            pass
            
        self.publish_state()

    def move_one_step(self):
        """Virtual movement: Teleport to next node in path."""
        if self.path:
            self.current_node = self.path.pop(0)
            if not self.path:
                self.state = "WORKING" # Or whatever next state is
                self.get_logger().info("Target reached")

    def publish_state(self):
        msg = AgentState()
        msg.agent_id = self.agent_id
        msg.current_node = self.current_node
        msg.state = self.state
        msg.timestamp_ms = self.get_clock().now().nanoseconds // 1000000
        self.state_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AgentNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

