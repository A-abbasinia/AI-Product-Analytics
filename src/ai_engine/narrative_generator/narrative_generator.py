class NarrativeGenerator:
    """
    Generates executive-level narrative text based on dashboard data,
    KPIs, trends, anomalies, insights, and recommendations.
    """

    def __init__(self):
        pass

    def generate_summary(self, domain, metrics):
        try:
            main_kpis = ", ".join([f"{k}: {v}" for k, v in metrics.items()])
        except:
            main_kpis = "KPIs unavailable"

        summary = (
            f"This report reviews the performance of the {domain} domain, "
            f"with a focus on the most important key performance indicators. "
            f"A quick overview of the current status shows that the primary KPIs include {main_kpis}. "
            f"These figures provide an initial snapshot of the current situation and overall trends."
        )
        return summary

    def generate_trend_section(self, trends):
        if not trends:
            return "No significant trends were detected in the analyzed data."

        trend_lines = []
        for item in trends:
            trend_lines.append(
                f"- A positive trend was observed in {item.get('metric', 'unknown')} with a value of {item.get('value', '?')}."
                if item.get("direction") == "up"
                else f"- A declining trend was detected in {item.get('metric', 'unknown')} with a value of {item.get('value', '?')}."
            )

        return "Trend Analysis:\n" + "\n".join(trend_lines)

    def generate_anomaly_section(self, anomalies):
        if not anomalies:
            return "No significant anomalies were identified during the analysis period."

        anomaly_lines = []
        for a in anomalies:
            anomaly_lines.append(
                f"- An anomaly was detected in {a.get('metric', 'unknown')} with a value of {a.get('value', '?')}."
            )

        return "Anomalies:\n" + "\n".join(anomaly_lines)

    def generate_insight_section(self, insights):
        if not insights:
            return "No significant insights were identified during this period."

        return "Key Insights:\n" + "\n".join([f"- {i}" for i in insights])

    def generate_recommendation_section(self, recommendations):
        if not recommendations:
            return "No actionable recommendations were generated for this period."

        return "Actionable Recommendations:\n" + "\n".join([f"- {r}" for r in recommendations])

    def generate_full_narrative(self, domain, metrics, trends, anomalies, insights, recommendations):
        parts = [
            self.generate_summary(domain, metrics),
            self.generate_trend_section(trends),
            self.generate_anomaly_section(anomalies),
            self.generate_insight_section(insights),
            self.generate_recommendation_section(recommendations)
        ]

        return "\n\n".join(parts)
