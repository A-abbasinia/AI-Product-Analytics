# src/ai_engine/insight_analyzer/trend_detector.py

import pandas as pd
import numpy as np

class TrendDetector:
    def __init__(self):
        pass

    def analyze(self, df, group_col, metric_col):
        """
        Detect trends in the provided dataframe.

        df: pandas DataFrame with at least group_col and metric_col
        group_col: str (e.g., 'month')
        metric_col: str (e.g., 'revenue')
        """

        insights = []

        # Ensure sorted by time/dimension
        df = df.sort_values(group_col).reset_index(drop=True)

        # Calculate percentage change
        df["pct_change"] = df[metric_col].pct_change()

        # Calculate moving averages
        df["ma3"] = df[metric_col].rolling(window=3).mean()

        # Detect monotonic increasing/decreasing trend
        is_uptrend = df[metric_col].is_monotonic_increasing
        is_downtrend = df[metric_col].is_monotonic_decreasing

        if is_uptrend:
            insights.append({
                "type": "trend",
                "pattern": "uptrend",
                "metric": metric_col,
                "group_by": group_col,
                "confidence": 0.90,
                "description": f"{metric_col} shows a consistent upward trend."
            })

        if is_downtrend:
            insights.append({
                "type": "trend",
                "pattern": "downtrend",
                "metric": metric_col,
                "group_by": group_col,
                "confidence": 0.90,
                "description": f"{metric_col} shows a consistent downward trend."
            })

        # Detect streaks (3+ increases or decreases)
        streak = 0
        streaks = {"increase": 0, "decrease": 0}

        for i in range(1, len(df)):
            if df[metric_col][i] > df[metric_col][i-1]:
                streak += 1
            else:
                streak = 0
            streaks["increase"] = max(streaks["increase"], streak)

        streak = 0
        for i in range(1, len(df)):
            if df[metric_col][i] < df[metric_col][i-1]:
                streak += 1
            else:
                streak = 0
            streaks["decrease"] = max(streaks["decrease"], streak)

        if streaks["increase"] >= 2:  # 3 consecutive points (0,1,2)
            insights.append({
                "type": "trend",
                "pattern": "multi-step-uptrend",
                "metric": metric_col,
                "group_by": group_col,
                "confidence": 0.85,
                "description": f"{metric_col} increased for {streaks['increase'] + 1} consecutive periods."
            })

        if streaks["decrease"] >= 2:
            insights.append({
                "type": "trend",
                "pattern": "multi-step-downtrend",
                "metric": metric_col,
                "group_by": group_col,
                "confidence": 0.85,
                "description": f"{metric_col} decreased for {streaks['decrease'] + 1} consecutive periods."
            })

        # Detect spikes/drops vs moving average
        if "ma3" in df.columns:
            idx = df.index[-1]
            current = df[metric_col].iloc[-1]
            ma_val = df["ma3"].iloc[-1]

            if not np.isnan(ma_val):
                deviation = (current - ma_val) / ma_val

                if deviation > 0.25:
                    insights.append({
                        "type": "trend",
                        "pattern": "spike",
                        "metric": metric_col,
                        "group_by": group_col,
                        "confidence": 0.80,
                        "description": f"{metric_col} shows a spike (+{round(deviation * 100)}% above moving average)."
                    })

                if deviation < -0.25:
                    insights.append({
                        "type": "trend",
                        "pattern": "drop",
                        "metric": metric_col,
                        "group_by": group_col,
                        "confidence": 0.80,
                        "description": f"{metric_col} shows a significant drop ({round(deviation * 100)}% below moving average)."
                    })

        return insights
