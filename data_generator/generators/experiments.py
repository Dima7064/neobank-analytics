"""Генерация A/B экспериментов (raw_experiments, raw_ab_assignments)."""

import numpy as np
import pandas as pd


EXPERIMENTS_CONFIG = [
    {
        "experiment_id": 1,
        "name": "onboarding_v2",
        "start_month": 3,
        "end_month": 4,
        "control_share": 0.5,
        "primary_metric": "activation_rate",
        "hypothesis": "Упрощённый онбординг (3 шага) → +5 п.п. активации",
        "cohort": "new_in_window",
    },
    {
        "experiment_id": 2,
        "name": "cross_sell_banner",
        "start_month": 7,
        "end_month": 8,
        "control_share": 0.5,
        "primary_metric": "cross_sell_rate",
        "hypothesis": "Баннер cross-sell → +7 п.п. cross-sell",
        "cohort": "existing_before",
    },
    {
        "experiment_id": 3,
        "name": "cashback_5",
        "start_month": 9,
        "end_month": 10,
        "control_share": 0.5,
        "primary_metric": "d30_retention",
        "hypothesis": "Кэшбэк 5% → +3 п.п. retention",
        "cohort": "existing_before",
    },
    {
        "experiment_id": 4,
        "name": "srm_broken",
        "start_month": 11,
        "end_month": 11,
        "control_share": 0.52,
        "primary_metric": "arpu",
        "hypothesis": "Тест с нарушенным SRM (для тренировки)",
        "cohort": "existing_before",
    },
]


def generate_experiments(
    clients: pd.DataFrame,
    rng: np.random.Generator,
    start_date: str,
    end_date: str,
) -> tuple:
    """Генерирует эксперименты и распределение клиентов по группам.

    Returns:
        Кортеж (experiments_df, assignments_df):
        - experiments_df: experiment_id, name, start_date, end_date,
          control_share, primary_metric, hypothesis
        - assignments_df: experiment_id, client_id, group, assigned_at
    """
    start_ts = pd.Timestamp(start_date)

    experiments_records = []
    assignments_records = []

    for exp in EXPERIMENTS_CONFIG:
        exp_id = exp["experiment_id"]
        exp_start = pd.Timestamp(year=start_ts.year, month=exp["start_month"], day=1)
        if exp["end_month"] == 12:
            exp_end = pd.Timestamp(year=start_ts.year, month=12, day=31)
        else:
            exp_end = pd.Timestamp(year=start_ts.year, month=exp["end_month"] + 1, day=1)

        experiments_records.append({
            "experiment_id": exp_id,
            "name": exp["name"],
            "start_date": exp_start,
            "end_date": exp_end,
            "control_share": exp["control_share"],
            "primary_metric": exp["primary_metric"],
            "hypothesis": exp["hypothesis"],
        })

        if exp["cohort"] == "new_in_window":
            eligible = clients[
                (clients["registered_at"] >= exp_start)
                & (clients["registered_at"] < exp_end)
            ]
        else:
            eligible = clients[clients["registered_at"] < exp_start]

        for cid in eligible["client_id"]:
            group = "control" if rng.random() < exp["control_share"] else "treatment"
            assignments_records.append({
                "experiment_id": exp_id,
                "client_id": int(cid),
                "group": group,
                "assigned_at": exp_start,
            })

    experiments_df = pd.DataFrame(experiments_records)
    assignments_df = pd.DataFrame(assignments_records)
    return experiments_df, assignments_df
