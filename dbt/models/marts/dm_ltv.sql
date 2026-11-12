{{ config(materialized='table') }}

SELECT
    t.client_id,
    c.segment,
    count(t.tx_id) AS total_tx,
    sum(t.amount) AS total_gmv,
    avg(t.amount) AS avg_check,
    max(t.tx_date) AS last_tx_date
FROM {{ ref('stg_transactions') }} t
JOIN {{ ref('stg_clients') }} c ON t.client_id = c.client_id
WHERE t.status = 'completed'
GROUP BY t.client_id, c.segment
