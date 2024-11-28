# Load environmnet variables from .env if it exists
ifneq (,$(wildcard .env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

# Variables
COMPOSE=docker compose
DEV_FILE=docker-compose.dev.yml
PROD_FILE=docker-compose.prod.yml

# Default environment
COMPOSE_FILE=$(DEV_FILE)

# Docker Publish Variables
IMAGE_NAME=medirag-image
TAG=latest

# Azure Variables
# Azure Container App
AZURE_REGISTRY_NAME=medirag-container-registry
AZURE_RESOURCE_GROUP=medirag-resources
AZURE_APP_NAME=medirag-app



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


# Docker Image Management
build:
	docker build -t $(IMAGE_NAME):$(TAG) .

tag:
	docker tag $(IMAGE_NAME):$(TAG) $(DOCKER_REGISTRY)/$(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

push: build tag
	docker push $(DOCKER_REGISTRY)/$(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Clean up local Docker images
clean-images:
	docker rmi -f $(IMAGE_NAME):$(TAG) $(DOCKER_REGISTRY)/$(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Full CI/CD Pipeline
release: push
	@echo "Image released: $(DOCKER_REGISTRY)/$(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)"


# GitHub Secrets Preparation
prepare-secrets:
	@echo "DOCKER_USERNAME=${DOCKER_USERNAME}" >> .github/workflows/.secrets
	@echo "DOCKER_PASSWORD=${DOCKER_PASSWORD}" >> .github/workflows/.secrets
	@echo "AZURE_CREDENTIALS=${AZURE_CREDENTIALS}" >> .github/workflows/.secrets
	@echo "AZURE_REGISTRY_NAME=${AZURE_REGISTRY_NAME}" >> .github/workflows/.secrets
	@echo "AZURE_RESOURCE_GROUP=${AZURE_RESOURCE_GROUP}" >> .github/workflows/.secrets
	@echo "AZURE_APP_NAME=${AZURE_APP_NAME}" >> .github/workflows/.secrets
	@echo "Secrets prepared for GitHub Actions"