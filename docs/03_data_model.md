# Схема данных проекта NeoBank

Модель данных — **звезда** (star schema) в DWH, но **raw-слой** — OLTP-подобный (как реальные источники).

## 1. Слои данных

Raw Layer (Postgres) → Staging (dbt) → DWH (ClickHouse) → Data Marts (dbt)
[как из источников] [очистка, типы] [звезда: dim + fact] [витрины под задачи]

- **Raw Layer** — «сырые» данные, как из OLTP-систем. Имена таблиц: `raw_*`.
- **Staging** — очищенные, приведённые к типам. Имена: `stg_*`.
- **DWH** — звезда: `dim_*` (справочники), `fact_*` (факты).
- **Data Marts** — витрины: `dm_*` (funnel, retention, ltv, ab_results).

## 2. ER-диаграмма (DWH-слой)

```mermaid
erDiagram
    dim_clients ||--o{ fact_events : "client_id"
    dim_clients ||--o{ fact_transactions : "client_id"
    dim_clients ||--o{ fact_accounts : "client_id"
    dim_clients ||--o{ fact_cards : "client_id"
    dim_clients ||--o{ fact_products : "client_id"
    dim_clients ||--o{ fact_fraud : "client_id"
    dim_products ||--o{ fact_products : "product_id"
    dim_channels ||--o{ dim_clients : "channel_id"
    dim_geography ||--o{ dim_clients : "city_id"
    dim_dates ||--o{ fact_events : "date_id"
    dim_dates ||--o{ fact_transactions : "date_id"

    dim_clients {
        bigint client_id PK
        timestamp registered_at
        int channel_id FK
        int city_id FK
        string segment
        int age
        string status
    }
    dim_products {
        int product_id PK
        string product_type
        string name
        numeric rate
        numeric limit_amount
    }
    dim_channels {
        int channel_id PK
        string channel_name
    }
    dim_geography {
        int city_id PK
        string city_name
        string region
    }
    dim_dates {
        date date_id PK
        int year
        int month
        int day
        int weekday
    }
    fact_events {
        bigint event_id PK
        bigint client_id FK
        string event_type
        timestamp event_at
        date date_id FK
        jsonb properties
    }
    fact_transactions {
        bigint tx_id PK
        bigint client_id FK
        bigint account_id FK
        bigint card_id FK
        date date_id FK
        timestamp tx_at
        numeric amount
        string tx_type
        string category
        string status
    }
    fact_accounts {
        bigint account_id PK
        bigint client_id FK
        string account_type
        timestamp opened_at
        timestamp closed_at
        numeric balance
    }
    fact_cards {
        bigint card_id PK
        bigint client_id FK
        bigint account_id FK
        string card_type
        timestamp issued_at
        timestamp activated_at
        string status
    }
    fact_products {
        bigint client_product_id PK
        bigint client_id FK
        int product_id FK
        timestamp opened_at
        timestamp closed_at
        numeric amount
        string status
    }
    fact_fraud {
        bigint fraud_id PK
        bigint tx_id FK
        bigint client_id FK
        timestamp detected_at
        string fraud_type
        numeric amount
        boolean confirmed
    }


3. Описание таблиц (DWH-слой)
3.1. dim_clients — клиенты
Гранулярность: одна строка = один клиент.

Поле	Тип	Описание
client_id	bigint	PK, уникальный идентификатор
registered_at	timestamp	Дата регистрации
channel_id	int	FK → dim_channels (канал привлечения)
city_id	int	FK → dim_geography (город)
segment	varchar	Сегмент: 'young', 'family', 'premium'
age	int	Возраст на момент регистрации
status	varchar	Статус: 'active', 'churned', 'blocked'
churned_at	timestamp	Дата ухода (NULL если активен)
3.2. dim_products — продукты (справочник)
Гранулярность: одна строка = один тип продукта.

Поле	Тип	Описание
product_id	int	PK
product_type	varchar	'debit_card', 'account', 'deposit', 'credit_card', 'consumer_loan'
name	varchar	Название (для отображения)
rate	numeric	Ставка (для вкладов/кредитов), NULL для карт
limit_amount	numeric	Лимит (для кредитов), NULL для дебета
3.3. dim_channels — каналы привлечения
Гранулярность: одна строка = один канал.

Поле	Тип	Описание
channel_id	int	PK
channel_name	varchar	'organic', 'paid_search', 'social', 'referral', 'partner'
3.4. dim_geography — города
Гранулярность: одна строка = один город.

Поле	Тип	Описание
city_id	int	PK
city_name	varchar	'Москва', 'Санкт-Петербург', 'Казань', ...
region	varchar	'Московская область', 'Ленинградская область', ...
population	int	Население (для сегментации)
3.5. dim_dates — календарь
Гранулярность: одна строка = один день.

Поле	Тип	Описание
date_id	date	PK
year	int	Год
month	int	Месяц (1–12)
day	int	День (1–31)
weekday	int	День недели (1=Пн, 7=Вс)
is_weekend	boolean	Выходной?
is_holiday	boolean	Праздник?
3.6. fact_events — события клиентов
Гранулярность: одна строка = одно событие.

Поле	Тип	Описание
event_id	bigint	PK
client_id	bigint	FK → dim_clients
event_type	varchar	'registration', 'verification', 'login', 'view_product', 'open_product', 'transaction', 'churn'
event_at	timestamp	Время события
date_id	date	FK → dim_dates
properties	jsonb	Доп. свойства (JSON)
Почему миллионы: каждое действие — событие. 500 000 клиентов × ~50 событий = 25 млн строк.

3.7. fact_transactions — транзакции
Гранулярность: одна строка = одна транзакция.

Поле	Тип	Описание
tx_id	bigint	PK
client_id	bigint	FK → dim_clients
account_id	bigint	FK → fact_accounts
card_id	bigint	FK → fact_cards (NULL для переводов)
date_id	date	FK → dim_dates
tx_at	timestamp	Время транзакции
amount	numeric	Сумма
tx_type	varchar	'purchase', 'transfer', 'withdrawal', 'top_up', 'payment'
category	varchar	'groceries', 'transport', 'entertainment', 'utilities', 'other'
status	varchar	'completed', 'declined', 'reversed'
is_fraud	boolean	Флаг fraud (для обучения модели)
3.8. fact_accounts — счета
Гранулярность: одна строка = один счёт.

Поле	Тип	Описание
account_id	bigint	PK
client_id	bigint	FK → dim_clients
account_type	varchar	'current', 'deposit', 'credit'
opened_at	timestamp	Дата открытия
closed_at	timestamp	Дата закрытия (NULL если открыт)
balance	numeric	Текущий баланс
status	varchar	'active', 'closed', 'blocked'
3.9. fact_cards — карты
Гранулярность: одна строка = одна карта.

Поле	Тип	Описание
card_id	bigint	PK
client_id	bigint	FK → dim_clients
account_id	bigint	FK → fact_accounts
card_type	varchar	'debit', 'credit'
issued_at	timestamp	Дата выпуска
activated_at	timestamp	Дата активации (NULL если не активирована)
status	varchar	'issued', 'active', 'blocked', 'closed'
3.10. fact_products — продукты клиента
Гранулярность: одна строка = один продукт у клиента.

Поле	Тип	Описание
client_product_id	bigint	PK
client_id	bigint	FK → dim_clients
product_id	int	FK → dim_products
opened_at	timestamp	Дата открытия
closed_at	timestamp	Дата закрытия (NULL если активен)
amount	numeric	Сумма (для вклада/кредита), NULL для карты
status	varchar	'active', 'closed', 'overdue'
3.11. fact_fraud — fraud-случаи
Гранулярность: одна строка = один подтверждённый fraud-случай.

Поле	Тип	Описание
fraud_id	bigint	PK
tx_id	bigint	FK → fact_transactions
client_id	bigint	FK → dim_clients
detected_at	timestamp	Когда обнаружили
fraud_type	varchar	'card_not_present', 'account_takeover', 'friendly_fraud'
amount	numeric	Сумма ущерба
confirmed	boolean	Подтверждён?
4. Raw-слой (Postgres): чем отличается
Raw-слой — «как из источников». Отличия от DWH:

Имена: raw_clients, raw_transactions, raw_events и т.д.

Грязь:

Пропуски (NULL) там, где их быть не должно.

Дубликаты (0.1%).

Строки вместо чисел ("1 500" в amount).

Разные форматы городов (Москва, москва, Moscow).

Часовые пояса: created_at в UTC, event_at в Moscow.

Опечатки.

Нет связей (FK): raw-слой — просто таблицы, без constraints.

Денормализация: иногда дублируются поля (например, channel_name прямо в raw_clients).

Задача ETL: очистить raw → получить чистый DWH.

5. Data Marts (витрины)
Витрина	Что внутри	Гранулярность
dm_funnel	Воронка: регистрация → активация → ...	день + сегмент
dm_retention	Retention по когортам	когорта (месяц) + day_n
dm_ltv	LTV по клиентам	клиент
dm_cross_sell	Матрица cross-sell (продукт A × продукт B)	пара продуктов
dm_ab_results	Результаты A/B по экспериментам	эксперимент + группа + метрика
dm_fraud_features	Фичи для ML-модели fraud	транзакция
6. Ключевые решения по схеме
Звезда, а не снежинка — проще для аналитики, быстрее в ClickHouse.

dim_dates — обязательна, чтобы не терять дни без данных.

fact_events — денормализованная, но с jsonb для гибкости.

fact_transactions — с is_fraud — для обучения модели (в реальности — отдельная таблица разметки, но для симуляции ок).

Raw-слой — «грязный» — специально, чтобы тренировать очистку.

Гранулярность — критична. Всегда проверять перед JOIN (например, fact_transactions × fact_products может задвоить, если у клиента несколько продуктов).
```
