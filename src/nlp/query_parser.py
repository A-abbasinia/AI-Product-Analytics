import re
from src.metrics.metric_registry import MetricRegistry


class QueryParser:

    @staticmethod
    def extract_metric(user_query: str):

        query = user_query.lower().strip()

        metrics = sorted(
            MetricRegistry.list_metrics(),
            key=len,
            reverse=True
        )

        # Exact match of metric names
        for metric_name in metrics:
            if metric_name.replace("_", " ") in query:
                return metric_name

        # Fallback patterns
        patterns = {
            r"revenue per customer": "revenue_per_customer",
            r"orders per customer": "orders_per_customer",
            r"average order value|aov": "average_order_value",
            r"total revenue|revenue": "revenue",
            r"total orders|number of orders|how many orders": "orders",
        }

        for pattern, metric in patterns.items():
            if re.search(pattern, query):
                return metric

        return None
