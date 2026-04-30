import os
import pandas as pd

from src.data.data_cleaner import DataCleaner
from src.data.registry import registry


class DataLoader:

    def __init__(self, data_path: str):
        self.data_path = data_path


    def load_all(self):

        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Data path not found: {self.data_path}")

        files = [f for f in os.listdir(self.data_path) if f.endswith(".csv")]

        if not files:
            raise RuntimeError("No CSV files found.")

        for file in files:

            table_name = (
                file.replace(".csv", "")
                    .replace("PAT-", "")
                    .lower()
            )

            path = os.path.join(self.data_path, file)

            df = pd.read_csv(path)

            df = DataCleaner.clean_currency_columns(df)
            df = DataCleaner.parse_date_columns(df)
            df = DataCleaner.compute_session_duration(df)

            registry.register(table_name, df)

        print("✅ Tables Loaded:", registry.list_tables())


    def get_joined_dataset(self) -> pd.DataFrame:

        available = set(registry.list_tables())

        if "orders" not in available:
            raise RuntimeError("Orders table required")

        df = registry.get("orders").copy()


        # orderdetails
        if "orderdetails" in available:

            details = registry.get("orderdetails")

            if "order_id" in details.columns:

                df = df.merge(details, on="order_id", how="left")


        # products
        if "products" in available and "product_id" in df.columns:

            products = registry.get("products")

            df = df.merge(products, on="product_id", how="left")

            possible_product_cols = [
                "product_name",
                "name",
                "product",
                "title"
            ]

            for col in possible_product_cols:

                if col in df.columns:

                    df["product_name"] = df[col]
                    break


        # categories
        if "categories" in available and "category_id" in df.columns:

            cats = registry.get("categories")

            df = df.merge(cats, on="category_id", how="left")

            possible_cols = [
                "category",
                "category_name",
                "name_category",
                "name_y"
            ]

            for col in possible_cols:

                if col in df.columns:

                    df["category"] = df[col]
                    break


        # transactions
        if "transactions" in available:

            tx = registry.get("transactions")

            if "order_id" in tx.columns:

                df = df.merge(tx, on="order_id", how="left")


        # customers
        if "customers" in available and "user_id" in df.columns:

            customers = registry.get("customers")

            df = df.merge(customers, on="user_id", how="left")


        # visits
        if "visits" in available and "user_id" in df.columns:

            visits = registry.get("visits")

            df = df.merge(visits, on="user_id", how="left")


        # consultation
        if "consultation" in available and "user_id" in df.columns:

            consult = registry.get("consultation")

            df = df.merge(consult, on="user_id", how="left")


        print("✅ Joined dataset built")
        print("Shape:", df.shape)

        return df
