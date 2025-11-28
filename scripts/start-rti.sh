#!/bin/bash
# Start RTI on x86 station (172.17.174.183)
# 
# Usage: 
#   ./start-rti.sh [num_federates]
#   Default: 2 federates

NUM_FEDS=${1:-2}

echo "Context-Fabric Runtime Infrastructure (RTI)"
echo "Listening on: 0.0.0.0:15045"
echo "Expecting: $NUM_FEDS federates"
echo ""
echo "Federates should connect to: 172.17.174.183:15045"
echo "----------------------------------------------"

# Run RTI (from scripts/ directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../fed-gen/coordinator/bin/RTI" -n $NUM_FEDS

