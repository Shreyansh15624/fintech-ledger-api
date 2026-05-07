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
    echo "  up          Start the Docker databases and launch the FastAPI server"
    echo "  worker      Start the Celery background worker to process transfers"
    echo "  migrate     Apply any pending Alembic schema updates"
    echo "  test        Start the Docker databases and run the Pytest suite and teardown"
    echo "  down        Safely stop and remove all the background Docker containers"
    echo "  help        Display this menu"
}

check_env(){
    if [ ! -f .env ]; then
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
        sudo docker compose --env-file .env up -d db ledger_redis

        wait_for_postgres

        echo -e "${GREEN}Launching Uvicorn server...${NC}"
        uv run uvicorn app.main:app --reload
        ;;
    worker)
        check_env
        echo -e "${YELLOW}Booting the Celery Background Worker...${NC}"
        uv run celery -A app.worker.celery_app worker --loglevel=info
        ;;

    migrate)
        check_env
        echo -e "${YELLOW}Booting Primary Database for migration...${NC}"
        # By not specifying the service here, docker boots everything within the YAML
        sudo docker compose --env-file .env up -d

        wait_for_postgres

        echo -e "${GREEN}Applying Alembic Upgrades...${NC}"
        uv run alembic upgrade head
        echo -e "${GREEN}Schema is up to date!${NC}"
        ;;

    test)
        check_env
        echo -e "${YELLOW}Preparing Isolated Test Environment...${NC}"
        # Explicitly calling 'ledger_redis' alongside the 'test_db' so the tests don't crash
        sudo docker compose --env-file .env up -d test_db ledger_redis

        wait_for_postgres

        echo -e "${GREEN}Executing Pytest Suite...${NC}"
        uv run pytest tests/

        echo -e "${YELLOW}Tearing down the Test Environment...${NC}"
        sudo docker compose --env-file .env down
        echo -e "${GREEN}Test cycle complete. Infrastructure spun down safely.${NC}"
        ;;
    
    stress)
        echo -e "${YELLOW}Deploying the Locust Swarm Testing Dashboard...${NC}"
        ehco -e "${YELLOW}Open https://localhost:8089 in your browser after launch.${NC}"
        uv run locust -f load_tests/locustfile.py
        ;;

    down)
        echo -e "${YELLOW}Spinning down all database infrastructure...${NC}"
        # This command tears down evey container that's currently running 
        sudo docker compose --env-file .env down
        echo -e "${GREEN}All background processes stopped. Memory freed.${NC}"
        ;;
    
    help|*)
        show_help
        ;;
esac