# ====== config ======
SHELL := /bin/bash
PROJECT ?= docuwise
ENV_FILE ?= .env

COMPOSE_DEV  := docker compose -f compose.dev.yaml --env-file $(ENV_FILE)
COMPOSE_PROD := docker compose -f compose.prod.yaml --env-file $(ENV_FILE)

# Image tags (tweak registry later for CI)
REG ?= local
API_IMG ?= $(REG)/docuwise-api:latest
UI_IMG  ?= $(REG)/docuwise-ui:latest

API_URL ?= http://localhost:8000/health
UI_URL  ?= http://localhost:3000

CURL := curl -fsS --max-time 5

.PHONY: help \
        dev-up dev-down dev-restart dev-logs dev-ps dev-build dev-rebuild \
        dev-api-logs dev-ui-logs \
        prod-up prod-down prod-restart prod-logs prod-ps prod-build prod-rebuild \
        prod-api-logs prod-ui-logs \
        images prune mongo-sh \
        smoke health check lint test format

help:
	@echo "Targets:"
	@echo "  Dev:   dev-up|dev-down|dev-restart|dev-logs|dev-ps|dev-build|dev-rebuild"
	@echo "         dev-api-logs|dev-ui-logs"
	@echo "  Prod:  prod-up|prod-down|prod-restart|prod-logs|prod-ps|prod-build|prod-rebuild"
	@echo "         prod-api-logs|prod-ui-logs"
	@echo "  QA:    health|smoke|check"
	@echo "  Misc:  images|prune|mongo-sh|lint|test|format"

# ====== DEV ======
dev-up:
	$(COMPOSE_DEV) up -d

dev-down:
	$(COMPOSE_DEV) down

dev-restart:
	$(COMPOSE_DEV) down
	$(COMPOSE_DEV) up -d

dev-logs:
	$(COMPOSE_DEV) logs -f --tail=200

dev-api-logs:
	$(COMPOSE_DEV) logs -f --tail=200 api

dev-ui-logs:
	$(COMPOSE_DEV) logs -f --tail=200 ui

dev-ps:
	$(COMPOSE_DEV) ps

dev-build:
	$(COMPOSE_DEV) build

dev-rebuild:
	$(COMPOSE_DEV) build --no-cache
	$(COMPOSE_DEV) up -d --force-recreate

# ====== PROD ======
prod-up:
	$(COMPOSE_PROD) up -d

prod-down:
	$(COMPOSE_PROD) down -v

prod-restart:
	$(COMPOSE_PROD) down -v
	$(COMPOSE_PROD) up -d

prod-logs:
	$(COMPOSE_PROD) logs -f --tail=200

prod-api-logs:
	$(COMPOSE_PROD) logs -f --tail=200 api

prod-ui-logs:
	$(COMPOSE_PROD) logs -f --tail=200 ui

prod-ps:
	$(COMPOSE_PROD) ps

prod-build:
	$(COMPOSE_PROD) build

prod-rebuild:
	$(COMPOSE_PROD) build --no-cache
	$(COMPOSE_PROD) up -d --force-recreate

# ====== QA ======
# Health checks both API and UI; fails fast with non-zero exit if either is down.
health:
	@echo "🔎 Checking API: $(API_URL)"
	@$(CURL) "$(API_URL)" >/dev/null && echo "✅ API healthy" || (echo "❌ API health failed"; exit 1)
	@echo "🔎 Checking UI:  $(UI_URL)"
	@$(CURL) "$(UI_URL)"  >/dev/null && echo "✅ UI reachable" || (echo "❌ UI check failed"; exit 1)

# End-to-end smoke test (script lives in scripts/e2e_smoke.py)
smoke:
	python scripts/e2e_smoke.py

smoke_ingest:
	python scripts/e2e_ingest.py

# Full prod sanity: up → health → smoke → down
check:
	@$(MAKE) prod-up
	@$(MAKE) health
	@$(MAKE) smoke
	@$(MAKE) prod-down

# ====== images & cleanup ======
images:
	docker images | grep docuwise || true

prune:
	docker system prune -f

# Optional: quick mongo shell (adjust service name if different)
mongo-sh:
	docker exec -it $$(docker ps --filter "name=$(PROJECT)_mongo" --format "{{.ID}}" | head -n1) mongosh || \
	echo "Couldn't find a running mongo container with name $(PROJECT)_mongo"

# ====== Lint / Test / Format (tweak paths/tools as needed) ======
lint:
	ruff check app || true

test:
	pytest -q

format:
	ruff check --select I --fix app
	isort app
	black app
