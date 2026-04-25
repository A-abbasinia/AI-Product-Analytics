# src/data/data_cleaner.py

import pandas as pd


class DataCleaner:

    @staticmethod
    def clean_currency_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Removes $ and commas from monetary columns and converts them to float.
        """
        for col in df.columns:
            if df[col].dtype == object:
                if df[col].astype(str).str.contains(r'\$|,', regex=True).any():
                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace('$', '', regex=False)
                        .str.replace(',', '', regex=False)
                        .astype(float)
                    )
        return df

    @staticmethod
    def parse_date_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Attempts to convert columns containing 'date', 'time', 'created', 'updated'
        into datetime.
        """
        for col in df.columns:
            lower_col = col.lower()
            if any(keyword in lower_col for keyword in ["date", "time", "created", "updated"]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass
        return df

    @staticmethod
    def compute_session_duration(df: pd.DataFrame) -> pd.DataFrame:
        """
        If start_time and end_time exist, compute session_duration in minutes.
        """
        if "start_time" in df.columns and "end_time" in df.columns:
            df["session_duration"] = (
                df["end_time"] - df["start_time"]
            ).dt.total_seconds() / 60
        return df
