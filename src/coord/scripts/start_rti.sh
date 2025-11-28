#!/bin/bash
# Start Lingua Franca RTI (Run Time Infrastructure)
#
# The RTI coordinates logical time across all LF federates.
# Run this FIRST before starting the federated coordinators.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RTI_BIN="$SCRIPT_DIR/../lf/src-gen/Coordinator/bin/RTI"

if [ ! -f "$RTI_BIN" ]; then
    echo "Error: RTI binary not found. Did you run build_lf.sh?"
    echo "Expected: $RTI_BIN"
    exit 1
fi

echo "Starting Lingua Franca RTI..."
echo "Federates will connect to this RTI to synchronize logical time."
echo ""

# Run RTI with appropriate flags
"$RTI_BIN" -n 2 -c 1  # -n 2 = 2 federates, -c 1 = clock sync mode

# Note: RTI will listen on port 15045 by default
# Federates must be able to reach this port

