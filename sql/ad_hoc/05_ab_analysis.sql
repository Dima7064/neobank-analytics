-- Анализ результатов A/B тестов (ARPU и транзакции на пользователя)
SELECT
    experiment_id,
    group,
    users,
    round(avg_tx_per_user, 2) AS avg_tx,
    round(arpu, 2) AS arpu,
    -- Доля от общего числа пользователей в эксперименте
    round(users / sum(users) OVER (PARTITION BY experiment_id) * 100, 2) AS group_share_pct
FROM neobank_marts.dm_ab_results
ORDER BY experiment_id, group;
