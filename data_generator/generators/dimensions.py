"""Генерация справочников (dim_*).

Справочники — это «медленно меняющиеся» сущности: каналы, города,
продукты, календарь. Они одинаковы для всех клиентов.
"""

import pandas as pd

from data_generator.scenarios.monthly_growth import get_channel_shares


def generate_dim_channels() -> pd.DataFrame:
    """5 каналов привлечения.

    Returns:
        DataFrame: channel_id, channel_name
    """
    return pd.DataFrame([
        {"channel_id": 1, "channel_name": "organic"},
        {"channel_id": 2, "channel_name": "paid_search"},
        {"channel_id": 3, "channel_name": "social"},
        {"channel_id": 4, "channel_name": "referral"},
        {"channel_id": 5, "channel_name": "partner"},
    ])


def generate_dim_geography() -> pd.DataFrame:
    """10 городов России с населением.

    Используется для распределения клиентов по городам
    пропорционально населению.

    Returns:
        DataFrame: city_id, city_name, region, population
    """
    return pd.DataFrame([
        {"city_id": 1,  "city_name": "Москва",            "region": "Москва",                  "population": 13_000_000},
        {"city_id": 2,  "city_name": "Санкт-Петербург",   "region": "Ленинградская область",   "population": 5_500_000},
        {"city_id": 3,  "city_name": "Новосибирск",       "region": "Новосибирская область",   "population": 1_600_000},
        {"city_id": 4,  "city_name": "Екатеринбург",      "region": "Свердловская область",    "population": 1_500_000},
        {"city_id": 5,  "city_name": "Казань",            "region": "Татарстан",               "population": 1_300_000},
        {"city_id": 6,  "city_name": "Нижний Новгород",   "region": "Нижегородская область",   "population": 1_200_000},
        {"city_id": 7,  "city_name": "Челябинск",         "region": "Челябинская область",     "population": 1_200_000},
        {"city_id": 8,  "city_name": "Самара",            "region": "Самарская область",       "population": 1_100_000},
        {"city_id": 9,  "city_name": "Омск",              "region": "Омская область",          "population": 1_100_000},
        {"city_id": 10, "city_name": "Ростов-на-Дону",    "region": "Ростовская область",      "population": 1_100_000},
    ])


def generate_dim_products() -> pd.DataFrame:
    """5 продуктов необанка.

    Returns:
        DataFrame: product_id, product_type, name, rate, limit_amount
    """
    return pd.DataFrame([
        {"product_id": 1, "product_type": "debit_card",     "name": "Дебетовая карта",   "rate": None, "limit_amount": None},
        {"product_id": 2, "product_type": "account",        "name": "Текущий счёт",      "rate": None, "limit_amount": None},
        {"product_id": 3, "product_type": "deposit",        "name": "Вклад «Копилка»",   "rate": 0.16, "limit_amount": None},
        {"product_id": 4, "product_type": "credit_card",    "name": "Кредитная карта",   "rate": 0.25, "limit_amount": 300_000},
        {"product_id": 5, "product_type": "consumer_loan",  "name": "Потребкредит",      "rate": 0.20, "limit_amount": 1_000_000},
    ])


def generate_dim_dates(start_date: str, end_date: str) -> pd.DataFrame:
    """Календарь на период.

    Нужен, чтобы не терять дни без данных (важно для retention и трендов).

    Args:
        start_date: "2024-01-01"
        end_date: "2024-12-31"

    Returns:
        DataFrame: date_id, year, month, day, weekday, is_weekend, is_holiday
    """
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    holidays = {
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8),  # новогодние
        (2, 23),   # День защитника Отечества
        (3, 8),    # 8 марта
        (5, 1),    # Праздник весны и труда
        (5, 9),    # День Победы
        (6, 12),   # День России
        (11, 4),   # День народного единства
    }
    df = pd.DataFrame({
        "date_id": dates,
        "year": dates.year,
        "month": dates.month,
        "day": dates.day,
        "weekday": dates.dayofweek + 1,          # 1 = понедельник, 7 = воскресенье
        "is_weekend": dates.dayofweek >= 5,      # суббота, воскресенье
    })
    df["is_holiday"] = df.apply(lambda r: (r["month"], r["day"]) in holidays, axis=1)
    return df


def generate_all_dimensions(start_date: str, end_date: str) -> dict:
    """Удобная обёртка: генерирует все справочники разом.

    Returns:
        dict с ключами: channels, geography, products, dates
    """
    return {
        "channels":  generate_dim_channels(),
        "geography": generate_dim_geography(),
        "products":  generate_dim_products(),
        "dates":     generate_dim_dates(start_date, end_date),
    }


# Экспорт на случай, если нужен только канал-шар для месяца
__all__ = [
    "generate_dim_channels",
    "generate_dim_geography",
    "generate_dim_products",
    "generate_dim_dates",
    "generate_all_dimensions",
    "get_channel_shares",
]
