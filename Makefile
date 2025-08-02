# Makefile for Ulinzi Assess Project

PROJECT_NAME := ulinzi_assess
DOCKER_COMPOSE_FILE := docker-compose.yml
ENV_FILE := .env
DB_CONTAINER := db_service
DB_NAME := db
DB_USER := postgres

PYTHON := python
PYTEST := pytest
POETRY := poetry

ifneq (,$(wildcard $(ENV_FILE)))
    include $(ENV_FILE)
    export $(shell sed 's/=.*//' $(ENV_FILE))
endif

.PHONY: help up down logs reset-db test rebuild

help: 
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: 
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d --build

down:
	docker compose -f $(DOCKER_COMPOSE_FILE) down

logs:
	docker compose -f $(DOCKER_COMPOSE_FILE) logs -f

clean-db: 
	docker exec -it $(DB_CONTAINER) psql -U $(DB_USER) -d $(DB_NAME) -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

test:
	docker compose build backend
	docker compose run --rm backend pytest


rebuild: 
	docker compose -f $(DOCKER_COMPOSE_FILE) down -v
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d --build

