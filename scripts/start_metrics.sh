#!/bin/bash
source /ros2_ws/install/setup.bash
echo "=== Starting Metrics Node ==="
# Try direct execution (installed via pip entry_point)
metrics_node || python3 -m common.metrics_node
