
"""Копирование таблиц из Postgres (schema raw) в ClickHouse (database neobank).

Все колонки в ClickHouse — Nullable(String) (raw-слой, без приведения типов).
Приведение типов и очистка — задача dbt (staging).

Использование как модуля:
    from etl.copy_raw_to_ch import copy_table, copy_all
    copy_table("raw_clients")
    copy_all()
"""

import logging

import clickhouse_connect
import pandas as pd
from sqlalchemy import create_engine, text

from etl.config import POSTGRES, CLICKHOUSE, TABLES

log = logging.getLogger(__name__)


def get_pg_engine():
    """SQLAlchemy engine для Postgres (psycopg2 + utf8)."""
    url = (
        f"postgresql+psycopg2://{POSTGRES['user']}:{POSTGRES['password']}"
        f"@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['dbname']}"
        f"?client_encoding=utf8"
    )
    return create_engine(url)


def get_ch_client():
    """ClickHouse client (HTTP)."""
    return clickhouse_connect.get_client(
        host=CLICKHOUSE["host"],
        port=CLICKHOUSE["port"],
        username=CLICKHOUSE["user"],
        password=CLICKHOUSE["password"],
        database=CLICKHOUSE["database"],
    )


def _get_columns(pg_engine, table_name: str) -> list:
    """Возвращает список колонок таблицы в Postgres."""
    with pg_engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table "
            "ORDER BY ordinal_position"
        ), {"schema": POSTGRES["schema"], "table": table_name}).fetchall()
    return [r[0] for r in rows]


def _to_str_or_none(x):
    """Приводит значение к строке, но None/NaN/NaT оставляет как None."""
    if x is None:
        return None
    try:
        if pd.isna(x):
            return None
    except (TypeError, ValueError):
        pass
    return str(x)


def copy_table(table_name: str, batch_size: int = 50_000) -> int:
    """Копирует одну таблицу Postgres → ClickHouse.

    Таблица в ClickHouse создаётся заново (DROP + CREATE) со всеми
    Nullable(String)-колонками. Затем читаем Postgres чанками и вставляем.

    Returns:
        Число скопированных строк.
    """
    pg = get_pg_engine()
    ch = get_ch_client()

    try:
        col_names = _get_columns(pg, table_name)
        if not col_names:
            log.warning("Table %s not found in Postgres, skipping", table_name)
            return 0

        # Создаём таблицу в ClickHouse заново: все колонки Nullable(String)
        cols_ddl = ", ".join(f"`{c}` Nullable(String)" for c in col_names)
        ch.command(f"DROP TABLE IF EXISTS {table_name}")
        ch.command(
            f"CREATE TABLE {table_name} ({cols_ddl}) "
            f"ENGINE = MergeTree ORDER BY tuple()"
        )

        total = 0
        query = f"SELECT * FROM {POSTGRES['schema']}.{table_name}"

        with pg.connect() as conn:
            for chunk in pd.read_sql(query, conn, chunksize=batch_size):
                # Приводим все значения к строкам, сохраняя None для NULL
                chunk = chunk.astype(object)
                for c in chunk.columns:
                    chunk[c] = chunk[c].apply(_to_str_or_none)

                ch.insert(table_name, chunk.values.tolist(), column_names=col_names)
                total += len(chunk)
                log.info("%s: %s rows copied", table_name, total)

        log.info("DONE %s: %s rows", table_name, total)
        return total

    finally:
        ch.close()
        pg.dispose()


def copy_all(tables=None) -> dict:
    """Копирует все таблицы из конфига. Возвращает словарь table → rows."""
    if tables is None:
        tables = TABLES
    results = {}
    for t in tables:
        try:
            results[t] = copy_table(t)
        except Exception as e:
            log.exception("Failed to copy %s: %s", t, e)
            results[t] = f"ERROR: {e}"
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    res = copy_all()
    for t, n in res.items():
        print(f"{t:30s} {n}")