"""Сценарий роста: сколько клиентов приходит каждый месяц,
какие сегменты и каналы доминируют.
"""

import pandas as pd


def get_monthly_growth() -> pd.DataFrame:
    """Возвращает таблицу с весами роста по месяцам.

    Веса — относительные (1.0 = базовый месяц). Абсолютное число клиентов
    в месяц = total_clients * weight / sum(weights).
    Так один и тот же сценарий работает и для 100k, и для 500k клиентов.

    Returns:
        DataFrame с колонками:
        - month: 1..12
        - weight: относительный вес (растёт от 1.0 до 5.4)
        - young_share, family_share, premium_share: доли сегментов (сумма = 1)
        - dominant_channels: список каналов, доминирующих в месяце
    """
    return pd.DataFrame([
        {"month": 1,  "weight": 1.00, "young_share": 0.40, "family_share": 0.45, "premium_share": 0.15, "dominant_channels": ["paid_search", "social"]},
        {"month": 2,  "weight": 1.25, "young_share": 0.38, "family_share": 0.47, "premium_share": 0.15, "dominant_channels": ["paid_search", "social"]},
        {"month": 3,  "weight": 1.67, "young_share": 0.36, "family_share": 0.48, "premium_share": 0.16, "dominant_channels": ["social", "referral"]},
        {"month": 4,  "weight": 2.08, "young_share": 0.35, "family_share": 0.49, "premium_share": 0.16, "dominant_channels": ["social", "referral"]},
        {"month": 5,  "weight": 2.50, "young_share": 0.33, "family_share": 0.50, "premium_share": 0.17, "dominant_channels": ["referral", "organic"]},
        {"month": 6,  "weight": 2.92, "young_share": 0.32, "family_share": 0.50, "premium_share": 0.18, "dominant_channels": ["referral", "organic"]},
        {"month": 7,  "weight": 3.33, "young_share": 0.31, "family_share": 0.51, "premium_share": 0.18, "dominant_channels": ["organic", "referral"]},
        {"month": 8,  "weight": 3.75, "young_share": 0.30, "family_share": 0.51, "premium_share": 0.19, "dominant_channels": ["organic", "social"]},
        {"month": 9,  "weight": 4.17, "young_share": 0.30, "family_share": 0.51, "premium_share": 0.19, "dominant_channels": ["organic", "social"]},
        {"month": 10, "weight": 4.58, "young_share": 0.29, "family_share": 0.52, "premium_share": 0.19, "dominant_channels": ["organic", "referral"]},
        {"month": 11, "weight": 5.00, "young_share": 0.29, "family_share": 0.52, "premium_share": 0.19, "dominant_channels": ["organic", "referral"]},
        {"month": 12, "weight": 5.42, "young_share": 0.28, "family_share": 0.52, "premium_share": 0.20, "dominant_channels": ["organic", "referral"]},
    ])


# Базовые доли каналов (если канал не доминирующий, но всё равно используется)
BASE_CHANNEL_SHARES = {
    "organic":     0.20,
    "paid_search": 0.20,
    "social":      0.20,
    "referral":    0.20,
    "partner":     0.20,
}

# Множитель для доминирующего канала
DOMINANT_CHANNEL_MULTIPLIER = 2.0


def get_channel_shares(dominant_channels: list) -> dict:
    """Возвращает распределение каналов для месяца (сумма = 1).

    Доминирующие каналы получают множитель, остальные — базовый вес.
    """
    weights = {}
    for channel, base_share in BASE_CHANNEL_SHARES.items():
        if channel in dominant_channels:
            weights[channel] = base_share * DOMINANT_CHANNEL_MULTIPLIER
        else:
            weights[channel] = base_share
    total = sum(weights.values())
    return {ch: w / total for ch, w in weights.items()}
