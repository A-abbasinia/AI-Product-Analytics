import pandas as pd


class RootCauseAnalyzer:
    """
    Performs root cause analysis by comparing segment contributions
    between anomaly period and previous period.
    """

    def analyze(
        self,
        full_df: pd.DataFrame,
        dim_time: str,
        dim_other: str,
        metric: str,
        anomaly_index: int
    ):
        if full_df is None or full_df.empty:
            raise ValueError("Full dataframe is empty")

        # -----------------------------
        # ✅ Fix category column detection
        # -----------------------------
        if dim_other not in full_df.columns:
            if dim_other == "category":
                if "category_name" in full_df.columns:
                    dim_other = "category_name"
                else:
                    raise ValueError(
                        f"Dimension '{dim_other}' missing in dataframe. "
                        f"Available columns: {list(full_df.columns)}"
                    )
            else:
                raise ValueError(
                    f"Dimension '{dim_other}' missing in dataframe."
                )

        if dim_time not in full_df.columns:
            raise ValueError(f"Time dimension '{dim_time}' missing in dataframe")

        # -----------------------------
        # Aggregate metric
        # -----------------------------
        grouped = (
            full_df
            .groupby([dim_time, dim_other])[metric]
            .sum()
            .reset_index()
        )

        time_values = sorted(grouped[dim_time].unique())

        if anomaly_index >= len(time_values) or anomaly_index == 0:
            return []

        current_time = time_values[anomaly_index]
        previous_time = time_values[anomaly_index - 1]

        current_df = grouped[grouped[dim_time] == current_time]
        previous_df = grouped[grouped[dim_time] == previous_time]

        merged = pd.merge(
            current_df,
            previous_df,
            on=dim_other,
            how="outer",
            suffixes=("_curr", "_prev")
        ).fillna(0)

        merged["change"] = merged[f"{metric}_curr"] - merged[f"{metric}_prev"]

        total_change = merged["change"].sum()

        if total_change == 0:
            return []

        merged["contribution_pct"] = (
            merged["change"] / total_change
        ) * 100

        # Sort by absolute contribution
        merged = merged.sort_values(
            by="contribution_pct",
            key=abs,
            ascending=False
        )

        top_segments = merged.head(5)

        results = []
        for _, row in top_segments.iterrows():
            results.append({
                "segment": row[dim_other],
                "change": float(row["change"]),
                "contribution_pct": round(float(row["contribution_pct"]), 2)
            })

        return results
