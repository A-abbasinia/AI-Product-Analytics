from src.engine.analytics_engine import AnalyticsEngine


class MetricRegistry:
    """
    Backward-compatible metric registry.
    Supports:
    - V2 (using _METRIC_MAP)
    - V3 (canonical + alias system)
    """

    # NEW STRUCTURE
    _METRICS = {
        "revenue": AnalyticsEngine.total_revenue,
        "orders": AnalyticsEngine.total_orders,
        "average_order_value": AnalyticsEngine.average_order_value,
        "revenue_per_customer": AnalyticsEngine.revenue_per_customer,
    }

    _ALIASES = {
        # REVENUE
        "revenue": "revenue",
        "total_revenue": "revenue",
        "total revenue": "revenue",
        "sales": "revenue",

        # ORDERS
        "orders": "orders",
        "total_orders": "orders",
        "total orders": "orders",
        "number_of_orders": "orders",
        "how many orders": "orders",

        # AOV
        "average_order_value": "average_order_value",
        "average order value": "average_order_value",
        "avg_order_value": "average_order_value",
        "avg order value": "average_order_value",
        "aov": "average_order_value",

        # RPC
        "revenue_per_customer": "revenue_per_customer",
        "revenue per customer": "revenue_per_customer",
    }

    @classmethod
    def get_metric(cls, name: str):
        """
        Supports:
        - V2 legacy calls (via _METRIC_MAP)
        - alias resolution
        - canonical resolution
        """
        if not name:
            raise ValueError("Metric name is None")

        key = name.lower().strip()

        # 1) V2 compatibility: direct lookup
        if key in cls._METRIC_MAP:
            return cls._METRIC_MAP[key]

        # 2) alias → canonical → function
        canonical = cls._ALIASES.get(key)
        if canonical and canonical in cls._METRICS:
            return cls._METRICS[canonical]

        raise KeyError(f"Metric '{name}' is not registered.")

    @classmethod
    def get_all_aliases(cls):
        """Used by QueryParserV3."""
        return cls._ALIASES.copy()


# ---------------------------------------------------------------
# Build V2 _METRIC_MAP after the class is created
# ---------------------------------------------------------------
MetricRegistry._METRIC_MAP = {
    alias: MetricRegistry._METRICS[canonical]
    for alias, canonical in MetricRegistry._ALIASES.items()
}
