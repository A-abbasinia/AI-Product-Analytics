from typing import Optional, List
import pandas as pd

from src.data.registry import registry
from src.engine.analytics_engine import AnalyticsEngine


class GroupByEngine:

    @staticmethod
    def _resolve_table_for_metric(metric_name: str, group_by: str = None) -> pd.DataFrame:

        metric_name = metric_name.lower()
        gb = (group_by or "").lower()

        available = registry.list_tables()

        def safe(name):
            return registry.get(name) if name in available else None

        # ----------------------------------------------------
        # CATEGORY GROUP
        # ----------------------------------------------------

        if gb == "category":

            candidates = [
                safe("orders"),
                safe("transactions"),
                safe("orderdetails"),
                safe("products"),
                safe("categories"),
            ]

            frames = [f for f in candidates if f is not None]

            if not frames:
                raise ValueError("No tables available for category grouping.")

            df = frames[0].copy()

            for f in frames[1:]:

                shared = [c for c in df.columns if c in f.columns]

                if shared:
                    df = df.merge(f, on=shared[0], how="left")

            return df

        # ----------------------------------------------------
        # REVENUE
        # ----------------------------------------------------

        if "revenue" in metric_name or "amount" in metric_name:

            tx = safe("transactions")
            if tx is not None:
                return tx

            orders = safe("orders")
            if orders is not None:
                return orders

        # ----------------------------------------------------
        # ORDERS
        # ----------------------------------------------------

        if "order" in metric_name:

            orders = safe("orders")

            if orders is not None:
                return orders

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        for name in ["transactions", "orders", "orderdetails"]:

            t = safe(name)

            if t is not None:
                return t

        raise ValueError(
            f"Unable to resolve data source for metric '{metric_name}'. "
            f"Available tables: {available}"
        )

    # ----------------------------------------------------
    # GROUP COLUMN
    # ----------------------------------------------------

    @staticmethod
    def _extract_group_column(df: pd.DataFrame, group_by: str) -> pd.Series:

        gb = group_by.lower()

        if gb in ["month", "year", "day"]:

            date_col = AnalyticsEngine._resolve_date_column(df)

            dt = pd.to_datetime(df[date_col], errors="coerce")

            if gb == "month":
                return dt.dt.month

            if gb == "year":
                return dt.dt.year

            if gb == "day":
                return dt.dt.day

        if group_by in df.columns:
            return df[group_by]

        raise Exception(f"Unknown dimension: {group_by}")

    # ----------------------------------------------------
    # METRIC VALUE
    # ----------------------------------------------------

    @staticmethod
    def _compute_metric_column(df: pd.DataFrame, metric_name: str) -> pd.DataFrame:

        df = df.copy()

        metric_name = metric_name.lower()

        if "revenue" in metric_name:

            df["value"] = df.get("amount", df.get("revenue", 0))
            return df

        if "order" in metric_name:

            df["value"] = 1
            return df

        if metric_name == "average_order_value":

            df["value"] = df.get("amount", 0)
            return df

        df["value"] = 1

        return df

    # ----------------------------------------------------
    # GROUPBY CORE
    # ----------------------------------------------------

    @staticmethod
    def group_metric(metric_name: str, group_column: str, filters=None):

        df = GroupByEngine._resolve_table_for_metric(
            metric_name,
            group_column
        )

        df = AnalyticsEngine._apply_filters(df, filters)

        df = GroupByEngine._compute_metric_column(df, metric_name)

        if group_column in df.columns:
            group_key = df[group_column]
        else:
            group_key = GroupByEngine._extract_group_column(df, group_column)

        agg_mode = "mean" if metric_name == "average_order_value" else "sum"

        grouped = (
            df.groupby(group_key)["value"]
            .agg(agg_mode)
            .reset_index()
        )

        grouped.columns = [group_column, metric_name]

        return grouped

    # ----------------------------------------------------
    # PUBLIC API
    # ----------------------------------------------------

    @staticmethod
    def compute(metric_name: str, group_by: str, filters=None):

        return GroupByEngine.group_metric(
            metric_name,
            group_by,
            filters
        )
