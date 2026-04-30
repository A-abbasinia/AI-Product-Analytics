import re
from dataclasses import dataclass
from typing import Optional, List

from src.nlp.filter_objects import Filter
from src.nlp.filter_parser import FilterParser
from src.metrics.metric_registry import MetricRegistry


@dataclass
class ParsedQuery:
    metric: Optional[str]
    filters: List[Filter]
    group_by: Optional[str]


class QueryParserV3:

    @staticmethod
    def parse(user_query: str) -> ParsedQuery:
        text = user_query.lower().strip()

        # 1) Extract filters  (FIXED)
        parser = FilterParser()
        filters = parser.parse(text)

        # 2) Extract metric
        metric = QueryParserV3._extract_metric(text)

        # 3) Extract group-by
        group_by = QueryParserV3._extract_group_by(text)

        return ParsedQuery(
            metric=metric,
            filters=filters,
            group_by=group_by
        )

    # ----------------------------------------------------------------
    # Metric extraction
    # ----------------------------------------------------------------
    @staticmethod
    def _extract_metric(text: str) -> Optional[str]:
        aliases = MetricRegistry.get_all_aliases()  # MUST exist in registry

        best_alias = None
        longest = 0

        for alias, canonical in aliases.items():
            if alias in text:
                if len(alias) > longest:
                    best_alias = canonical
                    longest = len(alias)

        return best_alias

    # ----------------------------------------------------------------
    # Group-by extraction
    # ----------------------------------------------------------------
    @staticmethod
    def _extract_group_by(text: str) -> Optional[str]:
        known_dimensions = [
            "month", "year", "day",
            "status", "category", "payment_type"
        ]

        for dim in known_dimensions:
            pattern = r"\bby\s+" + re.escape(dim) + r"\b"
            if re.search(pattern, text):
                return dim

        return None
