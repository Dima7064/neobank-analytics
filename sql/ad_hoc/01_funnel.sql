-- Анализ воронки по месяцам: где теряются клиенты?
WITH monthly_funnel AS (
    SELECT
        toStartOfMonth(reg_date) AS month,
        sum(registered) AS registered,
        sum(verified) AS verified,
        sum(activated) AS activated,
        sum(got_product) AS got_product
    FROM neobank_marts.dm_funnel
    GROUP BY month
)
SELECT
    month,
    registered,
    verified,
    round(verified / nullIf(registered, 0) * 100, 2) AS cr_reg_ver_pct,
    activated,
    round(activated / nullIf(verified, 0) * 100, 2) AS cr_ver_act_pct,
    got_product,
    round(got_product / nullIf(activated, 0) * 100, 2) AS cr_act_prod_pct,
    round(activated / nullIf(registered, 0) * 100, 2) AS cr_reg_act_pct
FROM monthly_funnel
ORDER BY month;
