
"""DAG: копирование raw_* таблиц из Postgres в ClickHouse.

Запускается вручную (schedule=None). Можно запустить:
    - через UI: кнопка Play
    - через CLI: airflow dags trigger dag_raw_to_ch
"""

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# etl/ примонтирован в /opt/airflow/etl
sys.path.insert(0, "/opt/airflow")

from etl.config import TABLES  # noqa: E402


def _copy_one(table_name: str) -> int:
    """Обёртка для импорта внутри задачи (ускоряет парсинг DAG)."""
    from etl.copy_raw_to_ch import copy_table
    return copy_table(table_name)


default_args = {
    "owner": "analyst",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="dag_raw_to_ch",
    description="Copy raw_* from Postgres to ClickHouse (no transformation)",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["etl", "raw", "postgres", "clickhouse"],
) as dag:

    prev = None
    for table in TABLES:
        task = PythonOperator(
            task_id=f"copy_{table}",
            python_callable=_copy_one,
            op_kwargs={"table_name": table},
        )
        if prev is not None:
            prev >> task
        prev = task