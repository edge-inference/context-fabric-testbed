#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COMPOSE_FILE="docker-compose.jetson.yml"

# Detect Docker Compose command
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose --version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}Error: Neither 'docker compose' nor 'docker-compose' found.${NC}"
    exit 1
fi

help() {
    echo -e "${GREEN}Context-Fabric Jetson Deployment Tool${NC}"
    echo ""
    echo "Using: $DOCKER_COMPOSE"
    echo ""
    echo "Usage: ./jetson.sh [COMMAND] [ARGS...]"
    echo ""
    echo "Commands:"
    echo "  build                     Build the robot container image locally (uses host network)"
    echo "  start <robot> [rti_ip]    Start a specific robot container"
    echo "                            <robot>: robot1 or robot2"
    echo "                            [rti_ip]: IP address of RTI host (optional, defaults to hardcoded value)"
    echo "  stop                      Stop and remove all containers defined in jetson compose file"
    echo "  logs                      Follow logs of running containers"
    echo "  help                      Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./jetson.sh build"
    echo "  ./jetson.sh start robot1"
    echo "  ./jetson.sh start robot2 192.168.1.50"
    echo ""
}

build() {
    echo -e "${YELLOW}Building Context-Fabric Robot image on Jetson...${NC}"
    # Use host network to avoid Jetson Docker bridge iptables issues
    docker build --network host -t context-fabric-fed -f Dockerfile.fed .
    echo -e "${GREEN}Build complete.${NC}"
}

start() {
    ROBOT_NAME=$1
    RTI_IP=$2

    if [ -z "$ROBOT_NAME" ]; then
        echo -e "${RED}Error: Robot name required.${NC}"
        help
        exit 1
    fi

    if [ -n "$RTI_IP" ]; then
        echo -e "${GREEN}Starting $ROBOT_NAME connecting to RTI at $RTI_IP...${NC}"
        export RTI_IP=$RTI_IP
    else
        echo -e "${GREEN}Starting $ROBOT_NAME using default RTI IP from compose file...${NC}"
    fi
    
    $DOCKER_COMPOSE -f $COMPOSE_FILE up -d $ROBOT_NAME
    
    echo -e "${GREEN}$ROBOT_NAME started. Logs:${NC}"
    $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f $ROBOT_NAME
}

stop() {
    echo -e "${YELLOW}Stopping Jetson containers...${NC}"
    $DOCKER_COMPOSE -f $COMPOSE_FILE down
    echo -e "${GREEN}Stopped.${NC}"
}

logs() {
    $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f
}

# Main command dispatcher
case "$1" in
    build)
        build
        ;;
    start)
        start $2 $3
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    help|*)
        help
        ;;
esac
