import numpy as np
import pandas as pd

from src.ai_engine.insight_analyzer.root_cause_analyzer import RootCauseAnalyzer


class BaseAnomalyDetector:
    """Helper class for anomaly identification with multiple statistical methods"""

    @staticmethod
    def z_score(series: pd.Series):
        mean = series.mean()
        std = series.std()
        if std == 0:
            return np.zeros(len(series))
        return (series - mean) / std

    @staticmethod
    def modified_z_score(series: pd.Series):
        median = np.median(series)
        mad = np.median(np.abs(series - median))
        if mad == 0:
            return np.zeros(len(series))
        return 0.6745 * (series - median) / mad

    @staticmethod
    def iqr_bounds(series: pd.Series):
        q1 = np.percentile(series, 25)
        q3 = np.percentile(series, 75)
        iqr = q3 - q1
        return (q1 - 1.5 * iqr, q3 + 1.5 * iqr)

    @staticmethod
    def detect_anomalies(series: pd.Series, z_thr=2.5, mz_thr=3.5):
        """Detect anomalies based on combined z-score, MAD, and IQR thresholds"""
        z = np.abs(BaseAnomalyDetector.z_score(series))
        mz = np.abs(BaseAnomalyDetector.modified_z_score(series))
        low, high = BaseAnomalyDetector.iqr_bounds(series)

        anomalies = []
        for i, value in enumerate(series):
            if z[i] > z_thr or mz[i] > mz_thr or value < low or value > high:
                anomalies.append(i)
        return anomalies


class AnomalyDetector:
    """
    Detects anomalies and optionally triggers RootCauseAnalysis.
    """

    # ------------------------------------------------------
    # NEW: Metric normalizer inside joined_df
    # ------------------------------------------------------
    def _ensure_metric_column(self, joined_df: pd.DataFrame, metric: str):
        """
        Ensures the metric column exists inside joined_df.
        For example:
            metric='revenue'  -> uses 'amount'
            metric='orders'   -> count
        """

        # Already exists — OK
        if metric in joined_df.columns:
            return joined_df

        # Define mappings
        metric_map = {
            "revenue": "amount",
            "sales": "amount",
            "order_value": "amount",
        }

        # If metric is revenue or aliases → build from amount
        if metric in metric_map and metric_map[metric] in joined_df.columns:
            joined_df[metric] = joined_df[metric_map[metric]]
            return joined_df

        # Fallback: metric not found
        raise ValueError(f"Column not found: {metric}")

    # ------------------------------------------------------
    # MAIN ANALYSIS
    # ------------------------------------------------------
    def analyze(
        self,
        df: pd.DataFrame,
        dim: str,
        metric: str,
        joined_df: pd.DataFrame,
        z_thr: float = 2.5,
        mz_thr: float = 3.5,
        debug_force: bool = False
    ):
        if df is None or df.empty or metric not in df.columns:
            return {"has_anomaly": False, "reason": "empty dataframe or metric missing"}

        if joined_df is None or joined_df.empty:
            raise ValueError("joined_df is required for root-cause analysis")

        # ------------------------------------------------------
        # 🔥 NEW: ensure metric inside joined_df
        # ------------------------------------------------------
        joined_df = self._ensure_metric_column(joined_df, metric)

        # Run anomaly detection
        series = df[metric]
        anomalies = BaseAnomalyDetector.detect_anomalies(series, z_thr=z_thr, mz_thr=mz_thr)

        if not anomalies:
            if not debug_force:
                return {"has_anomaly": False}
            if len(series) < 2:
                return {"has_anomaly": False}
            idx = len(series) - 1
        else:
            idx = anomalies[-1]

        value = series.iloc[idx]
        prev = series.iloc[idx - 1] if idx > 0 else None
        insight_type = "spike" if prev is None or value > prev else "drop"
        deviation_pct = ((value - prev) / prev) * 100 if prev else None

        # Ensure time dimension exists
        if dim not in joined_df.columns:
            candidate_date_cols = ["order_date", "transaction_date", "date"]
            date_col = next((c for c in candidate_date_cols if c in joined_df.columns), None)

            if date_col is None:
                raise ValueError(
                    f"Time dimension '{dim}' missing and no usable date column found in dataframe."
                )

            joined_df[date_col] = pd.to_datetime(joined_df[date_col], errors="coerce")

            if dim == "month":
                joined_df["month"] = joined_df[date_col].dt.month
            elif dim == "year":
                joined_df["year"] = joined_df[date_col].dt.year
            elif dim == "day":
                joined_df["day"] = joined_df[date_col].dt.date
            else:
                raise ValueError(f"Unsupported time dimension '{dim}'")

        # Root Cause Analysis
        rca = RootCauseAnalyzer()
        root_causes = rca.analyze(
            full_df=joined_df,
            dim_time=dim,
            dim_other="category",
            metric=metric,
            anomaly_index=idx
        )

        return {
            "has_anomaly": bool(anomalies),
            "debug_forced": debug_force and not bool(anomalies),
            "type": insight_type,
            "index": int(idx),
            "value": float(value),
            "prev": float(prev) if prev is not None else None,
            "deviation_pct": float(deviation_pct) if deviation_pct is not None else None,
            "root_causes": root_causes,
        }
