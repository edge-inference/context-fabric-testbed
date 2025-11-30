import rclpy
from rclpy.node import Node
from interfaces.msg import AgentState, DSMUpdate, TaskEvent
import time
import csv
import os
from collections import defaultdict

class MetricsNode(Node):
    """
    Central Metrics Aggregator.
    Subscribes to all system state topics and generates real-time reports.
    """
    def __init__(self):
        super().__init__('metrics_node')
        
        # Subscriptions
        self.create_subscription(AgentState, 'agent_state', self.handle_agent_state, 10)
        self.create_subscription(DSMUpdate, 'dsm_gossip', self.handle_dsm_gossip, 10)
        self.create_subscription(TaskEvent, 'task_events', self.handle_task_event, 10)
        
        # State Tracking
        self.agents = {}  # id -> {state, node, task, battery, last_seen}
        self.tasks = {}   # id -> {status, agent, start_time, end_time}
        self.gossip_count = 0
        self.gossip_bytes = 0
        
        # Metrics
        self.start_time = time.time()
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_latency = 0
        
        # Logging
        self.log_dir = "/ros2_ws/logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.csv_file = open(f"{self.log_dir}/metrics_run_{int(self.start_time)}.csv", 'w')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['timestamp', 'tasks_completed', 'active_agents', 'gossip_rate', 'avg_completion_time'])
        
        # Timer for reporting (every 1s)
        self.create_timer(1.0, self.report_metrics)
        
        self.get_logger().info("Metrics Node Started - Monitoring System Health")

    def handle_agent_state(self, msg):
        self.agents[msg.agent_id] = {
            'state': msg.state,
            'node': msg.current_node,
            'task': msg.active_task_id,
            'battery': msg.battery_level,
            'last_seen': time.time()
        }

    def handle_dsm_gossip(self, msg):
        self.gossip_count += 1
        # Estimate size: header + arrays
        size = 20 + len(msg.node_ids)*4 + len(msg.values)*8 + len(msg.timestamps)*8
        self.gossip_bytes += size

    def handle_task_event(self, msg):
        if msg.event_type == "CREATED":
            self.tasks[msg.task_id] = {'status': 'AVAILABLE', 'created': msg.timestamp_ms}
        
        elif msg.event_type == "CLAIMED":
            if msg.task_id in self.tasks:
                self.tasks[msg.task_id]['status'] = 'CLAIMED'
                self.tasks[msg.task_id]['agent'] = msg.agent_id
                self.tasks[msg.task_id]['claimed'] = msg.timestamp_ms
                
        elif msg.event_type == "COMPLETED":
            if msg.task_id in self.tasks:
                entry = self.tasks[msg.task_id]
                entry['status'] = 'COMPLETED'
                entry['completed'] = msg.timestamp_ms
                self.tasks_completed += 1
                
                # Calculate latency (Claim -> Complete)
                if 'claimed' in entry:
                    latency = (msg.timestamp_ms - entry['claimed']) / 1000.0
                    self.total_latency += latency

        elif msg.event_type == "FAILED":
             if msg.task_id in self.tasks:
                self.tasks[msg.task_id]['status'] = 'FAILED'
                self.tasks_failed += 1

    def report_metrics(self):
        """Print status table to log"""
        uptime = time.time() - self.start_time
        active_agents = len([a for a in self.agents.values() if time.time() - a['last_seen'] < 5])
        avg_time = (self.total_latency / self.tasks_completed) if self.tasks_completed > 0 else 0
        
        # Console Output
        self.get_logger().info("="*40)
        self.get_logger().info(f"System Status (Uptime: {uptime:.0f}s)")
        self.get_logger().info(f"Active Agents: {active_agents}")
        self.get_logger().info(f"Tasks: {self.tasks_completed} Done | {self.tasks_failed} Failed | Avg Time: {avg_time:.1f}s")
        self.get_logger().info(f"Gossip: {self.gossip_count} msgs ({self.gossip_bytes/1024:.1f} KB)")
        
        # Agent Details
        for aid, data in sorted(self.agents.items()):
            age = time.time() - data['last_seen']
            status = "ONLINE" if age < 5 else "OFFLINE"
            self.get_logger().info(f"  Agent {aid}: {status} [{data['state']}] Node: {data['node']} Task: {data['task']}")
            
        self.get_logger().info("="*40)
        
        # CSV Log
        self.csv_writer.writerow([
            time.time(),
            self.tasks_completed,
            active_agents,
            self.gossip_count,
            avg_time
        ])
        self.csv_file.flush()
        
        # Reset counters for rates if desired, but cumulative is often better for logs
        # self.gossip_count = 0 

def main(args=None):
    rclpy.init(args=args)
    node = MetricsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
