import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils import fetch_df

# Создаем папку для данных
os.makedirs("excel/data", exist_ok=True)

print("Выгрузка LTV...")
df_ltv = fetch_df("SELECT * FROM neobank_marts.dm_ltv")
df_ltv.to_csv("excel/data/ltv.csv", index=False, encoding="utf-8-sig")

print("Выгрузка Воронки...")
df_funnel = fetch_df("SELECT * FROM neobank_marts.dm_funnel")
df_funnel.to_csv("excel/data/funnel.csv", index=False, encoding="utf-8-sig")

print("Выгрузка Клиентов...")
df_clients = fetch_df("SELECT client_id, segment, city_name_clean, age FROM neobank_staging.stg_clients")
df_clients.to_csv("excel/data/clients.csv", index=False, encoding="utf-8-sig")

print("Готово! Файлы лежат в excel/data/")
