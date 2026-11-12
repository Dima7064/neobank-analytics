"""Генерация транзакций (raw_transactions)."""

import numpy as np
import pandas as pd

from data_generator.scenarios.storyline import get_monthly_metrics


FREQ_BY_SEGMENT = {
    "young":   (15, 25),
    "family":  (20, 30),
    "premium": (25, 40),
}

AMOUNT_PURCHASE = {
    "young":   (200, 2_000),
    "family":  (500, 5_000),
    "premium": (1_000, 20_000),
}

CATEGORIES = ["groceries", "transport", "entertainment", "utilities", "other"]
CATEGORY_WEIGHTS = [0.30, 0.20, 0.15, 0.15, 0.20]


def generate_transactions(
    clients: pd.DataFrame,
    cross_sell: pd.DataFrame,
    rng: np.random.Generator,
    end_date: str,
) -> pd.DataFrame:
    """Генерирует транзакции для каждого клиента.

    Логика:
    - Если lifespan_days == 0 — нет транзакций.
    - Первая транзакция: registered_at + 1-14 дней (если will_activate).
    - Частота зависит от сегмента.
    - Тип: purchase (60%), transfer (20%), payment (10%),
      withdrawal (5%), top_up (5%).
    - 0.5% — fraud, с учётом fraud_rate по месяцам.

    Returns:
        DataFrame: tx_id, client_id, account_id, card_id, date_id,
        tx_at, amount, tx_type, category, status, is_fraud
    """
    end_ts = pd.Timestamp(end_date)
    metrics = get_monthly_metrics().set_index("month")

    records = []
    tx_id = 1

    for _, client in clients.iterrows():
        if client["lifespan_days"] == 0 or not client["will_activate"]:
            continue

        cid = client["client_id"]
        seg = client["segment"]
        reg = client["registered_at"]

        first_tx_at = reg + pd.Timedelta(days=int(rng.integers(1, 15)))

        fmin, fmax = FREQ_BY_SEGMENT[seg]
        monthly_freq = int(rng.integers(fmin, fmax + 1))
        months_alive = client["lifespan_days"] / 30.0
        n_tx = int(monthly_freq * months_alive * rng.uniform(0.7, 1.3))
        if n_tx <= 0:
            continue

        day_offsets = rng.integers(0, int(client["lifespan_days"]), size=n_tx)
        hour_choices = rng.integers(0, 24, size=n_tx)
        minute_choices = rng.integers(0, 60, size=n_tx)

        for k in range(n_tx):
            tx_at = first_tx_at + pd.Timedelta(
                days=int(day_offsets[k]),
                hours=int(hour_choices[k]),
                minutes=int(minute_choices[k]),
            )
            if tx_at >= end_ts:
                continue

            month = (tx_at.year - reg.year) * 12 + tx_at.month
            if month < 1:
                month = 1
            if month > 12:
                month = 12
            fraud_rate = float(metrics.loc[month, "fraud_rate"]) if month in metrics.index else 0.0

            tx_type = rng.choice(
                ["purchase", "transfer", "payment", "withdrawal", "top_up"],
                p=[0.60, 0.20, 0.10, 0.05, 0.05],
            )

            if tx_type == "purchase":
                amin, amax = AMOUNT_PURCHASE[seg]
                amount = float(rng.integers(amin, amax))
                category = rng.choice(CATEGORIES, p=CATEGORY_WEIGHTS)
            elif tx_type == "payment":
                amount = float(rng.integers(500, 20_000))
                category = None
            elif tx_type == "transfer":
                amount = float(rng.integers(100, 50_000))
                category = None
            elif tx_type == "withdrawal":
                amount = float(rng.integers(1_000, 50_000))
                category = None
            else:  # top_up
                amount = float(rng.integers(500, 100_000))
                category = None

            status = rng.choice(["completed", "declined", "reversed"], p=[0.95, 0.03, 0.02])
            is_fraud = bool(rng.random() < fraud_rate)

            records.append({
                "tx_id": tx_id,
                "client_id": cid,
                "tx_at": tx_at,
                "date_id": tx_at.normalize(),
                "amount": amount,
                "tx_type": str(tx_type),
                "category": category,
                "status": str(status),
                "is_fraud": is_fraud,
            })
            tx_id += 1

    df = pd.DataFrame(records)
    return df
