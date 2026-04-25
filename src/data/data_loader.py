# src/data/data_loader.py

import os
import pandas as pd
from typing import List

from src.data.data_cleaner import DataCleaner
from src.data.registry import DataRegistry


class DataLoader:

    def __init__(self, data_path: str):
        self.data_path = data_path

    def load_all(self):

        files = [f for f in os.listdir(self.data_path) if f.endswith(".csv")]

        for file in files:
            table_name = file.replace(".csv", "").replace("PAT-", "").lower()
            full_path = os.path.join(self.data_path, file)

            df = pd.read_csv(full_path)

            df = DataCleaner.clean_currency_columns(df)
            df = DataCleaner.parse_date_columns(df)
            df = DataCleaner.compute_session_duration(df)

            DataRegistry.register(table_name, df)

        print("✅ All tables loaded successfully.")
        print("Tables:", DataRegistry.list_tables())

    # ---------------------------------------------------------
    # BUILD FULL JOINED DATASET
    # ---------------------------------------------------------

    def get_joined_dataset(self) -> pd.DataFrame:

        available = set(DataRegistry.list_tables())

        if "orders" not in available:
            raise RuntimeError("Orders table is required.")

        df = DataRegistry.get("orders").copy()

        # orders → orderdetails
        if "orderdetails" in available:
            details = DataRegistry.get("orderdetails")
            df = df.merge(details, on="order_id", how="left", suffixes=("", "_orderdetails"))

        # → products
        if "products" in available and "product_id" in df.columns:
            products = DataRegistry.get("products")
            df = df.merge(products, on="product_id", how="left", suffixes=("", "_product"))

        # → categories
        if "categories" in available and "category_id" in df.columns:
            cats = DataRegistry.get("categories")
            df = df.merge(cats, on="category_id", how="left", suffixes=("", "_category"))

            # ✅ NORMALIZE CATEGORY COLUMN
            possible_category_cols = [
                "category",
                "category_name",
                "name",
                "name_category",
                "name_y",
            ]

            for col in possible_category_cols:
                if col in df.columns:
                    df["category"] = df[col]
                    break

        # → transactions
        if "transactions" in available:
            tx = DataRegistry.get("transactions")
            df = df.merge(tx, on="order_id", how="left", suffixes=("", "_tx"))

        # → customers
        if "customers" in available and "user_id" in df.columns:
            customers = DataRegistry.get("customers")
            df = df.merge(customers, on="user_id", how="left", suffixes=("", "_customer"))

        # → visits
        if "visits" in available and "user_id" in df.columns:
            visits = DataRegistry.get("visits")
            df = df.merge(visits, on="user_id", how="left", suffixes=("", "_visit"))

        # → consultation
        if "consultation" in available and "user_id" in df.columns:
            consult = DataRegistry.get("consultation")
            df = df.merge(consult, on="user_id", how="left", suffixes=("", "_consult"))

        return df
