"""Генерация счетов клиентов (raw_accounts)."""

import numpy as np
import pandas as pd


def generate_accounts(
    clients: pd.DataFrame,
    cross_sell: pd.DataFrame,
    rng: np.random.Generator,
    end_date: str,
) -> pd.DataFrame:
    """Генерирует счета.

    Каждый клиент получает текущий счёт при регистрации.
    Вклад и кредитный счёт — только если клиент получил продукт (cross_sell).

    Args:
        clients: DataFrame клиентов
        cross_sell: DataFrame связи client_id → product_type (какие продукты получил)
        rng: numpy Generator
        end_date: конец периода

    Returns:
        DataFrame: account_id, client_id, account_type, opened_at,
        closed_at, balance, status
    """
    end_ts = pd.Timestamp(end_date)
    records = []
    account_id = 1

    balance_ranges = {
        "young":   (1_000, 50_000),
        "family":  (10_000, 500_000),
        "premium": (100_000, 5_000_000),
    }

    cross_sell_map = cross_sell.groupby("client_id")["product_type"].apply(set).to_dict()

    for _, client in clients.iterrows():
        cid = client["client_id"]
        seg = client["segment"]
        lo, hi = balance_ranges[seg]
        products = cross_sell_map.get(cid, set())

        churned = client["status"] == "churned"
        closed_at = client["churned_at"] if churned else pd.NaT

        records.append({
            "account_id": account_id,
            "client_id": cid,
            "account_type": "current",
            "opened_at": client["registered_at"],
            "closed_at": closed_at,
            "balance": float(rng.integers(lo, hi)),
            "status": "closed" if churned else ("blocked" if client["status"] == "blocked" else "active"),
        })
        account_id += 1

        if "deposit" in products:
            opened = client["registered_at"] + pd.Timedelta(days=int(rng.integers(0, 180)))
            if opened < end_ts:
                records.append({
                    "account_id": account_id,
                    "client_id": cid,
                    "account_type": "deposit",
                    "opened_at": opened,
                    "closed_at": closed_at if churned else pd.NaT,
                    "balance": float(rng.integers(10_000, 1_000_000)),
                    "status": "closed" if churned else "active",
                })
                account_id += 1

        if "credit_card" in products or "consumer_loan" in products:
            opened = client["registered_at"] + pd.Timedelta(days=int(rng.integers(0, 180)))
            if opened < end_ts:
                records.append({
                    "account_id": account_id,
                    "client_id": cid,
                    "account_type": "credit",
                    "opened_at": opened,
                    "closed_at": closed_at if churned else pd.NaT,
                    "balance": float(rng.integers(0, 300_000)),
                    "status": "closed" if churned else "active",
                })
                account_id += 1

    return pd.DataFrame(records)
