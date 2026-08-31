.PHONY: help up down restart init logs ps clean

# ===========================================
# Ecom Stock Pipeline - Makefile
# ===========================================

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	docker compose up -d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Running initialization..."
	@./scripts/init.sh

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose down
	docker compose up -d

init: ## Initialize services (Vault, MinIO, Kafka, StarRocks)
	@./scripts/init.sh

logs: ## View logs
	docker compose logs -f

logs-%: ## View logs for specific service (e.g., make logs-airflow)
	docker compose logs -f $*

ps: ## Show running containers
	docker compose ps

clean: ## Remove all containers and volumes
	docker compose down -v
	rm -rf volumes/*

# Service-specific commands
vault-status: ## Check Vault status
	@export VAULT_ADDR=http://localhost:8200 && vault status

minio-setup: ## Setup MinIO buckets
	@docker compose exec minio mc alias set myminio http://localhost:9000 minioadmin minioadmin
	@docker compose exec minio mc mb myminio/ecom-raw
	@docker compose exec minio mc mb myminio/ecom-processed
	@docker compose exec minio mc mb myminio/ecom-analytics

kafka-topics: ## List Kafka topics
	@docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

starrocks-shell: ## Connect to StarRocks shell
	@docker compose exec starrocks-fe mysql -h127.0.0.1 -P9030 -uroot

dbt-run: ## Run dbt models
	@docker compose run --rm dbt dbt run

dbt-test: ## Run dbt tests
	@docker compose run --rm dbt dbt test

flink-ui: ## Open Flink Web UI
	@echo "Flink UI: http://localhost:8081"

airflow-ui: ## Open Airflow Web UI
	@echo "Airflow UI: http://localhost:8080 (admin/admin)"

kafka-ui: ## Open Kafka Web UI
	@echo "Kafka UI: http://localhost:8086"

apicurio-ui: ## Open Apicurio Registry UI
	@echo "Apicurio UI: http://localhost:8085"

minio-ui: ## Open MinIO Console
	@echo "MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"

gen-data: ## Run data generator
	docker compose up -d data-generator

gen-logs: ## View data generator logs
	docker compose logs -f data-generator
