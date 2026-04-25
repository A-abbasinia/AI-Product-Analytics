class InsightGenerator:
    def __init__(self):
        pass

    def generate_insight(self, metric):
        metric = metric.lower()

        insight_templates = {
            "revenue": "Revenue has changed due to variations in customer demand and category performance.",
            "orders": "Order volume reflects shifts in conversions and product availability.",
            "sessions": "Traffic appears influenced by marketing efforts and seasonal interest.",
            "aov": "AOV is driven by product mix and discounting strategies.",
            "conversion_rate": "Conversion changes often relate to UI flow and checkout performance.",
            "retention_rate": "Retention indicates repeat purchase behavior and satisfaction.",
        }

        return insight_templates.get(metric, "This metric provides a useful signal about business performance.")
