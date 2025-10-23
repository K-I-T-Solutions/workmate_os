#!/bin/bash
# WorkmateOS Migration Helper Script
# Place this in: backend/migrate.sh

set -e

# Ensure we're in the backend directory where alembic.ini lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verify we're in the right place
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}Error: alembic.ini not found. Are you in the backend/ directory?${NC}"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

function print_usage() {
    echo -e "${YELLOW}WorkmateOS Database Migration Helper${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  create <message>  - Create new migration"
    echo "  upgrade          - Apply all pending migrations"
    echo "  downgrade <-1>   - Rollback migrations (default: -1)"
    echo "  current          - Show current revision"
    echo "  history          - Show migration history"
    echo "  init             - Initialize alembic (first time only)"
    echo ""
}

function ensure_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${RED}Error: venv not found. Run 'python -m venv venv' first.${NC}"
        exit 1
    fi
    source venv/bin/activate
}

case "$1" in
    create)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Migration message required${NC}"
            echo "Example: $0 create \"Create core tables\""
            exit 1
        fi
        ensure_venv
        echo -e "${GREEN}Creating migration: $2${NC}"
        alembic revision --autogenerate -m "$2"
        ;;
    
    upgrade)
        ensure_venv
        echo -e "${GREEN}Applying migrations...${NC}"
        alembic upgrade head
        echo -e "${GREEN}✓ Migrations applied successfully${NC}"
        ;;
    
    downgrade)
        ensure_venv
        STEPS="${2:--1}"
        echo -e "${YELLOW}Rolling back $STEPS migration(s)...${NC}"
        alembic downgrade "$STEPS"
        echo -e "${GREEN}✓ Rollback complete${NC}"
        ;;
    
    current)
        ensure_venv
        alembic current
        ;;
    
    history)
        ensure_venv
        alembic history --verbose
        ;;
    
    init)
        ensure_venv
        echo -e "${GREEN}Initializing Alembic...${NC}"
        alembic init alembic
        echo -e "${YELLOW}⚠ Don't forget to configure alembic.ini and env.py${NC}"
        ;;
    
    *)
        print_usage
        exit 1
        ;;
esac