{{ config(materialized='table') }}

WITH ab_users AS (
    SELECT client_id, experiment_id, group
    FROM {{ ref('stg_ab_assignments') }}
),
user_metrics AS (
    SELECT
        a.experiment_id,
        a.group,
        a.client_id,
        count(t.tx_id) AS tx_count,
        sum(t.amount) AS gmv
    FROM ab_users a
    LEFT JOIN {{ ref('stg_transactions') }} t ON a.client_id = t.client_id
    GROUP BY a.experiment_id, a.group, a.client_id
)
SELECT
    experiment_id,
    group,
    count(DISTINCT client_id) AS users,
    avg(tx_count) AS avg_tx_per_user,
    avg(gmv) AS arpu
FROM user_metrics
GROUP BY experiment_id, group
ORDER BY experiment_id, group
