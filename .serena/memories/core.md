# Stock Pipeline — Core

E-commerce/stock data pipeline: Kafka ingestion -> Flink stream processing -> StarRocks warehouse -> dbt transforms -> Airflow orchestration. Docker-compose-based local stack. Project name in configs is `ecom_stock_pipeline` / `ecom-pipeline` (dbt/vault paths), NOT `stock_pipeline` — don't assume naming consistency across configs.

Repo is largely scaffolding/stubs as of 2026-08: `dags/stock_dag.py` tasks are placeholder `print()` calls, `main.py` is the uv template default, `pyproject.toml` has no real deps yet, `README.md` is empty. Treat code here as work-in-progress, not a finished reference implementation.

Source map:
- `docker-compose.yml` — all services (see `mem:tech_stack` for list + ports)
- `scripts/init.sh` — post-`docker compose up` bootstrap (Vault secrets, MinIO buckets, Kafka topics, StarRocks DBs); idempotent, run via `make init`
- `dags/` — Airflow DAGs (`stock_dag.py`)
- `dbt/` — dbt project `ecom_stock_pipeline`, profile target `starrocks` (see `configs/dbt/profiles.yml`)
- `generators/data_generator.py` — Faker-based synthetic event generator (ecommerce events, orders, product catalog, web traffic, exchange rates, weather, news), runs as the `data-generator` compose service
- `schemas/*.avsc` — Avro schemas per Kafka topic; `schemas/registry/` — Python client for the Apicurio schema registry (`Registry` class)
- `configs/` — per-service config (vault, airflow, dbt, flink, starrocks, kafka)
- `secrets/` — local secret material (untracked-sensitive; check before reading/sharing)

For commands see `mem:suggested_commands`. For stack/versions see `mem:tech_stack`.
