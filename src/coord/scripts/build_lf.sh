#!/bin/bash
# Build and run LF Coordinator (Federated Mode)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LF_DIR="$SCRIPT_DIR/../lf"

echo "[LF Build] Compiling Coordinator.lf..."
cd "$LF_DIR"

# Compile with federation support
lfc --rti Coordinator.lf

echo "[LF Build] Compilation complete. Generated files:"
ls -la src-gen/Coordinator/

echo ""
echo "To run the federated coordinator:"
echo "1. Start RTI:    ./src-gen/Coordinator/bin/RTI"
echo "2. Start Fed 1:  ./src-gen/Coordinator/bin/Coordinator_fed1"
echo "3. Start Fed 2:  ./src-gen/Coordinator/bin/Coordinator_fed2"

