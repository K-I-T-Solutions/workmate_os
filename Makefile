.PHONY: help dev-up dev-down dev-logs dev-rebuild shell db-shell migrate-create migrate-up migrate-down migrate-current migrate-history migrate-auto backend-rebuild db-reset seed check-env

COMPOSE = docker-compose -f infra/docker-compose.yml
BACKEND = backend
DB = central_postgres

help:
	@echo "WorkmateOS - Docker Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up           - Start all services"
	@echo "  make dev-down         - Stop all services"
	@echo "  make dev-rebuild      - Rebuild & restart all services"
	@echo "  make backend-rebuild  - Rebuild only backend"
	@echo "  make dev-logs         - Show live logs"
	@echo "  make shell            - Open backend shell"
	@echo "  make db-shell         - Open PostgreSQL shell"
	@echo ""
	@echo "Database Migrations:"
	@echo "  make migrate-create MSG='message' - Create new migration"
	@echo "  make migrate-auto MSG='message'   - Create & apply migration"
	@echo "  make migrate-up                   - Apply all migrations"
	@echo "  make migrate-down                 - Rollback one migration"
	@echo "  make migrate-current              - Show current revision"
	@echo "  make migrate-history              - Show migration history"
	@echo "  make db-reset                     - Drop & recreate DB (⚠️ destructive)"
	@echo ""
	@echo "Utilities:"
	@echo "  make check-env       - Check DATABASE_URL & Alembic revision"
	@echo "  make seed            - Load seed data"
	@echo ""

# Dev Lifecycle
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

backend-rebuild:
	docker compose -f infra/docker-compose.yml up -d --build $(BACKEND)
	@echo "✓ Backend rebuilt"

shell:
	docker exec -it $(BACKEND) bash

db-shell:
	docker exec -it $(DB) psql -U workmate -d workmate_os

# Migrations
migrate-create:
ifndef MSG
	@echo "❌ Error: MSG required"
	@echo "Usage: make migrate-create MSG='Add CRM module'"
	@exit 1
endif
	docker exec $(BACKEND) alembic revision --autogenerate -m "$(MSG)"
	@echo "✓ Migration created"

migrate-auto:
ifndef MSG
	@echo "❌ Error: MSG required"
	@echo "Usage: make migrate-auto MSG='Add CRM module'"
	@exit 1
endif
	docker exec $(BACKEND) alembic revision --autogenerate -m "$(MSG)"
	docker exec $(BACKEND) alembic upgrade head
	@echo "✓ Migration created & applied"

migrate-up:
	docker exec $(BACKEND) alembic upgrade head
	@echo "✓ Migrations applied successfully"

migrate-down:
	docker exec $(BACKEND) alembic downgrade -1
	@echo "✓ Migration rolled back"

migrate-current:
	docker exec $(BACKEND) alembic current

migrate-history:
	docker exec $(BACKEND) alembic history --verbose

db-reset:
	docker exec -it $(DB) psql -U workmate -d workmate_os -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	docker exec $(BACKEND) alembic upgrade head
	@echo "⚠️ Database reset complete"

check-env:
	docker exec $(BACKEND) printenv | grep DATABASE_URL
	docker exec $(BACKEND) alembic current

seed:
	docker exec $(BACKEND) python -m app.core.seed || true
	@echo "✓ Seed data loaded"
