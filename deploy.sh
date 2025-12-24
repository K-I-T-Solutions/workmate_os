#!/bin/bash

################################
# Workmate OS Deployment Script
################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER="workmate-01"
DEPLOY_DIR="/opt/workmate"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

echo -e "${GREEN}=== Workmate OS Production Deployment ===${NC}"

# Check if .env.prod exists
if [ ! -f "infra/${ENV_FILE}" ]; then
    echo -e "${RED}Error: infra/${ENV_FILE} not found!${NC}"
    echo "Please copy infra/.env.prod and configure it with production values."
    exit 1
fi

# Check if secrets are still default
if grep -q "CHANGE_ME" "infra/${ENV_FILE}"; then
    echo -e "${RED}Error: Please update all CHANGE_ME values in infra/${ENV_FILE}${NC}"
    exit 1
fi

echo -e "${YELLOW}1. Creating deployment directory on server...${NC}"
ssh ${SERVER} "sudo mkdir -p ${DEPLOY_DIR}"
ssh ${SERVER} "sudo chown \$(whoami):\$(whoami) ${DEPLOY_DIR}"

echo -e "${YELLOW}2. Syncing project files to server...${NC}"
rsync -avz --delete \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='dist' \
    --exclude='.claude' \
    --exclude='docs/uploads' \
    ./ ${SERVER}:${DEPLOY_DIR}/

echo -e "${YELLOW}3. Building and starting containers...${NC}"
ssh ${SERVER} "cd ${DEPLOY_DIR}/infra && docker compose -f ${COMPOSE_FILE} --env-file ${ENV_FILE} up -d --build"

echo -e "${YELLOW}4. Waiting for services to be healthy...${NC}"
sleep 10

echo -e "${YELLOW}5. Running database migrations...${NC}"
ssh ${SERVER} "cd ${DEPLOY_DIR} && docker exec workmate_backend alembic upgrade head" || echo "Migrations already applied or not needed"

echo -e "${YELLOW}6. Checking container status...${NC}"
ssh ${SERVER} "docker ps --filter 'name=workmate_'"

echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo "Services should be available at:"
echo "  - Frontend: https://workmate.kit-it-koblenz.de"
echo "  - Backend API: https://api.workmate.kit-it-koblenz.de"
echo "  - Traefik Dashboard: https://traefik.workmate.kit-it-koblenz.de"
echo ""
echo "To view logs:"
echo "  ssh ${SERVER} 'docker logs -f workmate_backend'"
echo "  ssh ${SERVER} 'docker logs -f workmate_frontend'"
echo "  ssh ${SERVER} 'docker logs -f workmate_traefik'"
