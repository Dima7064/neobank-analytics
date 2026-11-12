{{ config(materialized='table') }}

WITH first_tx AS (
    SELECT
        client_id,
        min(tx_date) AS cohort_date
    FROM {{ ref('stg_transactions') }}
    WHERE status = 'completed'
    GROUP BY client_id
),
activity AS (
    SELECT DISTINCT
        t.client_id,
        f.cohort_date,
        t.tx_date,
        dateDiff('day', f.cohort_date, t.tx_date) AS day_n
    FROM {{ ref('stg_transactions') }} t
    JOIN first_tx f ON t.client_id = f.client_id
    WHERE t.status = 'completed'
)
SELECT
    cohort_date,
    day_n,
    count(DISTINCT client_id) AS retained_users
FROM activity
WHERE day_n IN (0, 1, 7, 14, 30)
GROUP BY cohort_date, day_n
ORDER BY cohort_date, day_n
