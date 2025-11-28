"""
ROS 2 to Lingua Franca Bridge

This node acts as a bridge between ROS 2 agents and the LF Coordinator federates.
It translates ROS 2 service calls into messages that the LF federate can process.
"""

import rclpy
from rclpy.node import Node
from interfaces.srv import ClaimTask, CompleteTask, GetAvailableTasks, CreateTask
from interfaces.msg import TaskInfo
import socket
import json
import threading
import time


class LFBridgeNode(Node):
    """
    Bridge between ROS 2 and Lingua Franca Coordinator
    
    This node:
    1. Provides ROS 2 services (same API as coord_node.py)
    2. Forwards requests to local LF federate via socket
    3. Returns responses to ROS 2 agents
    """
    
    def __init__(self):
        super().__init__('lf_bridge_node')
        
        self.declare_parameter('device_id', 1)
        self.declare_parameter('lf_port', 9000)
        
        self.device_id = self.get_parameter('device_id').value
        self.lf_port = self.get_parameter('lf_port').value
        
        # Socket connection to LF federate
        self.lf_socket = None
        self.connect_to_lf()
        
        # ROS 2 Services (same interface as ZooKeeper-style coordinator)
        self.create_service(CreateTask, 'coord/create_task', self.handle_create_task)
        self.create_service(ClaimTask, 'coord/claim_task', self.handle_claim_task)
        self.create_service(CompleteTask, 'coord/complete_task', self.handle_complete_task)
        self.create_service(GetAvailableTasks, 'coord/get_available_tasks', self.handle_get_available_tasks)
        
        self.get_logger().info(f"LF Bridge started (device_id={self.device_id}, lf_port={self.lf_port})")
    
    def connect_to_lf(self):
        """Connect to local LF federate via TCP socket"""
        max_retries = 10
        for attempt in range(max_retries):
            try:
                self.lf_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.lf_socket.connect(('localhost', self.lf_port))
                self.get_logger().info(f"Connected to LF federate on port {self.lf_port}")
                return
            except ConnectionRefusedError:
                if attempt < max_retries - 1:
                    self.get_logger().warn(f"LF federate not ready, retrying... ({attempt+1}/{max_retries})")
                    time.sleep(1)
                else:
                    self.get_logger().error("Failed to connect to LF federate")
                    raise
    
    def send_to_lf(self, message: dict) -> dict:
        """Send message to LF federate and wait for response"""
        try:
            # Send request
            msg_str = json.dumps(message) + '\n'
            self.lf_socket.sendall(msg_str.encode('utf-8'))
            
            # Receive response
            response_str = self.lf_socket.recv(4096).decode('utf-8')
            response = json.loads(response_str)
            
            return response
        except Exception as e:
            self.get_logger().error(f"LF communication error: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_create_task(self, request, response):
        """Forward create task request to LF"""
        lf_request = {
            'type': 'create',
            'location': request.location,
            'task_type': request.task_type,
            'priority': request.priority
        }
        
        lf_response = self.send_to_lf(lf_request)
        
        response.success = lf_response.get('success', False)
        response.task_id = lf_response.get('task_id', 0)
        
        return response
    
    def handle_claim_task(self, request, response):
        """Forward claim request to LF"""
        lf_request = {
            'type': 'claim',
            'task_id': request.task_id,
            'agent_id': request.agent_id,
            'ttl_ms': request.ttl_ms if request.ttl_ms > 0 else 300000
        }
        
        lf_response = self.send_to_lf(lf_request)
        
        response.success = lf_response.get('success', False)
        response.message = f"Task {request.task_id} claim: {lf_response.get('success', False)}"
        
        if response.success:
            self.get_logger().info(f"Agent {request.agent_id} claimed task {request.task_id} (LF deterministic)")
        
        return response
    
    def handle_complete_task(self, request, response):
        """Forward completion to LF"""
        lf_request = {
            'type': 'complete',
            'task_id': request.task_id,
            'agent_id': request.agent_id
        }
        
        lf_response = self.send_to_lf(lf_request)
        
        response.success = lf_response.get('success', False)
        response.message = f"Task {request.task_id} completed"
        
        return response
    
    def handle_get_available_tasks(self, request, response):
        """Forward query to LF"""
        lf_request = {
            'type': 'get_tasks',
            'agent_id': request.agent_id
        }
        
        lf_response = self.send_to_lf(lf_request)
        
        response.success = lf_response.get('success', False)
        response.available_tasks = []
        
        for task_dict in lf_response.get('tasks', []):
            task_info = TaskInfo()
            task_info.task_id = task_dict['task_id']
            task_info.location = task_dict['location']
            task_info.task_type = task_dict['task_type']
            task_info.priority = task_dict['priority']
            task_info.status = task_dict['status']
            response.available_tasks.append(task_info)
        
        return response
    
    def destroy_node(self):
        """Cleanup socket connection"""
        if self.lf_socket:
            self.lf_socket.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = LFBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

