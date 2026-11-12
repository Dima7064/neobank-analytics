"""Генерация карт (raw_cards)."""

import numpy as np
import pandas as pd


def generate_cards(
    clients: pd.DataFrame,
    cross_sell: pd.DataFrame,
    rng: np.random.Generator,
    end_date: str,
) -> pd.DataFrame:
    """Генерирует карты.

    Каждый клиент получает дебетовую карту при регистрации (85% активируют).
    Кредитная карта — только если получил продукт credit_card.

    Returns:
        DataFrame: card_id, client_id, account_id, card_type,
        issued_at, activated_at, status
    """
    end_ts = pd.Timestamp(end_date)
    records = []
    card_id = 1

    cross_sell_map = cross_sell.groupby("client_id")["product_type"].apply(set).to_dict()

    for _, client in clients.iterrows():
        cid = client["client_id"]
        products = cross_sell_map.get(cid, set())

        issued = client["registered_at"] + pd.Timedelta(days=int(rng.integers(1, 8)))
        if issued >= end_ts:
            continue

        activated = pd.NaT
        status = "issued"
        if rng.random() < 0.85:
            activated = issued + pd.Timedelta(days=int(rng.integers(1, 15)))
            if activated < end_ts:
                status = "active"
                if rng.random() < 0.05:
                    status = "blocked"
            else:
                activated = pd.NaT

        records.append({
            "card_id": card_id,
            "client_id": cid,
            "card_type": "debit",
            "issued_at": issued,
            "activated_at": activated,
            "status": status,
        })
        card_id += 1

        if "credit_card" in products:
            issued_c = client["registered_at"] + pd.Timedelta(days=int(rng.integers(30, 200)))
            if issued_c < end_ts:
                activated_c = issued_c + pd.Timedelta(days=int(rng.integers(1, 15)))
                if activated_c < end_ts:
                    records.append({
                        "card_id": card_id,
                        "client_id": cid,
                        "card_type": "credit",
                        "issued_at": issued_c,
                        "activated_at": activated_c,
                        "status": "active",
                    })
                    card_id += 1

    return pd.DataFrame(records)
