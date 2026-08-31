# Tech Stack

- Python 3.12 (`.python-version`), package manager: `uv` (pyproject.toml has no deps yet — real deps will land under `dependencies = []`)
- Orchestration: Airflow (webserver :8080, admin/admin), CeleryExecutor (redis + postgres-airflow + worker/triggerer/scheduler)
- Streaming: Kafka + Zookeeper (broker :9092), schema registry = Apicurio (:8085) backed by postgres-apicurio, Kafka UI :8086
- Stream processing: Flink 1.18 (jobmanager/taskmanager, UI :8081) — invoked from Airflow via `DockerOperator`, not a persistent job
- Warehouse: StarRocks (FE :9030 mysql-protocol, FE HTTP :8030) — dbt target, database `ecom_data` (schema `analytics`) / `ecom_analytics`
- Transform: dbt-starrocks (mysql driver), project `ecom_stock_pipeline`, profile `ecom_stock_pipeline`, materializations: staging=view, intermediate=ephemeral, marts=table
- Object storage: MinIO (:9001 console), buckets `ecom-raw`, `ecom-processed`, `ecom-analytics`, minioadmin/minioadmin
- Secrets: Vault (:8200, dev-root-token), kv-v2 at `secret/ecom-pipeline/{database,minio,kafka}`
- Data generation: `generators/data_generator.py`, Faker 28.0.0, runs as `data-generator` compose service, writes to `./volumes/raw-data/`
- Avro schemas per topic in `schemas/*.avsc`; registry client in `schemas/registry/`

All service hostnames above (e.g. `starrocks-fe`, `kafka`, `minio`) are docker-compose service names — resolvable only from inside the compose network, use `localhost` + mapped port from the host.
