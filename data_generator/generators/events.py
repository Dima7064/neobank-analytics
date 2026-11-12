"""Генерация событий (raw_events)."""

import numpy as np
import pandas as pd


def generate_events(
    clients: pd.DataFrame,
    cross_sell: pd.DataFrame,
    transactions: pd.DataFrame,
    rng: np.random.Generator,
    end_date: str,
) -> pd.DataFrame:
    """Генерирует события.

    Типы событий:
    - registration — 1 на клиента
    - verification — если will_activate
    - login — 2-10 в месяц в течение lifespan
    - view_product — 5-20 в месяц
    - open_product — для каждого cross-sell продукта
    - transaction — для каждой транзакции
    - churn — если status = churned

    Returns:
        DataFrame: event_id, client_id, event_type, event_at, date_id
    """
    end_ts = pd.Timestamp(end_date)
    records = []
    event_id = 1

    cross_sell_map = cross_sell.groupby("client_id")["product_type"].apply(list).to_dict()
    tx_by_client = transactions.groupby("client_id") if not transactions.empty else {}

    for _, client in clients.iterrows():
        cid = client["client_id"]
        reg = client["registered_at"]
        seg = client["segment"]
        lifespan = client["lifespan_days"]
        active = client["will_activate"]

        records.append({
            "event_id": event_id,
            "client_id": cid,
            "event_type": "registration",
            "event_at": reg,
            "date_id": reg.normalize(),
        })
        event_id += 1

        if active:
            ver_at = reg + pd.Timedelta(hours=int(rng.integers(1, 72)))
            if ver_at < end_ts:
                records.append({
                    "event_id": event_id,
                    "client_id": cid,
                    "event_type": "verification",
                    "event_at": ver_at,
                    "date_id": ver_at.normalize(),
                })
                event_id += 1

        if lifespan > 0:
            months_alive = max(lifespan / 30.0, 1.0)

            n_login = int(rng.integers(2, 11) * months_alive)
            for _ in range(n_login):
                day = int(rng.integers(0, lifespan))
                at = reg + pd.Timedelta(days=day, hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 60)))
                if at < end_ts:
                    records.append({
                        "event_id": event_id,
                        "client_id": cid,
                        "event_type": "login",
                        "event_at": at,
                        "date_id": at.normalize(),
                    })
                    event_id += 1

            n_view = int(rng.integers(5, 21) * months_alive)
            for _ in range(n_view):
                day = int(rng.integers(0, lifespan))
                at = reg + pd.Timedelta(days=day, hours=int(rng.integers(0, 24)), minutes=int(rng.integers(0, 60)))
                if at < end_ts:
                    records.append({
                        "event_id": event_id,
                        "client_id": cid,
                        "event_type": "view_product",
                        "event_at": at,
                        "date_id": at.normalize(),
                    })
                    event_id += 1

        products = cross_sell_map.get(cid, [])
        if "deposit" in products:
            at = reg + pd.Timedelta(days=int(rng.integers(60, 200)))
            if at < end_ts:
                records.append({
                    "event_id": event_id,
                    "client_id": cid,
                    "event_type": "open_product",
                    "event_at": at,
                    "date_id": at.normalize(),
                })
                event_id += 1
        if "credit_card" in products:
            at = reg + pd.Timedelta(days=int(rng.integers(120, 260)))
            if at < end_ts:
                records.append({
                    "event_id": event_id,
                    "client_id": cid,
                    "event_type": "open_product",
                    "event_at": at,
                    "date_id": at.normalize(),
                })
                event_id += 1

        if not transactions.empty and cid in tx_by_client.groups:
            for _, tx in tx_by_client.get_group(cid).iterrows():
                records.append({
                    "event_id": event_id,
                    "client_id": cid,
                    "event_type": "transaction",
                    "event_at": tx["tx_at"],
                    "date_id": tx["date_id"],
                })
                event_id += 1

        if client["status"] == "churned" and pd.notna(client["churned_at"]):
            at = client["churned_at"]
            if at < end_ts:
                records.append({
                    "event_id": event_id,
                    "client_id": cid,
                    "event_type": "churn",
                    "event_at": at,
                    "date_id": at.normalize(),
                })
                event_id += 1

    return pd.DataFrame(records)
