FROM python:3.11-slim

WORKDIR /opt/dbt

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc default-libmysqlclient-dev build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
        dbt-core \
        dbt-starrocks

ENV DBT_PROFILES_DIR=/opt/dbt
ENV DBT_TARGET=starrocks

ENTRYPOINT ["dbt"]
