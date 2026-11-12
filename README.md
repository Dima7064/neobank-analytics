# NeoBank Analytics 🏦

Сквозной проект по продуктовой аналитике, симулирующий 12 месяцев жизни финтех-стартапа (необанка). Проект охватывает полный цикл работы с данными: от генерации «грязных» данных до дашбордов для топ-менеджмента и ML-моделей.

## 🎯 Бизнес-контекст

Мы запустили необанк «NeoBank» 1 января 2024 года. За год мы прошли путь от 0 до 50 000 клиентов. В этом репозитории — весь аналитический путь: как мы искали узкие места в воронке, тестировали онбординг, стимулировали cross-sell и боролись с мошенниками.

## 🛠 Стек технологий

- **Хранилища:** PostgreSQL (OLTP), ClickHouse (OLAP)
- **ETL / Трансформации:** Apache Airflow, dbt, PySpark
- **Языки:** Python (pandas, scikit-learn, scipy), SQL
- **BI и Визуализация:** Apache Superset, Power BI, Excel (Power Query), Google Sheets
- **Инфраструктура:** Docker, Git

## 🏗 Архитектура

1. **Data Generator:** Python-скрипт генерирует сырые данные (с пропусками и опечатками).
2. **Raw Layer:** Данные падают в PostgreSQL.
3. **Airflow DAG:** Копирует raw-данные в ClickHouse.
4. **dbt:** Очищает данные (staging) и строит витрины (marts).
5. **Presentation:** Аналитика в Jupyter, дашборды в BI, ML-модели.

## 📊 Ключевые результаты за год

- **Воронка:** Упростили онбординг (A/B-тест). Активация выросла с 18% до 37% (+19 п.п.).
- **Retention:** D30 Retention вырос с 15% до 42% за счет внедрения второго продукта (вклада).
- **Cross-sell:** Доля клиентов с 2+ продуктами выросла с 5% до 38%.
- **Fraud:** Внедрили ML-модель, которая ловит 75% мошенников, снизив убытки на 70%.
- **LTV:** Средний LTV клиента вырос с 8 000 ₽ до 27 000 ₽.

## 📂 Структура репозитория

- `data_generator/` — скрипты генерации данных и внесения «грязи».
- `airflow/` — DAG'и для ETL (Postgres -> ClickHouse).
- `dbt/` — SQL-модели для очистки (staging) и построения витрин (marts).
- `analysis/` — Jupyter-ноутбуки с EDA, A/B-тестами и ML.
- `sql/` — Ad-hoc запросы и DDL для Greenplum.
- `bi/` — Скриншоты и файлы дашбордов (Power BI, Superset).
- `excel/` — Отчет для менеджмента с Power Query.

## 🚀 Как запустить (Quick Start)

1. Установите Docker Desktop.
2. Выполните: `docker-compose up -d`
3. Сгенерируйте данные: `python -m data_generator.generate`
4. Запустите DAG `dag_raw_to_ch` в Airflow (`localhost:8080`).
5. Запустите dbt: `cd dbt && dbt run`
6. Смотрите дашборды в Superset (`localhost:8088`) или Power BI.

## 📸 Скриншоты

_(Сюда вставь скриншоты своих дашбордов, например:)_
![Power BI Executive Dashboard](bi/power_bi/page1_product_health.png)
