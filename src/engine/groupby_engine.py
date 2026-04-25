from typing import Optional, List
import pandas as pd

from src.data.registry import DataRegistry
from src.nlp.filter_objects import Filter
from src.engine.analytics_engine import AnalyticsEngine


class GroupByEngine:

    @staticmethod
    def _resolve_table_for_metric(metric_name: str, group_by: str = None) -> pd.DataFrame:
        metric_name = metric_name.lower()
        gb = (group_by or "").lower()

        # SPECIAL CASE: category-based grouping
        if gb == "category":
            orders = DataRegistry.get("orders")
            tx = DataRegistry.get("transactions")
            details = DataRegistry.get("orderdetails")
            products = DataRegistry.get("products")
            cats = DataRegistry.get("categories")

            df = (
                orders
                .merge(tx, on="order_id", how="left")
                .merge(details, on="order_id", how="left")
                .merge(products, on="product_id", how="left")
                .merge(cats, on="category_id", how="left")
            )

            # AUTO-DETECT CATEGORY COLUMN
            possible_names = [
                "category",
                "category_name",
                "name",
                "name_x",
                "name_y",   # THIS one is your real category column
            ]

            found = None
            for col in possible_names:
                if col in df.columns:
                    found = col
                    break

            if found is None:
                raise KeyError(
                    f"No category-like column found after join. Columns available: {list(df.columns)}"
                )

            # unify category column
            if found != "category":
                df["category"] = df[found]

            return df

        # ---------------------------------------------------------------------
        # other metrics
        # ---------------------------------------------------------------------
        if "revenue" in metric_name:
            return DataRegistry.get("transactions")

        if "order" in metric_name:
            return DataRegistry.get("orders")

        if "customer" in metric_name:
            customers = DataRegistry.get("customers")
            orders = DataRegistry.get("orders")
            tx = DataRegistry.get("transactions")

            return (
                customers
                .merge(orders, on="user_id", how="left")
                .merge(tx, on="order_id", how="left")
            )

        return DataRegistry.get("transactions")

    # -------------------------------------------------------------
    # Extract group column
    # -------------------------------------------------------------
    @staticmethod
    def _extract_group_column(df: pd.DataFrame, group_by: str) -> pd.Series:
        gb = group_by.lower()

        if gb in ["month", "year", "day"]:
            date_col = AnalyticsEngine._resolve_date_column(df)
            dt = pd.to_datetime(df[date_col])

            if gb == "month":
                return dt.dt.month
            if gb == "year":
                return dt.dt.year
            if gb == "day":
                return dt.dt.day

        if group_by in df.columns:
            return df[group_by]

        raise Exception(f"Unknown dimension for group-by: {group_by}")

    # -------------------------------------------------------------
    # Compute metric
    # -------------------------------------------------------------
    @staticmethod
    def _compute_metric_column(df: pd.DataFrame, metric_name: str) -> pd.DataFrame:
        metric_name = metric_name.lower()

        if "revenue" in metric_name:
            df["value"] = df["amount"]
            return df

        if "orders" in metric_name:
            df["value"] = 1
            return df

        if metric_name == "revenue_per_customer":
            df["value"] = df["amount"]
            return df

        if metric_name == "average_order_value":
            df["value"] = df["amount"] if "amount" in df else 0
            return df

        df["value"] = 1
        return df

    # -------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------
    @staticmethod
    def group_metric(metric_name: str, group_column: str, filters=None):
        df = GroupByEngine._resolve_table_for_metric(metric_name, group_column)
        df = AnalyticsEngine._apply_filters(df, filters)
        df = GroupByEngine._compute_metric_column(df, metric_name)

        if group_column in df.columns:
            group_key = df[group_column]
        else:
            group_key = GroupByEngine._extract_group_column(df, group_column)

        agg = "mean" if metric_name == "average_order_value" else "sum"

        grouped = df.groupby(group_key)["value"].agg(agg).reset_index()
        grouped.columns = [group_column, metric_name]
        return grouped

    @staticmethod
    def compute(metric_name: str, group_by: str, filters=None):
        return GroupByEngine.group_metric(metric_name, group_by, filters)
