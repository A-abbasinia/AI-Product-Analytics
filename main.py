from src.data.data_loader import DataLoader
from src.data.registry import DataRegistry
from src.engine.analytics_engine import AnalyticsEngine
from src.metrics.metric_registry import MetricRegistry
from src.engine.ai_query_engine import AIQueryEngine
from src.nlp.query_parser_v3 import QueryParserV3
from src.engine.groupby_engine import GroupByEngine
from src.semantic.table_relationships import TableRelationships

from src.ai_engine.insight_analyzer.trend_detector import TrendDetector
from src.ai_engine.insight_analyzer.anomaly_detector import AnomalyDetector

from src.ai_engine.dashboard_recommender.DashboardRecommender import DashboardRecommender

# NEW
from src.ai_engine.narrative_generator.narrative_generator import NarrativeGenerator


if __name__ == "__main__":

    loader = DataLoader(data_path="data/raw")
    loader.load_all()

    print("\n===================================")
    print("Loaded Tables:")
    print("===================================")
    print(DataRegistry.list_tables())

    customers_df = DataRegistry.get("customers")
    print("\nCustomers shape:", customers_df.shape)
    print(customers_df.head())

    print("\n===================================")
    print("Table Relationships:")
    print("===================================")
    for rel in TableRelationships.get_relationships():
        print(rel)

    print("\n===================================")
    print("Analytics Engine Tests")
    print("===================================")

    print("Total Revenue:", AnalyticsEngine.total_revenue())
    print("Total Orders:", AnalyticsEngine.total_orders())
    print("Average Order Value:", AnalyticsEngine.average_order_value())

    print("\nRevenue per Customer (head):")
    print(AnalyticsEngine.revenue_per_customer().head())

    print("\n===================================")
    print("Metric Registry Test")
    print("===================================")

    metric = MetricRegistry.get_metric("revenue")
    print("Revenue via registry:", metric())

    print("\n===================================")
    print("AI Query Engine Tests")
    print("===================================")

    queries = [
        "what is the total revenue",
        "how many orders did we have",
        "revenue for user_id 5",
        "orders with completed status"
    ]

    for q in queries:
        print("\nQ:", q)
        try:
            result = AIQueryEngine.answer(q)
            print("A:", result)
        except Exception as e:
            print("Error:", e)

    print("\n===================================")
    print("GroupBy Engine Tests")
    print("===================================")

    group_tests = [
        ("revenue", "month"),
        ("orders", "year"),
        ("average_order_value", "category")
    ]

    grouped_df = None

    for metric_name, dim in group_tests:
        print(f"\nMetric: {metric_name}, GroupBy: {dim}")
        try:
            df_group = GroupByEngine.compute(metric_name, dim)
            print(df_group.head())

            if metric_name == "revenue" and dim == "month":
                grouped_df = df_group

        except Exception as e:
            print("Error:", e)

    print("\n===================================")
    print("Trend Detector Tests")
    print("===================================")

    insights = []
    joined_df = None

    try:
        joined_df = loader.get_joined_dataset()

        if grouped_df is None:
            grouped_df = GroupByEngine.compute("revenue", "month")

        trend_detector = TrendDetector()
        insights = trend_detector.analyze(grouped_df, "month", "revenue")

        print("Trend insights:")
        if not insights:
            print("No strong trends detected.")
        else:
            for ins in insights:
                print("-", ins["description"])

    except Exception as e:
        print("Trend Detector Error:", e)

    print("\n===================================")
    print("Anomaly Detector Tests")
    print("===================================")

    anomalies = []

    try:
        if grouped_df is None:
            grouped_df = GroupByEngine.compute("revenue", "month")

        an = AnomalyDetector()
        anomalies = an.analyze(
            df=grouped_df,
            dim="month",
            metric="revenue",
            joined_df=joined_df,
            z_thr=1.5,
            mz_thr=2.5,
            debug_force=True
        )

        print("Anomaly Report:")
        print(anomalies)

    except Exception as e:
        print("Anomaly Detector Error:", e)

    print("\n===================================")
    print("Dashboard Recommender Engine Test")
    print("===================================")

    recommender = DashboardRecommender()
    narrator = NarrativeGenerator()

    domains = ["product", "marketing", "behavior"]

    for domain in domains:
        print(f"\n=== {domain.upper()} DASHBOARD ===")

        try:
            output = recommender.create_dashboard(domain)

            dashboard = output["dashboard"]
            dash_insights = output["insights"]
            dash_recommendations = output["recommendations"]

            print("\nDashboard JSON:")
            print(dashboard)

            print("\nInsights:")
            for ins in dash_insights:
                print("-", ins["metric"] + ":", ins["insight"])

            print("\nRecommendations:")
            for rec in dash_recommendations:
                print("-", rec["metric"] + ":", rec["recommendations"])

            # ----------------------------------------------------
            # *** NarrativeGenerator-Compatible Data Formatting ***
            # ----------------------------------------------------

            # Convert trend insights → Narrative format
            parsed_trends = []
            for t in insights:
                desc = t["description"].lower()
                parsed_trends.append({
                    "metric": "revenue",
                    "value": None,
                    "direction": "down" if "decrease" in desc else "up"
                })

            # Convert anomaly → Narrative format
            parsed_anomalies = []
            if isinstance(anomalies, list):
                for a in anomalies:
                    parsed_anomalies.append({
                        "metric": a.get("metric", "revenue"),
                        "value": a.get("value", None)
                    })

            # Extract insight texts
            insight_texts = [i["insight"] for i in dash_insights]

            # Extract recommendation texts
            recommendation_texts = []
            for r in dash_recommendations:
                recommendation_texts.extend(r["recommendations"])

            print("\nExecutive Narrative:")

            narrative = narrator.generate_full_narrative(
                domain=domain,
                metrics={
                    "total_revenue": AnalyticsEngine.total_revenue(),
                    "total_orders": AnalyticsEngine.total_orders(),
                    "avg_order_value": AnalyticsEngine.average_order_value()
                },
                trends=parsed_trends,
                anomalies=parsed_anomalies,
                insights=insight_texts,
                recommendations=recommendation_texts
            )

            print(narrative)

        except Exception as e:
            print("Dashboard Error:", e)

    print("\n===================================")
    print("Pipeline Completed Successfully")
    print("===================================")
