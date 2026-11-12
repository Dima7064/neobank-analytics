-- Retention по когортам (Pivot): сколько пользователей возвращается на 7, 14, 30 дни
SELECT
    cohort_date,
    maxIf(retained_users, day_n = 0) AS day_0,
    maxIf(retained_users, day_n = 7) AS day_7,
    maxIf(retained_users, day_n = 14) AS day_14,
    maxIf(retained_users, day_n = 30) AS day_30,
    round(maxIf(retained_users, day_n = 7) / nullIf(maxIf(retained_users, day_n = 0), 0) * 100, 2) AS ret_d7_pct,
    round(maxIf(retained_users, day_n = 30) / nullIf(maxIf(retained_users, day_n = 0), 0) * 100, 2) AS ret_d30_pct
FROM neobank_marts.dm_retention
GROUP BY cohort_date
ORDER BY cohort_date;
