-- Какие продукты чаще всего покупают вместе?
-- Используем arrayJoin, чтобы "развернуть" массивы продуктов
WITH exploded AS (
    SELECT
        client_id,
        arrayJoin(product_types) AS product
    FROM neobank_marts.dm_cross_sell
    WHERE products_count >= 2
)
SELECT
    p1.product AS product_1,
    p2.product AS product_2,
    count(DISTINCT p1.client_id) AS clients_with_both
FROM exploded p1
JOIN exploded p2 ON p1.client_id = p2.client_id
WHERE p1.product < p2.product -- Избегаем зеркальных пар
GROUP BY product_1, product_2
ORDER BY clients_with_both DESC;
