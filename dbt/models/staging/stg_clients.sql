{{ config(materialized='view') }}

SELECT
    toUInt64(client_id) AS client_id,
    toDateTime(registered_at) AS registered_at,
    toUInt32(channel_id) AS channel_id,
    toUInt32(city_id) AS city_id,
    -- Очистка города от опечаток
    multiIf(
        city_name IN ('Москва', 'москва', 'Moscow', 'Мск'), 'Москва',
        city_name IN ('Санкт-Петербург', 'Спб', 'СПб', 'SPb'), 'Санкт-Петербург',
        city_name IN ('Новосибирск', 'Нск'), 'Новосибирск',
        city_name IN ('Екатеринбург', 'Екб'), 'Екатеринбург',
        city_name IN ('Казань', 'казань'), 'Казань',
        city_name IN ('Нижний Новгород', 'НН', 'Nizhny'), 'Нижний Новгород',
        city_name IN ('Челябинск', 'Челяба'), 'Челябинск',
        city_name IN ('Самара', 'самара'), 'Самара',
        city_name IN ('Омск', 'Омскъ'), 'Омск',
        city_name IN ('Ростов-на-Дону', 'Ростов', 'Rostov'), 'Ростов-на-Дону',
        'Unknown'
    ) AS city_name_clean,
    segment,
    -- Извлекаем число из "25 лет"
    toUInt8OrZero(replaceRegexpAll(toString(age), '[^0-9]', '')) AS age,
    status,
    toDateTimeOrNull(churned_at) AS churned_at,
    email,
    phone
FROM {{ source('raw', 'raw_clients') }}
