"""Генерация клиентов (raw_clients) и их статусов.

Клиент — центральная сущность. От него зависят счета, карты, транзакции, события.
"""

import numpy as np
import pandas as pd

from data_generator.scenarios.monthly_growth import get_monthly_growth, get_channel_shares
from data_generator.scenarios.storyline import get_monthly_metrics


def generate_clients(
    n_clients: int,
    start_date: str,
    end_date: str,
    rng: np.random.Generator,
    dim_geography: pd.DataFrame,
    dim_channels: pd.DataFrame,
) -> pd.DataFrame:
    """Генерирует клиентов, распределяя их по месяцам согласно сюжету.

    Args:
        n_clients: сколько клиентов всего
        start_date: "2024-01-01"
        end_date: "2024-12-31"
        rng: numpy Generator
        dim_geography: справочник городов
        dim_channels: справочник каналов

    Returns:
        DataFrame с колонками: client_id, registered_at, channel_id, city_id,
        segment, age, month (служебное)
    """
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date)

    growth = get_monthly_growth()
    growth["clients_in_month"] = (
        growth["weight"] / growth["weight"].sum() * n_clients
    ).round().astype(int)
    diff = n_clients - growth["clients_in_month"].sum()
    growth.loc[growth.index[-1], "clients_in_month"] += diff

    geo_weights = dim_geography["population"].values.astype(float)
    geo_weights /= geo_weights.sum()
    geo_ids = dim_geography["city_id"].values

    channel_name_to_id = dict(zip(dim_channels["channel_name"], dim_channels["channel_id"]))

    hour_weights = np.array([
        2, 1, 1, 1, 1, 2, 4, 6, 8, 9, 8, 8,
        8, 8, 8, 8, 9, 10, 10, 9, 8, 6, 4, 3,
    ], dtype=float)
    hour_weights /= hour_weights.sum()

    records = []
    client_id = 1

    for _, row in growth.iterrows():
        month = int(row["month"])
        n_month = int(row["clients_in_month"])
        if n_month <= 0:
            continue

        month_start = pd.Timestamp(year=start_ts.year, month=month, day=1)
        if month == 12:
            month_end = end_ts
        else:
            next_month = pd.Timestamp(year=start_ts.year, month=month + 1, day=1)
            month_end = next_month - pd.Timedelta(days=1)
        days_in_month = (month_end - month_start).days + 1

        day_weights = np.linspace(2.0, 1.0, days_in_month)
        day_weights /= day_weights.sum()

        day_offsets = rng.choice(days_in_month, size=n_month, p=day_weights)
        hours = rng.choice(24, size=n_month, p=hour_weights)
        minutes = rng.integers(0, 60, size=n_month)

        regs = pd.to_datetime([
            month_start + pd.Timedelta(days=int(d), hours=int(h), minutes=int(m))
            for d, h, m in zip(day_offsets, hours, minutes)
        ])

        shares = get_channel_shares(row["dominant_channels"])
        channel_names = rng.choice(
            list(shares.keys()), size=n_month, p=list(shares.values())
        )
        channel_ids = [channel_name_to_id[ch] for ch in channel_names]

        segments = rng.choice(
            ["young", "family", "premium"],
            size=n_month,
            p=[float(row["young_share"]), float(row["family_share"]), float(row["premium_share"])],
        )
        city_ids = rng.choice(geo_ids, size=n_month, p=geo_weights)

        ages = np.empty(n_month, dtype=int)
        for i, seg in enumerate(segments):
            if seg == "young":
                ages[i] = rng.integers(18, 26)
            elif seg == "family":
                ages[i] = rng.integers(26, 46)
            else:
                ages[i] = rng.integers(46, 70)

        for i in range(n_month):
            records.append({
                "client_id": client_id,
                "registered_at": regs[i],
                "channel_id": int(channel_ids[i]),
                "city_id": int(city_ids[i]),
                "segment": segments[i],
                "age": int(ages[i]),
                "month": month,
            })
            client_id += 1

    return pd.DataFrame(records)


def finalize_clients_status(
    clients: pd.DataFrame,
    end_date: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Добавляет статус, churned_at, will_activate, lifespan_days.

    Логика:
    - activation_rate по месяцу регистрации → will_activate
    - d7_retention, d30_retention → lifespan_days
    - если lifespan истёк до конца года → churned
    - 5% — blocked
    """
    end_ts = pd.Timestamp(end_date)
    metrics = get_monthly_metrics().set_index("month")

    n = len(clients)
    activation_p = clients["month"].map(metrics["activation_rate"]).values.astype(float)
    d7_p = clients["month"].map(metrics["d7_retention"]).values.astype(float)
    d30_p = clients["month"].map(metrics["d30_retention"]).values.astype(float)

    will_activate = rng.random(n) < activation_p
    retain_d7 = rng.random(n) < d7_p
    retain_d30 = rng.random(n) < d30_p

    lifespan = np.zeros(n, dtype=int)
    lifespan[will_activate & ~retain_d7] = 7
    lifespan[will_activate & retain_d7 & ~retain_d30] = 30

    long_lived = np.where(will_activate & retain_d7 & retain_d30)[0]
    for i in long_lived:
        days = (end_ts - clients.iloc[i]["registered_at"]).days
        lifespan[i] = max(days, 30)

    status = np.full(n, "active", dtype=object)
    churned_at = pd.Series([pd.NaT] * n, index=clients.index)

    for i in range(n):
        if lifespan[i] > 0:
            churn_date = clients.iloc[i]["registered_at"] + pd.Timedelta(days=int(lifespan[i]))
            if churn_date < end_ts:
                status[i] = "churned"
                churned_at.iloc[i] = churn_date
        else:
            churn_date = clients.iloc[i]["registered_at"] + pd.Timedelta(days=30)
            if churn_date < end_ts:
                status[i] = "churned"
                churned_at.iloc[i] = churn_date

    blocked_mask = rng.random(n) < 0.05
    status[blocked_mask] = "blocked"

    clients = clients.copy()
    clients["will_activate"] = will_activate
    clients["lifespan_days"] = lifespan
    clients["status"] = status
    clients["churned_at"] = churned_at
    return clients
