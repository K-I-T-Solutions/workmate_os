.PHONY: help dev-up dev-down dev-logs dev-rebuild migrate-create migrate-up migrate-down migrate-current migrate-history shell db-shell

help:
	@echo "WorkmateOS - Docker Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up        - Start all services"
	@echo "  make dev-down      - Stop all services"
	@echo "  make dev-rebuild   - Rebuild and restart"
	@echo "  make dev-logs      - Follow logs"
	@echo "  make shell         - Open backend shell"
	@echo "  make db-shell      - Open PostgreSQL shell"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make migrate-create MSG='message'  - Create new migration"
	@echo "  make migrate-up                    - Apply all migrations"
	@echo "  make migrate-down                  - Rollback one migration"
	@echo "  make migrate-current               - Show current revision"
	@echo "  make migrate-history               - Show migration history"
	@echo ""

# Docker Compose location
COMPOSE = docker-compose -f infra/docker-compose.yml

# Development
dev-up:
	$(COMPOSE) up -d
	@echo "✓ Services started. Waiting for backend..."
	@sleep 3
	@echo "✓ Backend: http://localhost:8000"
	@echo "✓ Run 'make migrate-up' to apply database migrations"

dev-down:
	$(COMPOSE) down

dev-logs:
	$(COMPOSE) logs -f

dev-rebuild:
	$(COMPOSE) up -d --build
	@echo "✓ Services rebuilt and restarted"

shell:
	docker exec -it workmate_backend bash

db-shell:
	docker exec -it central_postgres psql -U workmate -d workmate_os

# Migrations (executed inside Docker container)
migrate-create:
ifndef MSG
	@echo "❌ Error: MSG required"
	@echo "Usage: make migrate-create MSG='Create core tables'"
	@exit 1
endif
	docker exec workmate_backend alembic revision --autogenerate -m "$(MSG)"
	@echo "✓ Migration created. Check backend/alembic/versions/"

migrate-up:
	docker exec workmate_backend alembic upgrade head
	@echo "✓ Migrations applied successfully"

migrate-down:
	docker exec workmate_backend alembic downgrade -1
	@echo "✓ Migration rolled back"

migrate-current:
	docker exec workmate_backend alembic current

migrate-history:
	docker exec workmate_backend alembic history --verbose

# Seed data (for later)
seed:
	docker exec workmate_backend python -m app.core.seed
	@echo "✓ Seed data loaded"