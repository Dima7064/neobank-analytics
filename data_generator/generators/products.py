"""Генерация связи клиент-продукт (raw_products).

Определяет, какие продукты получил клиент — используется для
cross-sell rate и для генерации счетов/карт.
"""

import numpy as np
import pandas as pd

from data_generator.scenarios.storyline import get_product_launch_schedule


def generate_products(
    clients: pd.DataFrame,
    rng: np.random.Generator,
    end_date: str,
) -> pd.DataFrame:
    """Генерирует продукты клиентов.

    Логика:
    - debit_card + account — у всех с регистрации
    - deposit — с 7-го месяца, если клиент зарегистрирован до 7-го месяца,
      вероятность 20%
    - credit_card — с 9-го месяца, вероятность 15%
    - consumer_loan — с 9-го месяца, вероятность 5%

    Returns:
        DataFrame: client_product_id, client_id, product_id,
        product_type, opened_at, closed_at, amount, status
    """
    end_ts = pd.Timestamp(end_date)
    start_year = clients["registered_at"].min().year

    launch = get_product_launch_schedule()
    deposit_start = pd.Timestamp(year=start_year, month=launch["deposit"], day=1)
    credit_card_start = pd.Timestamp(year=start_year, month=launch["credit_card"], day=1)
    consumer_loan_start = pd.Timestamp(year=start_year, month=launch["consumer_loan"], day=1)

    records = []
    product_id_counter = 1

    for _, client in clients.iterrows():
        cid = client["client_id"]
        reg = client["registered_at"]
        churned = client["status"] == "churned"
        closed_at = client["churned_at"] if churned else pd.NaT

        records.append({
            "client_product_id": product_id_counter,
            "client_id": cid,
            "product_id": 1,
            "product_type": "debit_card",
            "opened_at": reg,
            "closed_at": closed_at,
            "amount": None,
            "status": "closed" if churned else "active",
        })
        product_id_counter += 1

        records.append({
            "client_product_id": product_id_counter,
            "client_id": cid,
            "product_id": 2,
            "product_type": "account",
            "opened_at": reg,
            "closed_at": closed_at,
            "amount": None,
            "status": "closed" if churned else "active",
        })
        product_id_counter += 1

        if reg < deposit_start and rng.random() < 0.20:
            opened = deposit_start + pd.Timedelta(days=int(rng.integers(0, 180)))
            if opened < end_ts:
                records.append({
                    "client_product_id": product_id_counter,
                    "client_id": cid,
                    "product_id": 3,
                    "product_type": "deposit",
                    "opened_at": opened,
                    "closed_at": closed_at if churned else pd.NaT,
                    "amount": float(rng.integers(10_000, 1_000_000)),
                    "status": "closed" if churned else "active",
                })
                product_id_counter += 1

        if reg < credit_card_start and rng.random() < 0.15:
            opened = credit_card_start + pd.Timedelta(days=int(rng.integers(0, 120)))
            if opened < end_ts:
                records.append({
                    "client_product_id": product_id_counter,
                    "client_id": cid,
                    "product_id": 4,
                    "product_type": "credit_card",
                    "opened_at": opened,
                    "closed_at": closed_at if churned else pd.NaT,
                    "amount": float(rng.integers(30_000, 300_000)),
                    "status": "closed" if churned else "active",
                })
                product_id_counter += 1

        if reg < consumer_loan_start and rng.random() < 0.05:
            opened = consumer_loan_start + pd.Timedelta(days=int(rng.integers(0, 120)))
            if opened < end_ts:
                records.append({
                    "client_product_id": product_id_counter,
                    "client_id": cid,
                    "product_id": 5,
                    "product_type": "consumer_loan",
                    "opened_at": opened,
                    "closed_at": closed_at if churned else pd.NaT,
                    "amount": float(rng.integers(50_000, 1_000_000)),
                    "status": "closed" if churned else "active",
                })
                product_id_counter += 1

    return pd.DataFrame(records)
