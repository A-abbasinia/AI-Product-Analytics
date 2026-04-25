# src/data/registry.py

from typing import Dict
import pandas as pd


class DataRegistry:
    """
    Central storage for all loaded DataFrames.
    """

    _tables: Dict[str, pd.DataFrame] = {}

    @classmethod
    def register(cls, name: str, df: pd.DataFrame):
        cls._tables[name] = df

    @classmethod
    def get(cls, name: str) -> pd.DataFrame:
        if name not in cls._tables:
            raise ValueError(f"Table '{name}' not found in registry.")
        return cls._tables[name]

    @classmethod
    def list_tables(cls):
        return list(cls._tables.keys())

    @classmethod
    def clear(cls):
        cls._tables.clear()
