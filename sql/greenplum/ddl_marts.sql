-- Пример DDL для Greenplum (MPP-архитектура).
-- В Greenplum данные распределяются по сегментам с помощью DISTRIBUTED BY.
-- Если этого не сделать, данные упадут в мастер-узел, и запросы будут медленными.

CREATE SCHEMA IF NOT EXISTS marts;

-- Витрина LTV. Распределяем по client_id, так как чаще всего группируем по клиенту.
CREATE TABLE marts.dm_ltv (
    client_id BIGINT,
    segment VARCHAR(50),
    total_tx BIGINT,
    total_gmv NUMERIC(18, 2),
    avg_check NUMERIC(18, 2),
    last_tx_date DATE
)
DISTRIBUTED BY (client_id)
PARTITION BY RANGE (last_tx_date)
(START ('2024-01-01') INCLUSIVE END ('2025-01-01') EXCLUSIVE EVERY ('1 month'));

-- Витрина воронки. Распределяем по дате.
CREATE TABLE marts.dm_funnel (
    reg_date DATE,
    registered BIGINT,
    verified BIGINT,
    activated BIGINT,
    got_product BIGINT
)
DISTRIBUTED BY (reg_date);

-- Пример аналитического запроса (MPP любит JOIN по ключу распределения)
SELECT
    l.segment,
    COUNT(DISTINCT l.client_id) AS users,
    SUM(l.total_gmv) AS gmv
FROM marts.dm_ltv l
JOIN marts.dm_funnel f ON l.last_tx_date = f.reg_date
GROUP BY l.segment;
