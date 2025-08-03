PROJECT_NAME := ulinzi_assess
ENV_FILE := .env

DB_CONTAINER := db_service
DB_NAME := postgres
DB_USER := postgres

PYTEST := pytest

ifneq (,$(wildcard $(ENV_FILE)))
    include $(ENV_FILE)
    export $(shell sed 's/=.*//' $(ENV_FILE))
endif

.PHONY: help up down logs reset-db clean-db test rebuild

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

clean-db:
	docker compose down
	docker volume rm ulinzi_assess_db_data || true

test:
	docker compose run --rm backend sh -c "$(PYTEST) -v tests"

rebuild:
	docker compose down -v
	docker compose up -d --build
