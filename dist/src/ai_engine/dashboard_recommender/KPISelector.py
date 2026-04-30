class KPISelector:
    def __init__(self):
        pass

    def select_kpis(self, domain):
        domain = domain.lower()

        product_kpis = [
            "revenue",
            "orders",
            "aov",
            "top_categories",
            "conversion_rate"
        ]

        marketing_kpis = [
            "sessions",
            "cac",
            "roas",
            "campaign_performance",
            "ctr"
        ]

        behavior_kpis = [
            "retention_rate",
            "repeat_purchase_rate",
            "clv",
            "cohort_performance"
        ]

        if domain == "product":
            return product_kpis
        if domain == "marketing":
            return marketing_kpis
        if domain == "behavior":
            return behavior_kpis

        return []
