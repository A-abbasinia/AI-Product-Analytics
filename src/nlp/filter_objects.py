from dataclasses import dataclass
from typing import Any, Tuple, Union


@dataclass
class Filter:
    column: str
    operator: str  # eq, gte, lte, between
    value: Union[Any, Tuple[Any, Any]]

    def __repr__(self):
        return f"Filter(column={self.column}, operator={self.operator}, value={self.value})"
