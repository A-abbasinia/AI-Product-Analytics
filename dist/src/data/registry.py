from typing import Dict
import pandas as pd


class _DataRegistry:
    """
    Singleton storage for all loaded DataFrames.
    """

    def __init__(self):
        self._tables: Dict[str, pd.DataFrame] = {}

    def register(self, name: str, df: pd.DataFrame):
        name = name.lower()
        self._tables[name] = df

    def get(self, name: str) -> pd.DataFrame:
        name = name.lower()

        if name not in self._tables:
            raise ValueError(f"Table '{name}' not found in registry.")

        return self._tables[name]

    def list_tables(self):
        return list(self._tables.keys())

    def exists(self, name: str) -> bool:
        return name.lower() in self._tables

    def clear(self):
        self._tables.clear()


# ✅ global singleton
registry = _DataRegistry()
