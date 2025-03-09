IMAGE_NAME = waitlist-api

COMPOSE_FILE = docker-compose.yml

PROD_WORKERS = 4

ENV ?= dev

.PHONY: up down clean logs ps rebuild cleanup dev prod run

up:
	docker-compose -f $(COMPOSE_FILE) up -d

down:
	docker-compose -f $(COMPOSE_FILE) down

clean:
	docker rmi $(IMAGE_NAME)

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

ps:
	docker-compose -f $(COMPOSE_FILE) ps

rebuild: down up

cleanup: down clean

dev:
	ENV=dev WORKERS=1 docker-compose -f $(COMPOSE_FILE) up -d

prod:
	ENV=prd WORKERS=$(PROD_WORKERS) docker-compose -f $(COMPOSE_FILE) up -d

run:
ifeq ($(ENV),dev)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else ifeq ($(ENV),prd)
	uvicorn app.main:app --host 0.0.0.0 --port 8000
else
	@echo "Invalid ENV value. Use 'dev' or 'prd'"
	@exit 1
endif
