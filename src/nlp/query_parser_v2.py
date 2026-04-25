from typing import Dict, Any
from src.metrics.metric_registry import MetricRegistry
from src.nlp.filter_parser import FilterParser


class QueryParserV2:

    @staticmethod
    def parse(user_query: str) -> Dict[str, Any]:
        """
        Parse the user query into:
          - metric: normalized metric key compatible with MetricRegistry
          - filters: list[Filter] from FilterParser
        """

        text = user_query.strip().lower()

        # 1) metric detection via longest-substring match
        metric_key = QueryParserV2._detect_metric(text)

        # 2) filters via FilterParser (نسخه فعلی خودت)
        filters = FilterParser.parse(text)

        return {
            "metric": metric_key,
            "filters": filters,
        }

    @staticmethod
    def _detect_metric(text: str) -> str:
        """
        Find the best metric alias present in the text using the longest match.
        """
        # aliasها همان کلیدهای MetricRegistry هستند
        aliases = list(MetricRegistry._METRIC_MAP.keys())

        best_match = None
        best_len = 0

        for alias in aliases:
            if alias in text:
                if len(alias) > best_len:
                    best_match = alias
                    best_len = len(alias)

        return best_match
