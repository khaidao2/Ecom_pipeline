# Suggested Commands

Primary interface is the `Makefile` — prefer these over raw `docker compose`:

- `make up` — start all services, wait 10s, run `scripts/init.sh`
- `make down` / `make restart`
- `make init` — re-run bootstrap (Vault secrets, MinIO buckets, Kafka topics, StarRocks DBs) without restarting containers
- `make ps` — container status
- `make logs` / `make logs-<service>` (e.g. `make logs-airflow`, matches compose service names in `mem:tech_stack`)
- `make clean` — `docker compose down -v` + wipe `volumes/*` (destructive — confirm with user before running)
- `make dbt-run` / `make dbt-test` — runs inside the `dbt` compose service
- `make gen-data` / `make gen-logs` — start/tail the Faker data generator
- `make vault-status`, `make minio-setup`, `make kafka-topics`, `make starrocks-shell` — service-specific one-offs
- `make airflow-ui` / `make flink-ui` / `make kafka-ui` / `make apicurio-ui` / `make minio-ui` — just print the URL, don't open a browser

No test suite, linter, or formatter configured yet at the Python level (no dev deps in `pyproject.toml`). `dbt test` is the only test command that currently exists (see `make dbt-test`).
