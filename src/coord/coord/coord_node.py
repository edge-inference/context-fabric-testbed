import rclpy
from rclpy.node import Node
from interfaces.srv import GetAvailableTasks, ClaimTask, CompleteTask, CreateTask
from interfaces.msg import TaskInfo

from .coordinator import Coordinator


class CoordinatorNode(Node):
    """
    ROS2 wrapper for ZooKeeper-style Coordinator.
    
    Provides ROS2 services for:
    - Task creation (CreateTask)
    - Task claiming (ClaimTask)
    - Task completion (CompleteTask)
    - Query available tasks (GetAvailableTasks)
    """
    
    def __init__(self):
        super().__init__('coordinator_node')
        
        self.declare_parameter('lease_ttl_ms', 300000)
        self.declare_parameter('tick_rate_ms', 100)
        
        lease_ttl_ms = self.get_parameter('lease_ttl_ms').value
        tick_rate_ms = self.get_parameter('tick_rate_ms').value
        
        self.coordinator = Coordinator(default_lease_ttl_ms=lease_ttl_ms)
        
        self.create_service(CreateTask, 'coord/create_task', self.handle_create_task)
        self.create_service(ClaimTask, 'coord/claim_task', self.handle_claim_task)
        self.create_service(CompleteTask, 'coord/complete_task', self.handle_complete_task)
        self.create_service(GetAvailableTasks, 'coord/get_available_tasks', self.handle_get_available_tasks)
        
        period_s = tick_rate_ms / 1000.0
        self.timer = self.create_timer(period_s, self.tick)
        
        self.get_logger().info(f"Coordinator started (lease_ttl={lease_ttl_ms}ms, tick_rate={tick_rate_ms}ms)")
    
    def tick(self):
        """Periodic tick to expire leases and update time"""
        current_time_ms = int(self.get_clock().now().nanoseconds / 1_000_000)
        self.coordinator.tick(current_time_ms)
    
    def handle_create_task(self, request, response):
        """Handle CreateTask service call"""
        try:
            task_id = self.coordinator.create_task(
                location=request.location,
                task_type=request.task_type,
                priority=request.priority
            )
            response.success = True
            response.task_id = task_id
            self.get_logger().info(f"Created task #{task_id} at location {request.location}")
        except Exception as e:
            response.success = False
            self.get_logger().error(f"Failed to create task: {e}")
        
        return response
    
    def handle_claim_task(self, request, response):
        """Handle ClaimTask service call"""
        try:
            success = self.coordinator.try_claim(
                task_id=request.task_id,
                agent_id=request.agent_id,
                ttl_ms=request.ttl_ms if request.ttl_ms > 0 else None
            )
            response.success = success
            if success:
                response.message = f"Task {request.task_id} claimed by agent {request.agent_id}"
                self.get_logger().info(response.message)
            else:
                response.message = f"Task {request.task_id} already claimed or unavailable"
                self.get_logger().warn(response.message)
        except Exception as e:
            response.success = False
            response.message = str(e)
            self.get_logger().error(f"Failed to claim task: {e}")
        
        return response
    
    def handle_complete_task(self, request, response):
        """Handle CompleteTask service call"""
        try:
            success = self.coordinator.complete_task(
                task_id=request.task_id,
                agent_id=request.agent_id
            )
            response.success = success
            if success:
                response.message = f"Task {request.task_id} completed by agent {request.agent_id}"
                self.get_logger().info(response.message)
            else:
                response.message = f"Task {request.task_id} not owned by agent {request.agent_id}"
                self.get_logger().warn(response.message)
        except Exception as e:
            response.success = False
            response.message = str(e)
            self.get_logger().error(f"Failed to complete task: {e}")
        
        return response
    
    def handle_get_available_tasks(self, request, response):
        """Handle GetAvailableTasks service call"""
        try:
            tasks = self.coordinator.get_available_tasks()
            
            response.success = True
            response.available_tasks = []
            
            for task in tasks:
                task_info = TaskInfo()
                task_info.task_id = task.task_id
                task_info.location = task.location
                task_info.task_type = task.task_type
                task_info.priority = task.priority
                task_info.status = task.status.value
                response.available_tasks.append(task_info)
            
            self.get_logger().debug(f"Agent {request.agent_id} requested tasks: {len(response.available_tasks)} available")
        except Exception as e:
            response.success = False
            self.get_logger().error(f"Failed to get available tasks: {e}")
        
        return response


def main(args=None):
    rclpy.init(args=args)
    node = CoordinatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

