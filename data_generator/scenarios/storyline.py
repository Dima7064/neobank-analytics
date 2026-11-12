"""Сюжет продукта: параметры по месяцам.

Здесь — «правда» симуляции. Генераторы используют эти параметры,
чтобы данные воспроизводили нужную динамику метрик.
"""

import pandas as pd


def get_monthly_metrics() -> pd.DataFrame:
    """Возвращает целевую динамику ключевых метрик по месяцам.

    Генераторы подгоняют вероятности так, чтобы фактические метрики
    были близки к этим значениям.

    Returns:
        DataFrame с колонками:
        - month: 1..12
        - activation_rate: доля зарегистрировавшихся, кто сделал первую
          транзакцию в течение 14 дней
        - d7_retention, d30_retention: retention по когортам
        - cross_sell_rate: доля клиентов с 2+ продуктами
        - fraud_rate: доля fraud-транзакций
        - cac_rub: стоимость привлечения клиента
        - arpu_rub: средняя выручка на клиента в месяц
        - ltv_rub: средний LTV накопленным итогом
    """
    return pd.DataFrame([
        {"month": 1,  "activation_rate": 0.18, "d7_retention": 0.25, "d30_retention": 0.15, "cross_sell_rate": 0.05, "fraud_rate": 0.000, "cac_rub": 4000, "arpu_rub": 300,  "ltv_rub": 8000},
        {"month": 2,  "activation_rate": 0.20, "d7_retention": 0.27, "d30_retention": 0.17, "cross_sell_rate": 0.06, "fraud_rate": 0.000, "cac_rub": 4000, "arpu_rub": 350,  "ltv_rub": 9000},
        {"month": 3,  "activation_rate": 0.23, "d7_retention": 0.28, "d30_retention": 0.19, "cross_sell_rate": 0.07, "fraud_rate": 0.000, "cac_rub": 3500, "arpu_rub": 400,  "ltv_rub": 11000},
        {"month": 4,  "activation_rate": 0.26, "d7_retention": 0.30, "d30_retention": 0.21, "cross_sell_rate": 0.08, "fraud_rate": 0.000, "cac_rub": 3500, "arpu_rub": 450,  "ltv_rub": 13000},
        {"month": 5,  "activation_rate": 0.28, "d7_retention": 0.32, "d30_retention": 0.25, "cross_sell_rate": 0.08, "fraud_rate": 0.000, "cac_rub": 3200, "arpu_rub": 500,  "ltv_rub": 15000},
        {"month": 6,  "activation_rate": 0.30, "d7_retention": 0.33, "d30_retention": 0.26, "cross_sell_rate": 0.10, "fraud_rate": 0.001, "cac_rub": 3200, "arpu_rub": 550,  "ltv_rub": 16000},
        {"month": 7,  "activation_rate": 0.32, "d7_retention": 0.35, "d30_retention": 0.30, "cross_sell_rate": 0.18, "fraud_rate": 0.002, "cac_rub": 3000, "arpu_rub": 600,  "ltv_rub": 18000},
        {"month": 8,  "activation_rate": 0.33, "d7_retention": 0.36, "d30_retention": 0.33, "cross_sell_rate": 0.25, "fraud_rate": 0.003, "cac_rub": 3000, "arpu_rub": 650,  "ltv_rub": 20000},
        {"month": 9,  "activation_rate": 0.34, "d7_retention": 0.38, "d30_retention": 0.36, "cross_sell_rate": 0.30, "fraud_rate": 0.005, "cac_rub": 3000, "arpu_rub": 700,  "ltv_rub": 22000},
        {"month": 10, "activation_rate": 0.35, "d7_retention": 0.39, "d30_retention": 0.38, "cross_sell_rate": 0.33, "fraud_rate": 0.0015, "cac_rub": 2900, "arpu_rub": 750, "ltv_rub": 24000},
        {"month": 11, "activation_rate": 0.36, "d7_retention": 0.41, "d30_retention": 0.40, "cross_sell_rate": 0.36, "fraud_rate": 0.0015, "cac_rub": 2800, "arpu_rub": 800, "ltv_rub": 25000},
        {"month": 12, "activation_rate": 0.37, "d7_retention": 0.42, "d30_retention": 0.42, "cross_sell_rate": 0.38, "fraud_rate": 0.0015, "cac_rub": 2800, "arpu_rub": 850, "ltv_rub": 27000},
    ])


# Месяцы, с которых запускаются продукты (по сюжету)
DEPOSIT_START_MONTH = 7          # вклад
CREDIT_CARD_START_MONTH = 9      # кредитная карта
CONSUMER_LOAN_START_MONTH = 9    # потребкредит


def get_product_launch_schedule() -> dict:
    """Месяцы запуска продуктов (1-based)."""
    return {
        "debit_card": 1,
        "account": 1,
        "deposit": DEPOSIT_START_MONTH,
        "credit_card": CREDIT_CARD_START_MONTH,
        "consumer_loan": CONSUMER_LOAN_START_MONTH,
    }
