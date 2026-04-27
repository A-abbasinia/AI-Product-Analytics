class NarrativeGenerator:
    """
    Generates executive-level narrative text based on dashboard data,
    KPIs, trends, anomalies, insights, and recommendations.
    """

    def __init__(self):
        pass

    # -----------------------------
    # SUMMARY SECTION
    # -----------------------------
    def generate_summary(self, domain, metrics):
        try:
            main_kpis = ", ".join([f"{k}: {v}" for k, v in metrics.items()])
        except:
            main_kpis = "KPIs unavailable"

        summary = (
            f"This report reviews the performance of the {domain} domain, "
            f"focusing on its key performance indicators. "
            f"The primary KPIs observed include {main_kpis}. "
            f"These metrics provide a high-level overview of performance and business health."
        )
        return summary

    # -----------------------------
    # TREND SECTION (Robust)
    # -----------------------------
    def generate_trend_section(self, trends):

        if not trends:
            return "No significant trends were detected in the analyzed data."

        # If trends is a string
        if isinstance(trends, str):
            return f"Trend Analysis:\n- {trends}"

        # If trends is a dict
        if isinstance(trends, dict):
            trends = [trends]

        trend_lines = []
        for item in trends:

            if not isinstance(item, dict):
                trend_lines.append(f"- {str(item)}")
                continue

            metric = item.get("metric", "unknown metric")
            value = item.get("value", "?")
            direction = item.get("direction", "unknown")

            if direction == "up":
                trend_lines.append(
                    f"- A positive upward trend was observed in {metric} (value: {value})."
                )
            elif direction == "down":
                trend_lines.append(
                    f"- A negative downward trend was detected in {metric} (value: {value})."
                )
            else:
                trend_lines.append(
                    f"- A trend was detected in {metric} with value {value}."
                )

        return "Trend Analysis:\n" + "\n".join(trend_lines)

    # -----------------------------
    # ANOMALY SECTION (Fully Robust)
    # -----------------------------
    def generate_anomaly_section(self, anomalies):

        if not anomalies:
            return "No significant anomalies were identified during the analysis period."

        # If anomalies is a string
        if isinstance(anomalies, str):
            return f"Anomalies:\n- {anomalies}"

        # If anomalies is a dict (this is your anomaly detector format)
        if isinstance(anomalies, dict):

            if not anomalies.get("has_anomaly", False):
                return "No significant anomalies were identified during the analysis period."

            lines = []
            deviation = anomalies.get("deviation_pct", "?")
            lines.append(f"- An anomaly was detected with deviation of {deviation}%.")

            root_causes = anomalies.get("root_causes", [])
            for rc in root_causes:

                if not isinstance(rc, dict):
                    lines.append(f"  • {str(rc)}")
                    continue

                dim = rc.get("dimension", "unknown dimension")
                seg = rc.get("segment", "unknown segment")
                impact = rc.get("contribution_pct", "?")

                lines.append(f"  • {dim} = {seg} (impact {impact}%)")

            return "Anomalies:\n" + "\n".join(lines)

        # If it's a list
        if isinstance(anomalies, list):

            lines = []
            for a in anomalies:

                if isinstance(a, dict):
                    metric = a.get("metric", "unknown metric")
                    value = a.get("value", "?")
                    lines.append(f"- An anomaly was detected in {metric} (value: {value}).")
                else:
                    lines.append(f"- {str(a)}")

            return "Anomalies:\n" + "\n".join(lines)

        # fallback
        return f"Anomalies:\n- {str(anomalies)}"

    # -----------------------------
    # INSIGHTS SECTION
    # -----------------------------
    def generate_insight_section(self, insights):
        if not insights:
            return "No significant insights were identified during this period."

        lines = []
        for i in insights:
            lines.append(f"- {str(i)}")

        return "Key Insights:\n" + "\n".join(lines)

    # -----------------------------
    # RECOMMENDATIONS SECTION
    # -----------------------------
    def generate_recommendation_section(self, recommendations):
        if not recommendations:
            return "No actionable recommendations were generated for this period."

        lines = []
        for r in recommendations:
            lines.append(f"- {str(r)}")

        return "Actionable Recommendations:\n" + "\n".join(lines)

    # -----------------------------
    # FULL NARRATIVE BUILDER
    # -----------------------------
    def generate_full_narrative(self, domain, metrics, trends, anomalies, insights, recommendations):

        parts = [
            self.generate_summary(domain, metrics),
            self.generate_trend_section(trends),
            self.generate_anomaly_section(anomalies),
            self.generate_insight_section(insights),
            self.generate_recommendation_section(recommendations)
        ]

        return "\n\n".join(parts)
