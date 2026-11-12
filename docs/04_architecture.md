# Архитектура проекта NeoBank

## 1. Общая схема

```mermaid
flowchart LR
    A[Data Generator<br/>Python] -->|загрузка| B[(PostgreSQL<br/>Raw Layer)]
    B -->|Airflow DAG 1| C[Staging<br/>dbt]
    C -->|Airflow DAG 2| D[(ClickHouse<br/>DWH)]
    D -->|dbt models| E[(Data Marts<br/>dm_*)]
    E -->|SQL / API| F[Power BI]
    E -->|SQL / API| G[Superset]
    E -->|SQL / API| H[Metabase]
    E -->|выгрузка| I[Excel /<br/>Google Sheets]
    E -->|pandas| J[Python Analysis<br/>Jupyter]
    J --> K[ML Models<br/>scikit-learn]
    K -->|scores| D
    L[Greenplum<br/>код без запуска] -.->|документация| E


2. Слои и технологии
2.1. Источник данных (симуляция)
Инструмент: Python (pandas, numpy, Faker).

Что делает:

Генерирует данные за 12 месяцев по сюжету.

Создаёт справочники (clients, products, channels, geography).

Создаёт факты (events, transactions, accounts, cards, products).

Вносит «грязь»: пропуски, дубликаты, TZ, опечатки.

Загружает в Postgres (raw-слой).

Файлы: data_generator/.

2.2. Raw Layer (PostgreSQL)
Инструмент: PostgreSQL 16 (Docker).

Роль: «боевая» OLTP-БД, как в реальной компании. Сюда пишет генератор, отсюда читает Airflow.

Что внутри: таблицы raw_* (без FK, с грязью).

2.3. ETL (Apache Airflow)
Инструмент: Apache Airflow 2.8 (Docker).

Роль: оркестрация пайплайнов.

DAG-и:

dag_raw_to_dwh — извлечение из Postgres, очистка, загрузка в ClickHouse (staging → DWH).

dag_dwh_to_marts — трансформации в витрины (через dbt).

dag_quality_checks — проверки качества данных (NULL, дубликаты, аномалии).

Файлы: airflow/dags/.

2.4. Трансформации (dbt Core)
Инструмент: dbt Core 1.7 + dbt-postgres + dbt-clickhouse.

Роль: SQL-трансформации с версионированием, тестами и документацией.

Слои dbt:

staging/ — очистка (stg_*): приведение типов, дедупликация, TZ.

marts/ — витрины (dm_*): воронка, retention, LTV, cross-sell, A/B.

Тесты: not_null, unique, relationships, accepted_values.

Файлы: dbt/.

2.5. DWH (ClickHouse)
Инструмент: ClickHouse 24.1 (Docker).

Роль: OLAP-хранилище для аналитики. Быстрые агрегации на миллионах строк.

Что внутри: dim_*, fact_* (звезда), dm_* (витрины).

Почему ClickHouse: в реальных компаниях (Ozon, Яндекс) — стандарт для аналитики. Быстрый, колоночный, бесплатный.

2.6. PySpark (агрегации на «больших» данных)
Инструмент: PySpark 3.5 (локально).

Роль: агрегации, которые тяжело делать в SQL (например, retention по когортам на 25 млн событий). Демонстрация навыка.

Файлы: spark/aggregations.py.

2.7. Greenplum (код без запуска)
Инструмент: Greenplum (не устанавливаем — тяжёлый).

Роль: показать, что знаешь MPP-архитектуру. Код в sql/greenplum/ с комментариями «как в Greenplum».

Почему: в энтерпрайзе (Сбер, Т-Банк) Greenplum — стандарт. На интервью — плюс.

2.8. BI (три инструмента)
Инструмент	Аудитория	Что строим
Power BI Desktop	Менеджмент	Executive dashboard
Apache Superset	Команда продукта	Product dashboard
Metabase	Ad-hoc	Operations dashboard
Почему три: показать гибкость. В реальных компаниях разные команды используют разные BI.

Файлы: bi/power_bi/, bi/superset/, bi/metabase/.

2.9. Excel + Google Sheets (отчёты)
Инструмент: Excel (Power Query), Google Sheets.

Роль: отчёт для «менеджмента» — как в реальных компаниях, где Excel всё ещё жив.

Файлы: excel/, google_sheets/ (добавим в Спринте 8.5).

2.10. Анализ (Python)
Инструмент: Jupyter (в VS Code).

Роль: EDA, воронка, retention, A/B, fraud-паттерны, визуализация.

Файлы: analysis/.

2.11. ML (scikit-learn)
Инструмент: scikit-learn 1.3, imbalanced-learn.

Роль: классификация (churn, fraud, cross-sell), регрессия (LTV), кластеризация (сегментация).

Файлы: ml/.

2.12. Инфраструктура
Docker — все сервисы в контейнерах.

Docker Compose — один up — и всё работает.

Git + GitHub — версионирование.

GitHub Actions — CI (тесты, lint).

3. Поток данных (как данные текут)
3.1. Генерация → Raw

Python (generate.py) → pandas DataFrame → SQLAlchemy → Postgres (raw_*)

3.2. Raw → Staging → DWH
Postgres (raw_*) → Airflow DAG → dbt staging (stg_*) → ClickHouse (dim_*, fact_*)


3.3. DWH → Marts
ClickHouse (dim_*, fact_*) → dbt marts → ClickHouse (dm_*)


3.4. Marts → Presentation
ClickHouse (dm_*) → Power BI / Superset / Metabase / Excel / Jupyter

3.5. ML
ClickHouse (dm_fraud_features) → Jupyter → scikit-learn → scores → ClickHouse (fact_fraud_scores)

4. Почему так (trade-offs)
Решение	Почему	Альтернатива
Postgres для raw	Просто, знакомо, близко к OLTP	MySQL, но Postgres лучше
ClickHouse для DWH	Быстрый, колоночный, стандарт в аналитике	BigQuery (платный), Snowflake (платный)
Airflow для ETL	Стандарт индустрии	Prefect, Dagster (новее, но меньше вакансий)
dbt для трансформаций	Стандарт, тесты, документация	Чистый SQL — без тестов и lineage
Три BI	Гибкость, сравнение	Один BI — проще, но менее показательно
Greenplum — код	Показать знание без тяжёлой установки	Установить — 10 ГБ, сложно
Docker	Воспроизводимость	«У меня работает» — не воспроизводимо
5. Ограничения (что НЕ в архитектуре)
Нет Kubernetes — избыточно для одного аналитика.

Нет облака — всё локально, бесплатно.

Нет real-time — batch-обработка (раз в день). Real-time — сложно, не нужно для портфолио.

Нет CI/CD для деплоя — только CI для тестов (GitHub Actions).

Нет мониторинга (Prometheus, Grafana) — избыточно.

Принцип: минимум инфраструктуры, максимум аналитики. Инфраструктура — средство, не цель.
```
