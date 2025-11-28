"""
Coordinator: ZooKeeper-Style Control Plane for ROS2

Provides strong consistency for task management with:
- Atomic task claims via LeaseManager
- Authoritative task state via TaskRegistry
- TTL-based lease expiration and renewal
"""

from typing import Dict, List, Optional
import time

from .lease_manager import LeaseManager
from .task_registry import TaskRegistry, TaskStatus, Task


class Coordinator:
    """
    ZooKeeper-like coordination service for warehouse ROS2 system.
    
    Separates control plane (strong consistency) from data plane (eventual).
    """
    
    def __init__(self, 
                 default_lease_ttl_ms: int = 300000):
        self.task_registry = TaskRegistry()
        self.lease_manager = LeaseManager(default_ttl_ms=default_lease_ttl_ms)
        
        self.current_time_ms = 0
        
        self.metrics = {
            'claim_attempts': 0,
            'claim_successes': 0,
            'claim_conflicts': 0,
            'lease_expirations': 0,
            'lease_renewals': 0,
            'tasks_created': 0,
            'tasks_completed': 0,
        }
    
    def tick(self, current_time_ms: int) -> None:
        """
        Advance coordinator logical time; expire leases.
        Called periodically by the coordinator node.
        """
        self.current_time_ms = current_time_ms
        
        expired = self.lease_manager.expire_leases(current_time_ms)
        self.metrics['lease_expirations'] += len(expired)
        
        for resource_id, owner_id in expired:
            if isinstance(resource_id, int):
                task = self.task_registry.get_task(resource_id)
                if task and task.status == TaskStatus.CLAIMED:
                    self.task_registry.fail_task(resource_id, owner_id, retry=True)
    
    def create_task(self, location: int, task_type: str = "pick", 
                   priority: float = 1.0) -> int:
        """
        Create a new task in the authoritative registry.
        Single source of truth for task existence and status.
        """
        task_id = self.task_registry.create_task(
            location=location,
            task_type=task_type,
            priority=priority
        )
        
        self.metrics['tasks_created'] += 1
        
        return task_id
    
    def get_available_tasks(self, region_id: int = None, 
                          max_distance: int = None) -> List[Task]:
        """
        Get available tasks, optionally filtered by region.
        Strong, consistent read - no stale data.
        """
        return self.task_registry.get_available_tasks(
            location=region_id,
            max_distance=max_distance
        )
    
    def get_task_status(self, task_id: int) -> Optional[str]:
        """Get current status of a task"""
        task = self.task_registry.get_task(task_id)
        return task.status.value if task else None
    
    def try_claim(self, task_id: int, agent_id: int, ttl_ms: int = None) -> bool:
        """
        Attempt to claim a task lease. Returns True if granted.
        Atomically: 1) acquires lease, 2) updates task status to 'claimed'
        """
        self.metrics['claim_attempts'] += 1
        
        task = self.task_registry.get_task(task_id)
        if not task or task.status != TaskStatus.AVAILABLE:
            self.metrics['claim_conflicts'] += 1
            return False
        
        ttl = ttl_ms or self.lease_manager.default_ttl_ms
        lease_success = self.lease_manager.try_acquire(
            resource_id=task_id,
            owner_id=agent_id,
            ttl_ms=ttl,
            current_time_ms=self.current_time_ms
        )
        
        if lease_success:
            self.task_registry.claim_task(task_id, agent_id)
            self.metrics['claim_successes'] += 1
        else:
            self.metrics['claim_conflicts'] += 1
        
        return lease_success
    
    def renew_claim(self, task_id: int, agent_id: int, ttl_ms: int = None) -> bool:
        """Renew an existing lease to extend TTL"""
        ttl = ttl_ms or self.lease_manager.default_ttl_ms
        success = self.lease_manager.renew(
            resource_id=task_id,
            owner_id=agent_id,
            ttl_ms=ttl,
            current_time_ms=self.current_time_ms
        )
        if success:
            self.metrics['lease_renewals'] += 1
        return success
    
    def release_claim(self, task_id: int, agent_id: int) -> bool:
        """Explicitly release a lease (for failed/cancelled tasks)"""
        success = self.lease_manager.release(
            resource_id=task_id,
            owner_id=agent_id
        )
        
        if success:
            task = self.task_registry.get_task(task_id)
            if task and task.agent_id == agent_id:
                self.task_registry.fail_task(task_id, agent_id, retry=True)
        
        return success
    
    def complete_task(self, task_id: int, agent_id: int) -> bool:
        """
        Mark task as completed and release lease.
        Atomically: 1) releases lease, 2) updates status to 'completed'
        """
        if self.lease_manager.get_owner(task_id) != agent_id:
            return False
        
        self.lease_manager.release(task_id, agent_id)
        success = self.task_registry.complete_task(task_id, agent_id)
        
        if success:
            self.metrics['tasks_completed'] += 1
        
        return success
    
    def get_lease_owner(self, task_id: int) -> Optional[int]:
        """Check who currently holds the lease for a task"""
        return self.lease_manager.get_owner(task_id)
    
    def get_metrics(self) -> Dict[str, int]:
        """Get coordinator metrics"""
        return self.metrics.copy()

