"""Конфиг подключений для ETL.

По умолчанию — docker-имена сервисов (postgres, clickhouse).
При локальном запуске вне Docker — переопредели через env:
    POSTGRES_HOST=localhost POSTGRES_PORT=5433 CH_HOST=localhost CH_PORT=8123
"""

import os

POSTGRES = {
    "host": os.environ.get("POSTGRES_HOST", "postgres"),
    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
    "user": os.environ.get("POSTGRES_USER", "analyst"),
    "password": os.environ.get("POSTGRES_PASSWORD", "analyst_pass"),
    "dbname": os.environ.get("POSTGRES_DB", "neobank"),
    "schema": os.environ.get("POSTGRES_SCHEMA", "raw"),
}

CLICKHOUSE = {
    "host": os.environ.get("CH_HOST", "clickhouse"),
    "port": int(os.environ.get("CH_PORT", "8123")),
    "user": os.environ.get("CH_USER", "analyst"),
    "password": os.environ.get("CH_PASSWORD", "analyst_pass"),
    "database": os.environ.get("CH_DB", "neobank"),
}

# Порядок важен: сначала справочники (dim_*), потом факты (raw_*).
# Тяжёлые таблицы (raw_transactions, raw_events) — в конце.
TABLES = [
    "dim_channels",
    "dim_geography",
    "dim_products",
    "dim_dates",
    "raw_clients",
    "raw_accounts",
    "raw_cards",
    "raw_products",
    "raw_experiments",
    "raw_ab_assignments",
    "raw_fraud",
    "raw_transactions",
    "raw_events",
]
