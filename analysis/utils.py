"""Утилиты для анализа: подключение к ClickHouse."""

import clickhouse_connect
import pandas as pd

def get_client():
    """Возвращает клиент ClickHouse (подключение к localhost)."""
    return clickhouse_connect.get_client(
        host="localhost",
        port=8123,
        username="analyst",
        password="analyst_pass",
        database="neobank"
    )

def fetch_df(query: str) -> pd.DataFrame:
    """Выполняет SQL-запрос и возвращает DataFrame."""
    client = get_client()
    try:
        result = client.query_df(query)
        return result
    finally:
        client.close()
