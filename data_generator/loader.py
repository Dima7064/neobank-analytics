
"""Загрузка raw-данных в PostgreSQL (схема raw).

В raw-слое все колонки хранятся как TEXT — это «data lake» стиль.
Приведение типов — задача ETL (Спринт 2).

Драйвер psycopg2 указан явно (postgresql+psycopg2://), иначе SQLAlchemy 2.x
пытается импортировать psycopg (v3). Параметр ?client_encoding=utf8 —
чтобы psycopg2 не падал на UnicodeDecodeError при получении сообщений об
ошибках от Postgres в CP1251 (типично для Windows с русской локалью).
"""

import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text


def get_engine(db_config: dict) -> sa.Engine:
    """Создаёт SQLAlchemy engine для Postgres (psycopg2 + utf8)."""
    url = (
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
        f"?client_encoding=utf8"
    )
    return create_engine(url)


def ensure_schema(engine: sa.Engine, schema: str) -> None:
    """Создаёт схему, если её нет."""
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))


def prepare_for_raw_load(df: pd.DataFrame) -> pd.DataFrame:
    """Приводит все колонки к object, NaN/NaT → None, datetime → строка."""
    df = df.copy()
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].apply(
                lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else None
            )
        else:
            df[col] = df[col].astype(object).where(df[col].notna(), None)
    return df


def load_table(
    df: pd.DataFrame,
    table_name: str,
    engine: sa.Engine,
    schema: str,
    batch_size: int,
) -> None:
    """Загружает DataFrame в таблицу schema.table_name (пересоздаёт)."""
    if df is None or df.empty:
        print(f"  {table_name}: 0 rows (skip)")
        return

    df_prepared = prepare_for_raw_load(df)
    dtype_map = {col: sa.Text() for col in df_prepared.columns}

    with engine.begin() as conn:
        df_prepared.to_sql(
            table_name,
            conn,
            schema=schema,
            if_exists="replace",
            index=False,
            chunksize=batch_size,
            dtype=dtype_map,
        )
    print(f"  {table_name}: {len(df_prepared):,} rows")


def load_all_to_raw(data: dict, db_config: dict, batch_size: int = 5000) -> None:
    """Загружает все DataFrame из data в схему raw."""
    engine = get_engine(db_config)
    schema = db_config["schema"]
    ensure_schema(engine, schema)

    dim_keys = [k for k in data if k.startswith("dim_")]
    raw_keys = [k for k in data if k.startswith("raw_")]

    print(f"  Loading {len(dim_keys)} dimension tables...")
    for key in dim_keys:
        load_table(data[key], key, engine, schema, batch_size)

    print(f"  Loading {len(raw_keys)} raw tables...")
    for key in raw_keys:
        load_table(data[key], key, engine, schema, batch_size)