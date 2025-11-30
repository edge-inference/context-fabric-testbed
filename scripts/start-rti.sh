#!/bin/bash
# Start RTI on x86 station (172.17.174.183)
# 
# Usage: 
#   ./start-rti.sh [num_federates] [federation_id]
#   Default: 2 federates, auto-generated federation ID

NUM_FEDS=${1:-2}
# Use fixed federation ID for consistency across devices
FEDERATION_ID=${LF_FEDERATION_ID:-"context-fabric-testbed-2025"}

echo "Context-Fabric Runtime Infrastructure (RTI)"
echo "Federation ID: $FEDERATION_ID"
echo "Listening on: 0.0.0.0:15045"
echo "Expecting: $NUM_FEDS federates"
echo ""
echo "Federates should connect to: 172.17.174.183:15045"
echo "----------------------------------------------"
echo ""
echo "IMPORTANT: Set this on Jetson devices:"
echo "  export LF_FEDERATION_ID='$FEDERATION_ID'"
echo "----------------------------------------------"

# Run RTI (from scripts/ directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../fed-gen/coordinator/bin/RTI" \
    -i "$FEDERATION_ID" \
    -n $NUM_FEDS \
    -c init \
    exchanges-per-interval 10

