.PHONY: help setup build start stop logs clean test

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Fraud Detection System - Available Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $1, $2}' $(MAKEFILE_LIST)

setup: ## Complete system setup
	@echo "$(GREEN)Starting system setup...$(NC)"
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	@docker-compose build

start: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	@docker-compose up -d

start-infra: ## Start infrastructure services only
	@echo "$(GREEN)Starting infrastructure services...$(NC)"
	@docker-compose up -d postgres redis kafka neo4j minio qdrant

start-app: ## Start application services only
	@echo "$(GREEN)Starting application services...$(NC)"
	@docker-compose up -d api inference enricher graph-builder trainer dashboard

start-monitoring: ## Start monitoring stack
	@echo "$(GREEN)Starting monitoring stack...$(NC)"
	@docker-compose --profile monitoring up -d

start-simulator: ## Start transaction simulator
	@echo "$(GREEN)Starting transaction simulator...$(NC)"
	@docker-compose --profile simulation up -d

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@docker-compose down

stop-all: ## Stop all services and remove volumes
	@echo "$(RED)Stopping all services and removing volumes...$(NC)"
	@docker-compose down -v

logs: ## Show logs for all services
	@docker-compose logs -f

logs-api: ## Show API service logs
	@docker-compose logs -f api

logs-inference: ## Show inference service logs
	@docker-compose logs -f inference

status: ## Show service status
	@docker-compose ps

health: ## Check service health
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -s http://localhost:8080/health | jq . || echo "API not responding"
	@curl -s http://localhost:8080/ready | jq . || echo "API not ready"

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	@python -m pytest tests/ -v

test-api: ## Test API endpoints
	@echo "$(GREEN)Testing API endpoints...$(NC)"
	@curl -X POST http://localhost:8080/api/v1/score \
		-H "Content-Type: application/json" \
		-d '{"id": 123, "timestamp": "2024-01-15T14:30:00Z", "card_id": "test_card", "merchant_id": "test_merchant", "amount": 100.0, "mcc": "5411"}'

generate-data: ## Generate sample data
	@echo "$(GREEN)Generating sample data...$(NC)"
	@python scripts/generate_sample_data.py

init-db: ## Initialize database
	@echo "$(GREEN)Initializing database...$(NC)"
	@python scripts/init_db.py

clean: ## Clean up Docker resources
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	@docker-compose down -v --remove-orphans
	@docker system prune -f

backup: ## Backup data
	@echo "$(GREEN)Creating backup...$(NC)"
	@./scripts/backup.sh

restore: ## Restore from backup
	@echo "$(GREEN)Restoring from backup...$(NC)"
	@./scripts/restore.sh

dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(NC)"
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

prod: ## Deploy production environment  
	@echo "$(GREEN)Deploying production environment...$(NC)"
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

update: ## Update services to latest images
	@echo "$(GREEN)Updating services...$(NC)"
	@docker-compose pull
	@docker-compose up -d

shell-api: ## Open shell in API container
	@docker-compose exec api bash

shell-db: ## Open shell in database container
	@docker-compose exec postgres psql -U fraud -d frauddb

dashboard: ## Open dashboard in browser
	@echo "$(GREEN)Opening dashboard...$(NC)"
	@open http://localhost:3000 || xdg-open http://localhost:3000

docs: ## Open API documentation
	@echo "$(GREEN)Opening API docs...$(NC)"
	@open http://localhost:8080/docs || xdg-open http://localhost:8080/docs

monitoring: ## Open monitoring dashboard
	@echo "$(GREEN)Opening Grafana...$(NC)"
	@open http://localhost:3001 || xdg-open http://localhost:3001