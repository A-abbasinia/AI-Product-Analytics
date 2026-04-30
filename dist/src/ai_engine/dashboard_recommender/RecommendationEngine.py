class RecommendationEngine:
    def __init__(self):
        pass

    def recommend(self, metric):
        metric = metric.lower()

        recommendations = {
            "revenue": [
                "Increase promotions for high performing categories.",
                "Improve product recommendation logic.",
                "Run targeted retargeting ads."
            ],
            "conversion_rate": [
                "Simplify checkout flow.",
                "Add trust badges and social proof.",
                "Optimize product detail page."
            ],
            "sessions": [
                "Boost SEO content.",
                "Run influencer marketing.",
                "Activate referral program."
            ],
            "retention_rate": [
                "Introduce loyalty program.",
                "Improve post-purchase engagement.",
                "Send personalized offers."
            ]
        }

        return recommendations.get(metric, ["No recommendation available."])
