-- Сравнение LTV по сегментам клиентов
SELECT
    segment,
    count(DISTINCT client_id) AS clients,
    sum(total_tx) AS total_transactions,
    round(avg(total_tx), 1) AS avg_tx_per_client,
    round(avg(total_gmv), 2) AS avg_ltv,
    round(quantile(0.5)(total_gmv), 2) AS median_ltv,
    round(quantile(0.95)(total_gmv), 2) AS p95_ltv,
    round(max(total_gmv), 2) AS max_ltv
FROM neobank_marts.dm_ltv
GROUP BY segment
ORDER BY avg_ltv DESC;
