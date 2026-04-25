from datetime import datetime
from typing import List, Optional
import pandas as pd

from src.data.registry import DataRegistry
from src.nlp.filter_objects import Filter


class AnalyticsEngine:
    """
    Core analytics computations over DataRegistry tables.
    """

    # =========================================
    # INTERNAL HELPERS
    # =========================================

    @staticmethod
    def _resolve_date_column(df: pd.DataFrame) -> Optional[str]:
        """
        Automatically find the correct date column.
        Priority:
          1) transaction_date
          2) order_date
        """
        if "transaction_date" in df.columns:
            return "transaction_date"
        if "order_date" in df.columns:
            return "order_date"
        return None

    @staticmethod
    def _apply_filters(df: pd.DataFrame, filters: Optional[List[Filter]]) -> pd.DataFrame:
        """
        Apply Filter objects to dataframe.
        Handles:
          - semantic year filter (__year__)
          - normal equality filters
          - between, gte, lte
        """

        if not filters:
            return df

        for f in filters:

            # -------------------
            # YEAR semantic filter
            # -------------------
            if f.column == "__year__":
                date_col = AnalyticsEngine._resolve_date_column(df)
                if date_col is None:
                    continue

                start, end = f.value
                df = df[(df[date_col] >= start) & (df[date_col] <= end)]
                continue

            # -------------------
            # Missing column → ignore filter
            # -------------------
            if f.column not in df.columns:
                continue

            # -------------------
            # Operator: eq
            # -------------------
            if f.operator == "eq":
                if df[f.column].dtype == object:
                    df = df[df[f.column].str.lower() == str(f.value).lower()]
                else:
                    df = df[df[f.column] == f.value]

            # -------------------
            # Operator: between
            # -------------------
            elif f.operator == "between":
                start, end = f.value
                df = df[(df[f.column] >= start) & (df[f.column] <= end)]

            # -------------------
            # gte
            # -------------------
            elif f.operator == "gte":
                df = df[df[f.column] >= f.value]

            # -------------------
            # lte
            # -------------------
            elif f.operator == "lte":
                df = df[df[f.column] <= f.value]

        return df

    # =========================================
    # METRICS
    # =========================================

    @staticmethod
    def total_revenue(filters: Optional[List[Filter]] = None) -> float:
        """
        Sum of transaction amounts.
        If user_id filter exists → join orders to propagate it.
        """
        transactions = DataRegistry.get("transactions")

        # Detect user_id filters
        has_user_filter = filters and any(f.column == "user_id" for f in filters)

        # JOIN needed when user_id filter exists
        if has_user_filter:
            orders = DataRegistry.get("orders")
            merged = transactions.merge(orders, on="order_id", how="left")
            merged = AnalyticsEngine._apply_filters(merged, filters)
            return float(merged["amount"].sum())

        # Normal case
        transactions = AnalyticsEngine._apply_filters(transactions, filters)
        return float(transactions["amount"].sum())

    @staticmethod
    def total_orders(filters: Optional[List[Filter]] = None) -> int:
        """
        Count orders. Filters applied on orders table.
        """
        orders = DataRegistry.get("orders")
        orders = AnalyticsEngine._apply_filters(orders, filters)
        return int(len(orders))

    @staticmethod
    def average_order_value(filters: Optional[List[Filter]] = None) -> float:
        """
        AOV = total_revenue / total_orders
        """
        rev = AnalyticsEngine.total_revenue(filters)
        cnt = AnalyticsEngine.total_orders(filters)

        return 0.0 if cnt == 0 else rev / cnt

    @staticmethod
    def revenue_per_customer(filters: Optional[List[Filter]] = None) -> pd.Series:
        """
        Revenue grouped by customer.
        customers → orders → transactions
        """
        customers = DataRegistry.get("customers")
        orders = DataRegistry.get("orders")
        transactions = DataRegistry.get("transactions")

        merged = (
            customers
            .merge(orders, on="user_id", how="left")
            .merge(transactions, on="order_id", how="left")
        )

        merged = AnalyticsEngine._apply_filters(merged, filters)

        return merged.groupby("user_id")["amount"].sum().fillna(0.0)
