from src.nlp.query_parser_v2 import QueryParserV2
from src.metrics.metric_registry import MetricRegistry


class AIQueryEngine:

    @staticmethod
    def answer(user_query: str):

        parsed = QueryParserV2.parse(user_query)

        metric_name = parsed["metric"]
        filters = parsed["filters"]

        if metric_name is None:
            return f"❌ Sorry, I could not understand the metric in your query: '{user_query}'"

        metric_fn = MetricRegistry.get_metric(metric_name)

        return metric_fn(filters=filters)
