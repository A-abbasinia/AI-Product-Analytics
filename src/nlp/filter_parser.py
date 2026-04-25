import re
from datetime import datetime
from typing import List
from src.nlp.filter_objects import Filter


class FilterParser:

    @staticmethod
    def parse(text: str) -> List[Filter]:
        filters = []

        text = text.lower()

        # -----------------------------
        # 1️⃣ Year filter (in 2022)
        # -----------------------------
        year_match = re.search(r"in (\d{4})", text)
        if year_match:
            year = int(year_match.group(1))

            start = datetime(year, 1, 1)
            end = datetime(year, 12, 31)

            filters.append(
                Filter(
                    column="__year__",      # semantic column
                    operator="between",
                    value=(start, end),
                )
            )

        # -----------------------------
        # 2️⃣ user_id filter
        # revenue for user_id 5
        # -----------------------------
        user_match = re.search(r"user_id\s*(\d+)", text)
        if user_match:
            user_id = int(user_match.group(1))
            filters.append(
                Filter(
                    column="user_id",
                    operator="eq",
                    value=user_id,
                )
            )

        # -----------------------------
        # 3️⃣ status filter
        # orders with completed status
        # -----------------------------
        status_match = re.search(r"(completed|pending|cancelled)", text)
        if status_match:
            status_value = status_match.group(1).lower()

            filters.append(
                Filter(
                    column="status",
                    operator="eq",
                    value=status_value,   # <-- FIXED HERE
                )
            )

        return filters
