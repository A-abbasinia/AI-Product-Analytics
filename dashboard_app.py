import streamlit as st
import plotly.express as px

from src.data.data_loader import DataLoader
from src.data.registry import DataRegistry
from src.engine.analytics_engine import AnalyticsEngine
from src.engine.groupby_engine import GroupByEngine

from src.ai_engine.insight_analyzer.trend_detector import TrendDetector
from src.ai_engine.insight_analyzer.anomaly_detector import AnomalyDetector
from src.ai_engine.dashboard_recommender.DashboardRecommender import DashboardRecommender
from src.ai_engine.narrative_generator.narrative_generator import NarrativeGenerator


st.set_page_config(layout="wide")

st.title("AI Product Analytics Dashboard")

# -----------------------------
# Load Data
# -----------------------------

loader = DataLoader(data_path="data/raw")
loader.load_all()

joined_df = loader.get_joined_dataset()

# -----------------------------
# KPI Section
# -----------------------------

st.header("Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"{AnalyticsEngine.total_revenue():,.0f}")
col2.metric("Total Orders", AnalyticsEngine.total_orders())
col3.metric("Average Order Value", f"{AnalyticsEngine.average_order_value():,.0f}")

# -----------------------------
# Revenue Trend
# -----------------------------

st.header("Revenue Trend")

revenue_month = GroupByEngine.compute("revenue", "month")

fig = px.line(
    revenue_month,
    x="month",
    y="revenue",
    markers=True,
    title="Monthly Revenue"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Trend Detection
# -----------------------------

trend_detector = TrendDetector()
trends = trend_detector.analyze(revenue_month, "month", "revenue")

st.header("Detected Trends")

if not trends:
    st.info("No strong trends detected.")
else:
    for t in trends:
        st.write("•", t["description"])

# -----------------------------
# Anomaly Detection
# -----------------------------

st.header("Anomaly Detection")

an = AnomalyDetector()

anomalies = an.analyze(
    df=revenue_month,
    dim="month",
    metric="revenue",
    joined_df=joined_df,
    debug_force=True
)

st.json(anomalies)

# -----------------------------
# Dashboard Recommender
# -----------------------------

st.header("Recommended Dashboards")

recommender = DashboardRecommender()

domains = ["product", "marketing", "behavior"]

for domain in domains:

    st.subheader(domain.capitalize())

    result = recommender.create_dashboard(domain)

    st.write("Dashboard Layout")
    st.json(result["dashboard"])

    st.write("Insights")
    for ins in result["insights"]:
        st.write("•", ins["insight"])

    st.write("Recommendations")
    for rec in result["recommendations"]:
        for r in rec["recommendations"]:
            st.write("•", r)

# -----------------------------
# Narrative
# -----------------------------

st.header("Executive Narrative")

narrator = NarrativeGenerator()

narrative = narrator.generate_full_narrative(
    domain="product",
    metrics={
        "total_revenue": AnalyticsEngine.total_revenue(),
        "total_orders": AnalyticsEngine.total_orders(),
        "avg_order_value": AnalyticsEngine.average_order_value()
    },
    trends=[],
    anomalies=[],
    insights=["Revenue fluctuates due to demand changes."],
    recommendations=["Improve product recommendation engine."]
)

st.text(narrative)
