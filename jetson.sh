#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COMPOSE_FILE="docker-compose.jetson.yml"

build() {
    echo -e "${YELLOW}Building Context-Fabric Robot image on Jetson...${NC}"
    # Use host network to avoid Jetson Docker bridge iptables issues
    docker build --network host -t context-fabric-fed -f Dockerfile.fed .
    echo -e "${GREEN}Build complete.${NC}"
}

start() {
    ROBOT_NAME=$1
    RTI_IP=$2

    if [ -z "$ROBOT_NAME" ] || [ -z "$RTI_IP" ]; then
        echo -e "${RED}Usage: ./jetson.sh start <robot1|robot2> <RTI_IP_ADDRESS>${NC}"
        echo "Example: ./jetson.sh start robot1 192.168.1.50"
        exit 1
    fi

    echo -e "${GREEN}Starting $ROBOT_NAME connecting to RTI at $RTI_IP...${NC}"
    
    # Export RTI IP for docker-compose interpolation
    export RTI_IP=$RTI_IP
    
    docker compose -f $COMPOSE_FILE up -d $ROBOT_NAME
    
    echo -e "${GREEN}$ROBOT_NAME started. Logs:${NC}"
    docker compose -f $COMPOSE_FILE logs -f $ROBOT_NAME
}

stop() {
    echo -e "${YELLOW}Stopping Jetson containers...${NC}"
    docker compose -f $COMPOSE_FILE down
    echo -e "${GREEN}Stopped.${NC}"
}

logs() {
    docker compose -f $COMPOSE_FILE logs -f
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
    *)
        echo "Usage: $0 {build|start <robot> <rti_ip>|stop|logs}"
        exit 1
        ;;
esac

