#!/bin/bash
# Helper to create a task via the metrics container (which has ROS installed)
# Usage: ./create_task.sh [location] [type] [priority]

LOC=${1:-10}
TYPE=${2:-pick}
PRIO=${3:-5}

docker compose exec metrics bash -c "source /ros2_ws/install/setup.bash && ros2 service call /robot_1/coord/create_task interfaces/srv/CreateTask \"{location: $LOC, task_type: '$TYPE', priority: $PRIO}\""
