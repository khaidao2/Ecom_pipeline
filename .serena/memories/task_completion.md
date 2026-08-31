# Task Completion Checklist

No CI, linter, formatter, or Python test suite configured yet. When a task touches:
- **dbt models**: run `make dbt-run` then `make dbt-test` (requires `make up` + `make init` already done, since StarRocks must be initialized).
- **generators/data_generator.py**: sanity-check by running `make gen-data` then `make gen-logs` to confirm it produces events without crashing.
- **Airflow DAGs**: no automated DAG validation configured — visually check via `make airflow-ui` (http://localhost:8080).
- **docker-compose.yml / scripts/init.sh**: `make restart` then `make init`, verify with `make ps` and `make logs-<service>`.

If the user adds real Python dependencies/tooling (ruff, pytest, mypy, etc.) to `pyproject.toml`, update this memory with the resulting commands.
