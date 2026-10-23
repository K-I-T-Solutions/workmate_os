.PHONY: help dev-up dev-down dev-logs dev-rebuild infra-up shell db-shell migrate-create migrate-up migrate-down migrate-current migrate-history migrate-auto backend-rebuild db-reset seed check-env

COMPOSE = docker compose -f infra/docker-compose.yml
# Nur die WorkmateOS-Dienste – infra/ enthält auch geteilte Infrastruktur (Postgres, Keycloak, Caddy, n8n …)
SERVICES = backend ui-v3
BACKEND_SERVICE = backend
BACKEND = workmate_backend
DB = central_postgres

help:
	@echo "WorkmateOS - Docker Development Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev-up           - Start WorkmateOS (backend, ui-v3)"
	@echo "  make dev-down         - Stop WorkmateOS (backend, ui-v3)"
	@echo "  make dev-rebuild      - Rebuild & restart WorkmateOS"
	@echo "  make backend-rebuild  - Rebuild only backend"
	@echo "  make dev-logs         - Show live logs (backend, ui-v3)"
	@echo "  make infra-up         - Start ALL infra services (⚠️ shared stack)"
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
	$(COMPOSE) up -d $(SERVICES)
	@echo "✓ WorkmateOS started. Waiting for backend..."
	@sleep 3
	@echo "✓ Backend: http://localhost:8000"
	@echo "✓ Run 'make migrate-up' to apply database migrations"

# Nur stoppen, nicht 'down' – Container bleiben erhalten, geteilte Dienste laufen weiter
dev-down:
	$(COMPOSE) stop $(SERVICES)
	@echo "✓ WorkmateOS stopped (shared infra keeps running)"

dev-logs:
	$(COMPOSE) logs -f $(SERVICES)

dev-rebuild:
	$(COMPOSE) up -d --build $(SERVICES)
	@echo "✓ WorkmateOS rebuilt and restarted"

# Kompletter infra-Stack (auch Dienste anderer Projekte) – bewusst eigenes Target
infra-up:
	$(COMPOSE) up -d
	@echo "✓ All infra services started"

backend-rebuild:
	$(COMPOSE) up -d --build $(BACKEND_SERVICE)
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
