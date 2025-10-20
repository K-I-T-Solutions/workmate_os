SHELL := /bin/bash
COMPOSE := docker compose -f infra/docker-compose.yml

dev-up:
	$(COMPOSE) up -d --build

dev-down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f backend ui

restart:
	$(COMPOSE) restart backend ui

.PHONY: dev-up dev-down logs restart
