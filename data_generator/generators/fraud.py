"""Генерация fraud-записей (raw_fraud) из транзакций с is_fraud=True."""

import numpy as np
import pandas as pd


FRAUD_TYPES = ["card_not_present", "account_takeover", "friendly_fraud"]
FRAUD_TYPE_WEIGHTS = [0.60, 0.30, 0.10]


def generate_fraud(
    transactions: pd.DataFrame,
    rng: np.random.Generator,
    end_date: str,
) -> pd.DataFrame:
    """Для каждой транзакции с is_fraud=True создаёт запись в raw_fraud.

    Args:
        transactions: DataFrame транзакций
        rng: numpy Generator
        end_date: конец периода

    Returns:
        DataFrame: fraud_id, tx_id, client_id, detected_at,
        fraud_type, amount, confirmed
    """
    columns = ["fraud_id", "tx_id", "client_id", "detected_at",
               "fraud_type", "amount", "confirmed"]

    if transactions.empty:
        return pd.DataFrame(columns=columns)

    fraud_tx = transactions[transactions["is_fraud"]].copy()
    if fraud_tx.empty:
        return pd.DataFrame(columns=columns)

    end_ts = pd.Timestamp(end_date)
    records = []

    for i, (_, tx) in enumerate(fraud_tx.iterrows(), start=1):
        detected = tx["tx_at"] + pd.Timedelta(days=int(rng.integers(1, 8)))
        if detected >= end_ts:
            detected = end_ts - pd.Timedelta(hours=1)

        fraud_type = str(rng.choice(FRAUD_TYPES, p=FRAUD_TYPE_WEIGHTS))
        confirmed = bool(rng.random() < 0.8)

        records.append({
            "fraud_id": i,
            "tx_id": int(tx["tx_id"]),
            "client_id": int(tx["client_id"]),
            "detected_at": detected,
            "fraud_type": fraud_type,
            "amount": float(tx["amount"]) if pd.notna(tx["amount"]) else None,
            "confirmed": confirmed,
        })

    return pd.DataFrame(records, columns=columns)
