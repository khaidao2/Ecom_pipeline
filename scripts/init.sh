#!/bin/bash
# ===========================================
# Ecom Stock Pipeline - Initialization Script
# ===========================================
set -e

echo "=========================================="
echo "  Ecom Stock Pipeline - Service Init"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ==========================================
# 1. Vault Secrets
# ==========================================
init_vault() {
    log_info "Initializing Vault secrets..."
    
    export VAULT_ADDR="http://localhost:8200"
    export VAULT_TOKEN="dev-root-token"
    
    vault secrets enable -path=secret kv-v2 2>/dev/null || true
    
    vault kv put secret/ecom-pipeline/database \
        starrocks_host="starrocks-fe" \
        starrocks_port="9030" \
        starrocks_user="root" \
        starrocks_password="" \
        postgres_host="postgres-airflow" \
        postgres_port="5432" \
        postgres_user="airflow" \
        postgres_password="airflow"
    
    vault kv put secret/ecom-pipeline/minio \
        endpoint="minio:9000" \
        access_key="minioadmin" \
        secret_key="minioadmin" \
        bucket="ecom-raw"
    
    vault kv put secret/ecom-pipeline/kafka \
        bootstrap_servers="kafka:9092"
    
    log_info "Vault secrets initialized!"
}

# ==========================================
# 2. MinIO Buckets
# ==========================================
init_minio() {
    log_info "Initializing MinIO buckets..."
    
    local count=0
    while [ $count -lt 60 ]; do
        if docker compose exec minio mc ready local 2>/dev/null; then break; fi
        sleep 2
        count=$((count + 2))
    done
    
    docker compose exec minio mc alias set myminio http://localhost:9000 minioadmin minioadmin 2>/dev/null || true
    
    docker compose exec minio mc mb myminio/ecom-raw 2>/dev/null || true
    docker compose exec minio mc mb myminio/ecom-processed 2>/dev/null || true
    docker compose exec minio mc mb myminio/ecom-analytics 2>/dev/null || true
    
    log_info "MinIO buckets initialized!"
}

# ==========================================
# 3. Kafka Topics
# ==========================================
init_kafka() {
    log_info "Initializing Kafka topics..."
    
    local topics=("ecommerce-events" "orders" "product-catalog" "web-traffic" "exchange-rates" "weather" "news")
    
    for topic in "${topics[@]}"; do
        docker compose exec kafka kafka-topics \
            --bootstrap-server localhost:9092 \
            --create --if-not-exists \
            --topic "$topic" \
            --partitions 3 \
            --replication-factor 1
    done
    
    log_info "Kafka topics created:"
    docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
}

# ==========================================
# 4. StarRocks Database
# ==========================================
init_starrocks() {
    log_info "Initializing StarRocks database..."
    
    local count=0
    while [ $count -lt 120 ]; do
        if docker compose exec starrocks-fe curl -s http://localhost:8030/api/health 2>/dev/null | grep -q "OK"; then break; fi
        sleep 3
        count=$((count + 3))
    done
    
    docker compose exec starrocks-fe mysql -h127.0.0.1 -P9030 -uroot \
        -e "CREATE DATABASE IF NOT EXISTS ecom_data;" 2>/dev/null || true
    
    docker compose exec starrocks-fe mysql -h127.0.0.1 -P9030 -uroot \
        -e "CREATE DATABASE IF NOT EXISTS ecom_analytics;" 2>/dev/null || true
    
    log_info "StarRocks database initialized!"
}

# ==========================================
# Main
# ==========================================
main() {
    echo ""
    log_info "Starting initialization..."
    echo ""
    
    if ! docker compose ps | grep -q "running"; then
        log_error "Docker compose not running! Run: docker compose up -d"
        exit 1
    fi
    
    init_vault
    init_minio
    init_kafka
    init_starrocks
    
    echo ""
    echo "=========================================="
    log_info "All services initialized!"
    echo "=========================================="
    echo ""
    echo "  Airflow:     http://localhost:8080 (admin/admin)"
    echo "  Vault:       http://localhost:8200 (dev-root-token)"
    echo "  MinIO:       http://localhost:9001 (minioadmin/minioadmin)"
    echo "  Flink:       http://localhost:8081"
    echo "  Kafka UI:    http://localhost:8086"
    echo "  Apicurio:    http://localhost:8085"
    echo "  StarRocks:   localhost:9030"
    echo "  Kafka:       localhost:9092"
    echo "  Data:        ./volumes/raw-data/"
    echo ""
}

main "$@"
