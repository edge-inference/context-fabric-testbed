#!/bin/bash
# Launch Federate 1 (for Jetson device_id=1)
# Connects to RTI at x86 station

export LF_RTI_HOST=172.17.174.183
export LF_RTI_PORT=15045

echo "Context-Fabric Federate 1"
echo "Connecting to RTI at ${LF_RTI_HOST}:${LF_RTI_PORT}"
echo ""

# Run the federate (from scripts/ directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../fed-gen/coordinator/bin/federate__fed1"

