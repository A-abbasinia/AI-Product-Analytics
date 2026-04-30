import os
import pandas as pd
import sqlite3

from src.data.data_loader import DataLoader
from src.data.registry import DataRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data/raw")

loader = DataLoader(DATA_PATH)
loader.load_all()

conn = sqlite3.connect(os.path.join(BASE_DIR, "product_analytics.db"))

for name in DataRegistry.list_tables():
    df = DataRegistry.get(name)
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"✔ Saved table: {name}")

conn.close()
print("🎉 SQLite database created successfully!")
