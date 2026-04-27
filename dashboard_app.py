import streamlit as st
import plotly.express as px

from src.data.data_loader import DataLoader
from src.engine.analytics_engine import AnalyticsEngine
from src.engine.groupby_engine import GroupByEngine

from src.ai_engine.insight_analyzer.trend_detector import TrendDetector
from src.ai_engine.insight_analyzer.anomaly_detector import AnomalyDetector
from src.ai_engine.dashboard_recommender.DashboardRecommender import DashboardRecommender
from src.ai_engine.narrative_generator.narrative_generator import NarrativeGenerator


st.set_page_config(layout="wide")
st.title("AI Product Analytics Dashboard")

# ----------------------------------
# Load Data (cached)
# ----------------------------------

@st.cache_data
def load_data():
    loader = DataLoader(data_path="data/raw")
    loader.load_all()
    joined = loader.get_joined_dataset()
    return loader, joined

loader, joined_df = load_data()


# ----------------------------------
# KPI Computation (cached)
# ----------------------------------

@st.cache_data
def compute_kpis():
    total_revenue = AnalyticsEngine.total_revenue()
    total_orders = AnalyticsEngine.total_orders()
    aov = AnalyticsEngine.average_order_value()
    return total_revenue, total_orders, aov

total_revenue, total_orders, aov = compute_kpis()


# ----------------------------------
# Page Tabs
# ----------------------------------

tab1, tab2, tab3 = st.tabs([
    "Business Overview",
    "AI Insights",
    "Executive Report"
])


# ======================================================
# TAB 1 — BUSINESS OVERVIEW
# ======================================================

with tab1:

    st.header("Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"{total_revenue:,.0f}")
    col2.metric("Total Orders", total_orders)
    col3.metric("Average Order Value", f"{aov:,.0f}")

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


# ======================================================
# TAB 2 — AI INSIGHTS
# ======================================================

with tab2:

    # -----------------------------
    # Trend Detection
    # -----------------------------

    st.header("Detected Trends")

    trend_detector = TrendDetector()

    trends = trend_detector.analyze(
        revenue_month,
        "month",
        "revenue"
    )

    if not trends:
        st.info("No strong trends detected.")
    else:
        for t in trends:
            desc = t.get("description", str(t))
            st.warning(desc)


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

    if anomalies.get("has_anomaly"):

        st.error("Revenue anomaly detected")

        st.write(
            "Deviation:",
            f"{anomalies.get('deviation_pct',0):.2f}%"
        )

        if "root_causes" in anomalies:

            st.subheader("Possible Root Causes")

            for cause in anomalies["root_causes"]:

                dim = cause.get("dimension","?")
                seg = cause.get("segment","?")
                impact = cause.get("contribution_pct",0)

                st.write(
                    f"• {dim} = {seg} "
                    f"(Impact: {impact:.1f}%)"
                )

    else:

        st.success("No anomaly detected")


    # -----------------------------
    # Dashboard Recommender
    # -----------------------------

    st.header("AI Recommended Dashboards")

    recommender = DashboardRecommender()

    domains = ["product", "marketing", "behavior"]

    all_insights = []
    all_recommendations = []

    for domain in domains:

        st.subheader(domain.capitalize())

        result = recommender.create_dashboard(domain)

        st.write("Dashboard Layout")

        st.json(result["dashboard"])

        st.write("Insights")

        for ins in result["insights"]:

            text = ins.get("insight", str(ins))

            st.info(text)

            all_insights.append(text)

        st.write("Recommendations")

        for rec in result["recommendations"]:

            for r in rec.get("recommendations",[]):

                st.write("•", r)

                all_recommendations.append(r)


# ======================================================
# TAB 3 — EXECUTIVE REPORT
# ======================================================

with tab3:

    st.header("Executive Narrative")

    narrator = NarrativeGenerator()

    narrative = narrator.generate_full_narrative(
        domain="product",
        metrics={
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "avg_order_value": aov
        },
        trends=trends if trends else [],
        anomalies=anomalies if anomalies else {},
        insights=all_insights,
        recommendations=all_recommendations
    )

    st.text_area(
        "AI Generated Business Report",
        narrative,
        height=300
    )


    # -----------------------------
    # Business Problems
    # -----------------------------

    st.header("Business Problems Identified")

    problems = [
        "Revenue shows unstable trend across months.",
        "Certain customer segments contribute disproportionately to revenue spikes.",
        "Product recommendation effectiveness may be limited."
    ]

    for p in problems:
        st.write("•", p)


    # -----------------------------
    # Proposed Solutions
    # -----------------------------

    st.header("Proposed Solutions")

    solutions = {
        "Revenue instability": [
            "Introduce seasonal marketing campaigns",
            "Implement dynamic pricing strategies",
            "Improve demand forecasting"
        ],
        "Segment concentration": [
            "Expand marketing to new customer segments",
            "Launch targeted promotions",
            "Analyze high-value segments deeper"
        ],
        "Recommendation limitations": [
            "Improve AI recommendation model",
            "Use user behavior signals",
            "Introduce personalized bundles"
        ]
    }

    for problem, recs in solutions.items():

        st.subheader(problem)

        for r in recs:
            st.write("•", r)
