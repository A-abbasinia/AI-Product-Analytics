import pandas as pd


class DataCleaner:

    @staticmethod
    def clean_currency_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove $ and commas and convert to float.
        """

        df = df.copy()

        for col in df.columns:

            if df[col].dtype == object:

                if df[col].astype(str).str.contains(r"\$|,", regex=True).any():

                    df[col] = (
                        df[col]
                        .astype(str)
                        .str.replace("$", "", regex=False)
                        .str.replace(",", "", regex=False)
                        .astype(float)
                    )

        return df

    @staticmethod
    def parse_date_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert probable date columns to datetime.
        """

        df = df.copy()

        for col in df.columns:

            lower = col.lower()

            if any(x in lower for x in ["date", "time", "created", "updated"]):

                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

        return df

    @staticmethod
    def compute_session_duration(df: pd.DataFrame) -> pd.DataFrame:

        df = df.copy()

        if "start_time" in df.columns and "end_time" in df.columns:

            df["session_duration"] = (
                df["end_time"] - df["start_time"]
            ).dt.total_seconds() / 60

        return df
