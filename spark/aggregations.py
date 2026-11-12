"""PySpark скрипт для агрегации больших данных.

В реальном проекте PySpark используется для обработки миллионов событий,
которые не помещаются в память одной машины.

Запуск (если установлен pyspark):
    python spark/aggregations.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as _sum, date_format

def main():
    print("Запуск PySpark сессии...")
    spark = SparkSession.builder \
        .appName("NeoBank Aggregations") \
        .config("spark.jars.packages", "com.clickhouse:clickhouse-jdbc:0.4.6") \
        .getOrCreate()

    # В реальном коде здесь было бы подключение к ClickHouse
    # df = spark.read.format("jdbc").option("url", "jdbc:clickhouse://localhost:8123/neobank").load("raw_events")
    
    # Для демонстрации создадим датафрейм в памяти
    data = [("registration", 100), ("transaction", 5000), ("login", 2000)]
    df = spark.createDataFrame(data, ["event_type", "count"])
    
    print("Группировка по типам событий:")
    df.groupBy("event_type").agg(_sum("count").alias("total")).show()
    
    spark.stop()

if __name__ == "__main__":
    main()
