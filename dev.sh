#!/bin/bash

#========================================
# 1. Defining the Format & Colors
#========================================
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

#========================================
# 2. Defining the Helper Functions
#========================================
show_help() {
    echo -e "${YELLOW}Fintech Ledger API - Dev Control Panel${NC}"
    echo "Usage: ./dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  up      Start the Docker databases and launch the FastAPI server"
    echo "  test    Start the Docker databases and run the Pytest suite and teardown"
    echo "  down    Safely stop and remove all the background Docker containers"
    echo "  help    Display this menu"
}

check_env(){
    if [ ! -f .env]; then
        echo - e "${RED}Error: .env file not found. Please create one before starting.${NC}"
        exit 1
    fi
}

wait_for_postgres() {
    echo -e "${YELLOW}Waiting for PostgreSQL to initialize...${NC}"
    # Startup waits until Docker confirms that the container is healthy & accepting connections
    # We sleep for 4 seconds to allow the internal Postgres engine to fully boot
    sleep 4
    echo -e "${GREEN}PostgreSQL Vaults are online and accepting connections!${NC}"
}

#========================================
# 3. Command Routing Logic
#========================================
case "$1" in
    up)
        check_env
        echo -e "${GREEN}Spinnig up the database infrastructure...${NC}"
        sudo docker compose --env-file .env up -d

        wait_for_postgres

        echo -e "${GREEN}Launching Uvicorn server...${NC}"
        uv run uvicorn app.main:app --reload
        ;;
    
    test)
        check_env
        echo -e "${YELLOW}Preparing Isolated Test Environment...${NC}"
        sudo docker compose --env-file .env up -d

        wait_for_postgres

        echo -e "${GREEN}Executing Pytest Suite...${NC}"
        uv run pytest tests/

        echo -e "${YELLOW}Tearing down the Test Environment...${NC}"
        sudo docker compose down
        echo -e "${GREEN}Test cycle complete. Infrastructure spun down safely.${NC}"
        ;;
    
    down)
        ehco -e "${YELLOW}Spinning down all database infrastructure...${NC}"
        sudo docker compose down
        echo -e "${GREEN}All background processes stopped. Memory freed.${NC}"
        ;;
    
    help|*)
        show_help
        ;;
esac