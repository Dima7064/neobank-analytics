"""«Грязь» в raw-данных: пропуски, дубликаты, TZ, опечатки.

В реальной жизни raw-слой — это НЕ чистые данные. Задача ETL (Спринт 2) —
разобраться с этой грязью. Здесь мы её симулируем.
"""

import numpy as np
import pandas as pd


CITY_VARIANTS = {
    "Москва":            ["Москва", "москва", "Moscow", "Мск"],
    "Санкт-Петербург":   ["Санкт-Петербург", "Спб", "СПб", "SPb"],
    "Новосибирск":       ["Новосибирск", "Нск"],
    "Екатеринбург":      ["Екатеринбург", "Екб"],
    "Казань":            ["Казань", "казань"],
    "Нижний Новгород":   ["Нижний Новгород", "НН", "Nizhny"],
    "Челябинск":         ["Челябинск", "Челяба"],
    "Самара":            ["Самара", "самара"],
    "Омск":              ["Омск", "Омскъ"],
    "Ростов-на-Дону":    ["Ростов-на-Дону", "Ростов", "Rostov"],
}


def _pick_variant(city_name: str, rng: np.random.Generator) -> str:
    if city_name in CITY_VARIANTS:
        return str(rng.choice(CITY_VARIANTS[city_name]))
    return city_name


def _format_amount_as_string(value) -> str:
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return str(value)


def apply_dirt(data: dict, rng: np.random.Generator) -> dict:
    """Применяет грязь к raw-таблицам.

    Что делаем:
    - clients: добавляем email (5% NULL), phone (15% NULL),
      city_name с опечатками, age — 2% как "N лет"
    - transactions: 1% amount как строка "1 500", 0.05% дубликатов,
      TZ для transfer — в UTC (сдвиг -3 часа)
    - events: 0.1% дубликатов

    Returns:
        Тот же dict, но с модифицированными raw-таблицами
    """
    clients = data["raw_clients"].copy()
    transactions = data["raw_transactions"].copy()
    events = data["raw_events"].copy()

    geo = data["dim_geography"]
    city_name_map = dict(zip(geo["city_id"], geo["city_name"]))

    # 1. email — 5% NULL
    emails = [f"client{cid}@example.com" for cid in clients["client_id"]]
    mask_email = rng.random(len(clients)) < 0.05
    for i in np.where(mask_email)[0]:
        emails[i] = None
    clients["email"] = emails

    # 2. phone — 15% NULL
    phones = [f"+79{i:09d}" for i in rng.integers(0, 10**9, size=len(clients))]
    mask_phone = rng.random(len(clients)) < 0.15
    for i in np.where(mask_phone)[0]:
        phones[i] = None
    clients["phone"] = phones

    # 3. city_name с опечатками
    clients["city_name"] = [
        _pick_variant(city_name_map.get(int(cid), ""), rng)
        for cid in clients["city_id"]
    ]

    # 4. age — 2% как строка "N лет"
    ages = clients["age"].astype(object)
    mask_age = rng.random(len(clients)) < 0.02
    for i in np.where(mask_age)[0]:
        try:
            ages.iloc[i] = f"{int(ages.iloc[i])} лет"
        except (ValueError, TypeError):
            pass
    clients["age"] = ages

    # 5. transactions: TZ для transfer — сдвиг -3 часа (Moscow -> UTC)
    if not transactions.empty:
        mask_transfer = transactions["tx_type"] == "transfer"
        transactions.loc[mask_transfer, "tx_at"] = (
            transactions.loc[mask_transfer, "tx_at"] - pd.Timedelta(hours=3)
        )
        transactions.loc[mask_transfer, "date_id"] = (
            transactions.loc[mask_transfer, "tx_at"].dt.normalize()
        )

    # 6. transactions: amount — 1% как строка
    if not transactions.empty:
        amounts = transactions["amount"].astype(object)
        mask_amt = rng.random(len(transactions)) < 0.01
        for i in np.where(mask_amt)[0]:
            amounts.iloc[i] = _format_amount_as_string(amounts.iloc[i])
        transactions["amount"] = amounts

    # 7. transactions: 0.05% дубликатов
    if not transactions.empty:
        n_dup = max(1, int(len(transactions) * 0.0005))
        sample_idx = rng.choice(len(transactions), size=n_dup, replace=False)
        transactions = pd.concat(
            [transactions, transactions.iloc[sample_idx]],
            ignore_index=True,
        )

    # 8. events: 0.1% дубликатов
    if not events.empty:
        n_dup = max(1, int(len(events) * 0.001))
        sample_idx = rng.choice(len(events), size=n_dup, replace=False)
        events = pd.concat(
            [events, events.iloc[sample_idx]],
            ignore_index=True,
        )

    data["raw_clients"] = clients
    data["raw_transactions"] = transactions
    data["raw_events"] = events
    return data
