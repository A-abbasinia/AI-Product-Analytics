import pandas as pd
from src.data.registry import DataRegistry
from src.semantic.table_relationships import TableRelationships


class JoinResolver:

    @staticmethod
    def join(left_table: str, right_table: str) -> pd.DataFrame:

        relationships = TableRelationships.get_relationships()

        for rel in relationships:
            if rel["left_table"] == left_table and rel["right_table"] == right_table:

                left_df = DataRegistry.get(left_table)
                right_df = DataRegistry.get(right_table)

                merged = pd.merge(
                    left_df,
                    right_df,
                    left_on=rel["left_key"],
                    right_on=rel["right_key"],
                    how="left"
                )

                return merged

        raise ValueError(f"No relationship defined between {left_table} and {right_table}")
