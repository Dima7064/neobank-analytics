{{ config(materialized='view') }}

SELECT
    toUInt32(experiment_id) AS experiment_id,
    toUInt64(client_id) AS client_id,
    group,
    toDateTime(assigned_at) AS assigned_at
FROM {{ source('raw', 'raw_ab_assignments') }}
