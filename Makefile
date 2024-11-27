# Variables
COMPOSE=docker compose
DEV_FILE=docker-compose.dev.yml
PROD_FILE=docker-compose.prod.yml

# Default environment
COMPOSE_FILE=$(DEV_FILE)

# Development
dev-build:
	$(COMPOSE) -f $(DEV_FILE) up --build

dev-down:
	$(COMPOSE) -f $(DEV_FILE) down --volumes --remove-orphans

dev-logs:
	$(COMPOSE) -f $(DEV_FILE) logs -f

clean-dev:
	$(COMPOSE) -f $(DEV_FILE) down --volumes --remove-orphans


# Production
prod-build:
	$(COMPOSE) -f $(DEV_FILE) up --build -d

prod-down:
	$(COMPOSE) -f $(DEV_FILE) down --volumes --remove-orphans

prod-logs:
	$(COMPOSE) -f $(DEV_FILE) logs -f

clean-prod:
	$(COMPOSE) -f $(PROD_FILE) down --volumes --remove-orphans


# Catch-all clean
clean:
	@echo "Please specify the environment: clean-dev or clean-prod"
	@exit 1