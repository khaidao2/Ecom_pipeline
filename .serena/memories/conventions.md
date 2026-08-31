# Conventions

- Compose service/volume naming: `<component>-<role>` (e.g. `postgres-airflow`, `starrocks-fe`, `zookeeper-data`); Kafka topics use kebab-case matching schema files under `schemas/` (e.g. `ecommerce-events`, `exchange-rates`).
- Vault kv paths namespaced `secret/ecom-pipeline/<category>` (database, minio, kafka) — extend this prefix for new secrets rather than inventing a new root.
- dbt layering: staging (1:1 source views) -> intermediate (ephemeral) -> marts (materialized tables in `analytics` schema). Follow this when adding models; see `dbt/dbt_project.yml`.
- `scripts/init.sh` functions are idempotent (`|| true`, `--if-not-exists`) — new bootstrap steps should follow that pattern so `make init` stays safely re-runnable.
- Naming inconsistency to be aware of: repo/dir is `stock_pipeline` but internal configs (dbt profile, vault paths, StarRocks DBs, docker-compose comments) use `ecom` / `ecom-pipeline` / `ecom_data` — don't "fix" this without checking with the user, it's pervasive across configs.
