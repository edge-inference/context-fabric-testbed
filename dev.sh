#!/bin/bash
# Development script for Context-Fabric Docker containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 {start|start-rti|stop|restart|status|logs|clean|build}"
    echo ""
    echo "Commands:"
    echo "  start     - Start all containers"
    echo "  start-rti - Start only RTI and metrics (for distributed setup)"
    echo "  stop      - Stop all containers"
    echo "  restart   - Restart all containers"
    echo "  status    - Show container status"
    echo "  logs      - Show logs (optional: rti, fed1, fed2, or all)"
    echo "  clean     - Stop and remove all containers"
    echo "  build     - Build Docker images"
    echo "  monitor   - Attach to metrics dashboard"
    exit 1
}

monitor() {
    echo -e "${GREEN}Attaching to Metrics Dashboard... (Ctrl+C to detach)${NC}"
    # Use logs -f because it's non-interactive logging for now
    docker compose logs -f metrics
}

start_rti() {
    echo -e "${GREEN}Starting RTI and Metrics only (distributed mode)...${NC}"
    docker compose up -d rti metrics
    
    echo -e "${YELLOW}Waiting for RTI to initialize...${NC}"
    sleep 3
    
    if ! docker ps | grep -q rti; then
        echo -e "${RED}RTI container failed to start${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}RTI and Metrics started.${NC}"
    echo -e "${YELLOW}RTI listening on: 172.17.174.183:15045${NC}"
    echo -e "${YELLOW}Federation ID: context-fabric-testbed-2025${NC}"
    echo ""
    echo -e "${GREEN}Now start robot containers on Jetson devices.${NC}"
}

start() {
    echo -e "${GREEN}Starting Context-Fabric containers...${NC}"
    
    # Start RTI and metrics first
    echo -e "${YELLOW}Starting RTI and metrics...${NC}"
    docker compose up -d rti metrics
    
    # Wait for RTI to start
    echo -e "${YELLOW}Waiting for RTI to initialize...${NC}"
    sleep 15
    
    # Check if RTI is running
    if ! docker ps | grep -q rti; then
        echo -e "${RED}RTI container failed to start${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}RTI is running. Starting robots...${NC}"
    docker compose up -d robot1 robot2
    
    echo -e "${GREEN}Containers started. Use './dev.sh logs' to view logs.${NC}"
}

stop() {
    echo -e "${YELLOW}Stopping Context-Fabric containers...${NC}"
    docker compose down
    echo -e "${GREEN}Containers stopped.${NC}"
}

restart() {
    echo -e "${YELLOW}Restarting Context-Fabric containers...${NC}"
    stop
    sleep 1
    start
}

status() {
    echo -e "${GREEN}Container Status:${NC}"
    echo "===================="
    docker compose ps
    echo ""
    echo -e "${GREEN}Resource Usage:${NC}"
    echo "===================="
    docker stats --no-stream rti fed1 fed2 2>/dev/null || echo "No containers running"
}

logs() {
    SERVICE=${2:-all}
    
    if [ "$SERVICE" = "all" ]; then
        echo -e "${GREEN}Showing logs for all containers (Ctrl+C to exit):${NC}"
        docker compose logs -f
    elif [ "$SERVICE" = "rti" ] || [ "$SERVICE" = "fed1" ] || [ "$SERVICE" = "fed2" ]; then
        echo -e "${GREEN}Showing logs for $SERVICE (Ctrl+C to exit):${NC}"
        docker compose logs -f "$SERVICE"
    else
        echo -e "${RED}Invalid service name. Use: rti, fed1, fed2, or all${NC}"
        exit 1
    fi
}

clean() {
    echo -e "${YELLOW}Cleaning up Context-Fabric containers and images...${NC}"
    docker compose down -v
    docker rm -f rti robot1 robot2 metrics 2>/dev/null || true
    
    # Remove images
    echo -e "${YELLOW}Removing Context-Fabric images...${NC}"
    docker rmi -f context-fabric-fed context-fabric-rti 2>/dev/null || true
    
    echo -e "${GREEN}Cleanup complete.${NC}"
}

build() {
    ARGS=""
    if [ "${2:-}" == "--no-cache" ]; then
        ARGS="--no-cache"
    fi

    # Optional: Deep clean images before build if --clean passed
    if [ "${2:-}" == "--clean" ]; then
        echo -e "${YELLOW}Removing existing Context-Fabric images...${NC}"
        docker rmi -f context-fabric-rti context-fabric-fed 2>/dev/null || true
        ARGS="--no-cache"
    fi

    echo -e "${GREEN}Building Context-Fabric Docker images...${NC}"
    echo ""
    echo -e "${YELLOW}Building RTI image...${NC}"
    docker build $ARGS -t context-fabric-rti -f Dockerfile.rti .
    echo ""
    echo -e "${YELLOW}Building Federate image...${NC}"
    docker build $ARGS -t context-fabric-fed -f Dockerfile.fed .
    
    echo -e "${YELLOW}Pruning dangling images...${NC}"
    docker image prune -f --filter "label!=keep"
    
    echo ""
    echo -e "${GREEN}Build complete!${NC}"
}

# Main command handler
case "${1:-}" in
    start)
        start
        ;;
    start-rti)
        start_rti
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$@"
        ;;
    clean)
        clean
        ;;
    build)
        build "$@"
        ;;
    monitor)
        monitor
        ;;
    *)
        usage
        ;;
esac

