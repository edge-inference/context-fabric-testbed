#!/bin/bash
set -e

# Usage: ./start_robot.sh <device_id> <fed_executable> <rti_host> <rti_port> <federation_id>

DEVICE_ID=$1
FED_EXEC=$2
RTI_HOST=$3
RTI_PORT=$4
FED_ID=$5

echo "=== Starting Robot $DEVICE_ID ==="
echo "Federate: $FED_EXEC"
echo "RTI: $RTI_HOST:$RTI_PORT"
echo "Federation ID: $FED_ID"

# Source ROS 2 workspace (includes interfaces)
source /ros2_ws/install/setup.bash

# Debug: Print PYTHONPATH
echo "DEBUG: PYTHONPATH is $PYTHONPATH"

# 1. Start LF Federate
echo "Starting LF Federate..."
$FED_EXEC -i "$FED_ID" --rti "$RTI_HOST:$RTI_PORT" &
LF_PID=$!

sleep 5

# 2. Start LF Bridge Node (Connects ROS to LF)
echo "Starting LF Bridge Node..."
# Wait for LF to initialize socket
sleep 5
lf_bridge_node --ros-args -r __ns:=/robot_$DEVICE_ID -r __node:=lf_bridge_node -p device_id:=$DEVICE_ID -p lf_port:=$((9000 + DEVICE_ID)) -r task_events:=/task_events &
BRIDGE_PID=$!

sleep 2

# 3. Start DSM Node
echo "Starting DSM Node..."
dsm_node --ros-args -r __ns:=/robot_$DEVICE_ID -r __node:=dsm_node -p device_id:=$DEVICE_ID -r dsm_gossip:=/dsm_gossip &
DSM_PID=$!

# 4. Start Agent Node
echo "Starting Agent Node..."
agent_node --ros-args -r __ns:=/robot_$DEVICE_ID -r __node:=agent_node -p agent_id:=$DEVICE_ID -p device_id:=$DEVICE_ID -r agent_state:=/agent_state -r dsm_gossip:=/dsm_gossip &
AGENT_PID=$!

# Wait for any process to exit
wait -n

# Cleanup on exit
kill $LF_PID $BRIDGE_PID $DSM_PID $AGENT_PID

