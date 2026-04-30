from .KPISelector import KPISelector
from .ChartRecommender import ChartRecommender
from .LayoutBuilder import LayoutBuilder
from .InsightGenerator import InsightGenerator
from .RecommendationEngine import RecommendationEngine

class DashboardRecommender:
    def __init__(self):
        self.kpi_selector = KPISelector()
        self.chart_recommender = ChartRecommender()
        self.layout_builder = LayoutBuilder()
        self.insight_generator = InsightGenerator()
        self.recommend_engine = RecommendationEngine()

    def create_dashboard(self, domain):
        kpis = self.kpi_selector.select_kpis(domain)

        chart_blocks = []
        insights = []
        recommendations = []

        for metric in kpis:
            chart_type = self.chart_recommender.choose_chart(metric)

            block = {
                "metric": metric,
                "type": chart_type,
                "size": "medium"
            }

            if chart_type == "kpi_card":
                block["size"] = "small"

            chart_blocks.append(block)

            insight = self.insight_generator.generate_insight(metric)
            insights.append({"metric": metric, "insight": insight})

            recs = self.recommend_engine.recommend(metric)
            recommendations.append({"metric": metric, "recommendations": recs})

        dashboard_json = self.layout_builder.build_dashboard(
            title=f"{domain.capitalize()} Analytics Dashboard",
            chart_blocks=chart_blocks
        )

        return {
            "dashboard": dashboard_json,
            "insights": insights,
            "recommendations": recommendations
        }
