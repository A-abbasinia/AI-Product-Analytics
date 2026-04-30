import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

from src.data.data_loader import DataLoader
from src.data.registry import registry
from src.engine.analytics_engine import AnalyticsEngine
from src.engine.groupby_engine import GroupByEngine

# AI Engines
from src.ai_engine.insight_analyzer.trend_detector import TrendDetector
from src.ai_engine.insight_analyzer.anomaly_detector import AnomalyDetector
from src.ai_engine.dashboard_recommender.DashboardRecommender import DashboardRecommender
from src.ai_engine.narrative_generator.narrative_generator import NarrativeGenerator


# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(layout="wide")
st.title("🤖 AI Product Analytics Dashboard")


# -------------------------------------------------------
# SQLite Connection
# -------------------------------------------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect(
        "product_analytics.db",
        check_same_thread=False
    )


# -------------------------------------------------------
# Initialize Data
# -------------------------------------------------------
@st.cache_resource
def init_data():
    loader = DataLoader(data_path="data/raw")
    loader.load_all()

    joined = loader.get_joined_dataset()
    registry.register("joined_dataset", joined)

    conn = get_connection()

    # Save all tables to SQLite
    for table in registry.list_tables():
        df = registry.get(table)
        df.to_sql(table, conn, if_exists="replace", index=False)

    return joined


joined_df = init_data()


# -------------------------------------------------------
# KPI Computation
# -------------------------------------------------------
@st.cache_data
def compute_kpis():
    return (
        AnalyticsEngine.total_revenue(),
        AnalyticsEngine.total_orders(),
        AnalyticsEngine.average_order_value()
    )


total_revenue, total_orders, aov = compute_kpis()


# -------------------------------------------------------
# Revenue Trend
# -------------------------------------------------------
@st.cache_data
def get_revenue_trend():
    return GroupByEngine.compute("revenue", "month")


revenue_month = get_revenue_trend()


# -------------------------------------------------------
# Tabs
# -------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Business Overview",
    "AI Insights",
    "Executive Report",
    "SQL Explorer 🔍",
    "Business Questions 📊",
    "Strategic Analysis 🧠"
])


# ======================================================
# BUSINESS OVERVIEW
# ======================================================
with tab1:

    st.header("📊 Key Metrics")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Revenue", f"{total_revenue:,.0f}")
    c2.metric("Total Orders", total_orders)
    c3.metric("Average Order Value", f"{aov:,.0f}")

    st.header("📈 Monthly Revenue Trend")

    fig = px.line(revenue_month, x="month", y="revenue", markers=True)
    st.plotly_chart(fig, use_container_width=True)


# ======================================================
# AI INSIGHTS
# ======================================================
with tab2:

    st.header("Trend Detection")

    trend_detector = TrendDetector()
    trends = trend_detector.analyze(revenue_month, "month", "revenue")

    if not trends:
        st.info("No strong trends detected.")
    else:
        for t in trends:
            st.warning(t["description"])

    st.header("Anomaly Detection")

    anomaly_detector = AnomalyDetector()

    anomalies = anomaly_detector.analyze(
        df=revenue_month,
        dim="month",
        metric="revenue",
        joined_df=joined_df,
        debug_force=True
    )

    if anomalies.get("has_anomaly"):

        st.error("Revenue anomaly detected")
        st.write("Deviation:", f"{anomalies.get('deviation_pct',0):.2f}%")

        if "root_causes" in anomalies:
            st.subheader("Possible Root Causes")
            for cause in anomalies["root_causes"]:
                st.write(
                    f"• {cause['dimension']} = {cause['segment']} "
                    f"(Impact {cause['contribution_pct']:.1f}%)"
                )
    else:
        st.success("No anomaly detected")

    st.header("AI Recommended Dashboards")

    recommender = DashboardRecommender()
    insights_all = []
    recs_all = []

    for domain in ["product", "marketing", "behavior"]:
        st.subheader(domain.capitalize())
        result = recommender.create_dashboard(domain)

        st.json(result["dashboard"])

        for ins in result["insights"]:
            insights_all.append(ins["insight"])
            st.info(ins["insight"])

        for rec in result["recommendations"]:
            for r in rec["recommendations"]:
                recs_all.append(r)
                st.write("•", r)


# ======================================================
# EXECUTIVE REPORT
# ======================================================
with tab3:

    st.header("🧠 Executive Narrative")

    narrator = NarrativeGenerator()

    narrative = narrator.generate_full_narrative(
        domain="product",
        metrics={
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "avg_order_value": aov
        },
        trends=trends,
        anomalies=anomalies,
        insights=insights_all,
        recommendations=recs_all
    )

    st.text_area("AI Generated Business Report", narrative, height=350)


# ======================================================
# SQL EXPLORER (FIXED & SAFE)
# ======================================================
with tab4:

    st.header("SQL Explorer 🔍")

    conn = get_connection()

    PRESET_QUERIES = {

        "Total Revenue": """
        SELECT SUM(amount) AS total_revenue
        FROM transactions
        """,

        "Monthly Revenue": """
        SELECT
            strftime('%Y-%m', transaction_date) AS month,
            SUM(amount) AS revenue
        FROM transactions
        GROUP BY month
        ORDER BY month
        """,

        "Top 10 Products": """
        SELECT
            p.name AS product_name,
            SUM(od.quantity) AS total_sold
        FROM orderdetails od
        JOIN products p
            ON od.product_id = p.product_id
        GROUP BY p.name
        ORDER BY total_sold DESC
        LIMIT 10
        """
    }

    q = st.selectbox("Choose query", list(PRESET_QUERIES.keys()))

    if st.button("Run Query"):
        df = pd.read_sql_query(PRESET_QUERIES[q], conn)
        st.dataframe(df, use_container_width=True)
        st.session_state["sql_df"] = df
        if df.shape[1] == 2:
            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Custom SQL")

    user_query = st.text_area("SQL")

    if st.button("Execute"):
        try:
            df = pd.read_sql_query(user_query, conn)
            st.dataframe(df, use_container_width=True)
            st.session_state["sql_df"] = df
        except Exception as e:
            st.error(str(e))


# ======================================================
# BUSINESS QUESTIONS (PROFESSIONAL VERSION)
# ======================================================
with tab5:

    st.header("📊 Strategic Business Insights")

    conn = get_connection()

    # -------------------------------------------------
    # USER METRICS
    # -------------------------------------------------
    c1, c2, c3 = st.columns(3)

    q_users = "SELECT COUNT(DISTINCT user_id) AS total_users FROM customers"
    q_buyers = "SELECT COUNT(DISTINCT user_id) AS buyers FROM orders"
    q_return = """
    SELECT COUNT(*) AS returning_customers
    FROM (
        SELECT user_id
        FROM orders
        GROUP BY user_id
        HAVING COUNT(order_id) > 1
    )
    """

    total_users = pd.read_sql_query(q_users, conn).iloc[0]["total_users"]
    buyers = pd.read_sql_query(q_buyers, conn).iloc[0]["buyers"]
    returning = pd.read_sql_query(q_return, conn).iloc[0]["returning_customers"]

    c1.metric("👥 Total Users", total_users)
    c2.metric("🛒 Buyers", buyers)
    c3.metric("🔁 Returning Customers", returning)

    st.divider()

    # -------------------------------------------------
    # AI CONSULTATION IMPACT
    # -------------------------------------------------
    st.subheader("🤖 Impact of AI Consultation on Revenue")

    q_ai_sales = """
    SELECT
        CASE
            WHEN o.user_id IN (SELECT DISTINCT user_id FROM consultation)
            THEN 'AI Users'
            ELSE 'Non-AI Users'
        END AS user_type,
        AVG(t.amount) AS avg_revenue
    FROM transactions t
    JOIN orders o
        ON t.order_id = o.order_id
    GROUP BY user_type
    """

    df_ai_sales = pd.read_sql_query(q_ai_sales, conn)
    st.dataframe(df_ai_sales, use_container_width=True)

    fig = px.bar(df_ai_sales, x="user_type", y="avg_revenue", color="user_type",
                 title="Average Revenue per User Type")
    st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # -------------------------------------------------
    # TOP SELLING PRODUCTS
    # -------------------------------------------------
    st.subheader("🏆 Top Selling Products")

    q_products = """
    SELECT
        p.name AS product_name,
        SUM(od.quantity) AS total_sold
    FROM orderdetails od
    JOIN products p
        ON od.product_id = p.product_id
    GROUP BY p.name
    ORDER BY total_sold DESC
    LIMIT 10
    """

    top_products = pd.read_sql_query(q_products, conn)
    col1, col2 = st.columns([2, 3])

    with col1:
        st.dataframe(top_products, use_container_width=True)
    with col2:
        fig = px.bar(top_products, x="product_name", y="total_sold",
                     title="Top 10 Best Selling Products")
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    # -------------------------------------------------
    # LOW STOCK ALERT
    # -------------------------------------------------
    st.subheader("⚠️ Low Stock Products")

    q_stock = """
    SELECT name AS product, stock_quantity
    FROM products
    WHERE stock_quantity < 20
    ORDER BY stock_quantity ASC
    """

    low_stock = pd.read_sql_query(q_stock, conn)
    if len(low_stock) > 0:
        fig = px.bar(low_stock, x="product", y="stock_quantity",
                     title="Products with Low Inventory", color="stock_quantity")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(low_stock, use_container_width=True)
    else:
        st.success("✅ No low stock products")

    st.divider()

    # -------------------------------------------------
    # MARKETING CAMPAIGN PERFORMANCE
    # -------------------------------------------------
    st.subheader("📣 Marketing Campaign Performance")

    q_marketing = """
    SELECT
        campaign_id,
        budget,
        clicks,
        conversions,
        ROUND((conversions * 1.0 / clicks) * 100, 2) AS conversion_rate
    FROM marketingcampaigns
    ORDER BY conversion_rate DESC
    """

    marketing = pd.read_sql_query(q_marketing, conn)
    col1, col2 = st.columns([2, 3])

    with col1:
        st.dataframe(marketing, use_container_width=True)
    with col2:
        fig = px.bar(marketing, x="campaign_id", y="conversion_rate",
                     title="Marketing Campaign Conversion Rate (%)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # -------------------------------------------------
    # TOTAL REVENUE
    # -------------------------------------------------
    st.subheader("💰 Revenue Overview")

    q_rev = "SELECT SUM(amount) AS total_revenue FROM transactions"
    total_revenue_val = pd.read_sql_query(q_rev, conn).iloc[0]["total_revenue"]
    st.metric("Total Revenue", f"{total_revenue_val:,.0f}")


# ======================================================
# STRATEGIC ANALYSIS
# ======================================================
# ======================================================
# STRATEGIC ANALYSIS (FULL CASE STUDY)
# ======================================================
with tab6:

    st.header("🧠 Strategic Business Analysis")

    conn = get_connection()

    # ==================================================
    # 1. SQL METRICS LAYER
    # ==================================================

    st.subheader("1️⃣ SQL Metrics Layer")

    sql_queries = {

        "Total Revenue":

        """
        SELECT SUM(amount) AS total_revenue
        FROM transactions
        """,

        "Monthly Revenue":

        """
        SELECT
            strftime('%Y-%m', transaction_date) AS month,
            SUM(amount) AS revenue
        FROM transactions
        GROUP BY month
        ORDER BY month
        """,

        "Conversion Rate":

        """
        SELECT
            COUNT(DISTINCT o.user_id) * 1.0 /
            COUNT(DISTINCT c.user_id) AS conversion_rate
        FROM customers c
        LEFT JOIN orders o
        ON c.user_id = o.user_id
        """,

        "Top Products":

        """
        SELECT
            p.name,
            SUM(od.quantity) AS total_sales
        FROM orderdetails od
        JOIN products p
        ON od.product_id = p.product_id
        GROUP BY p.name
        ORDER BY total_sales DESC
        LIMIT 10
        """,

        "Customer Retention":

        """
        SELECT
            COUNT(*) AS returning_customers
        FROM (
            SELECT user_id
            FROM orders
            GROUP BY user_id
            HAVING COUNT(order_id) > 1
        )
        """

    }

    metric = st.selectbox("Select Metric SQL", list(sql_queries.keys()))

    st.code(sql_queries[metric], language="sql")

    if st.button("Run Metric Query"):

        df = pd.read_sql_query(sql_queries[metric], conn)
        st.dataframe(df)

    st.divider()

    # ==================================================
    # 2. DASHBOARDS
    # ==================================================

    st.subheader("2️⃣ Business Dashboards")

    # ---------------------------
    # PRODUCT DASHBOARD
    # ---------------------------

    st.markdown("### Product Dashboard")

    q_products = """
    SELECT
        p.name,
        SUM(od.quantity) AS sales
    FROM orderdetails od
    JOIN products p
    ON od.product_id = p.product_id
    GROUP BY p.name
    ORDER BY sales DESC
    LIMIT 10
    """

    df_products = pd.read_sql_query(q_products, conn)

    fig = px.bar(
        df_products,
        x="name",
        y="sales",
        title="Top Selling Products"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # REVENUE DASHBOARD
    # ---------------------------

    st.markdown("### Revenue Dashboard")

    q_revenue = """
    SELECT
        strftime('%Y-%m', transaction_date) AS month,
        SUM(amount) AS revenue
    FROM transactions
    GROUP BY month
    """

    df_rev = pd.read_sql_query(q_revenue, conn)

    fig = px.line(
        df_rev,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------------------
    # MARKETING DASHBOARD
    # ---------------------------

    st.markdown("### Marketing Dashboard")

    q_marketing = """
    SELECT
        campaign_id,
        clicks,
        conversions,
        conversions * 1.0 / clicks AS conversion_rate
    FROM marketingcampaigns
    """

    df_marketing = pd.read_sql_query(q_marketing, conn)

    fig = px.bar(
        df_marketing,
        x="campaign_id",
        y="conversion_rate",
        title="Campaign Conversion Rate"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ==================================================
    # 3. BUSINESS PROBLEM ANALYSIS (ENHANCED ENGLISH)
    # ==================================================

    st.subheader("3️⃣ Business Problems Identified")

    st.markdown("""
    This section highlights the most critical business challenges discovered through data analysis.
    Each problem is presented with a clear description and supporting data evidence.
    """)

    problems = [
        {
            "title": "🚫 Low Conversion Rate",
            "desc": """
            Only a small portion of website visitors end up making a purchase.
            Root causes may include high checkout friction, insufficient trust signals,
            or suboptimal AI product recommendations.
            """,
            "data_cause": "Low ratio of users with completed orders compared to total visitors."
        },
        {
            "title": "⚠️ Revenue Concentration Risk",
            "desc": """
            A significant share of total revenue is generated by only a few top products.
            Any decline in their performance can drastically impact overall revenue stability.
            """,
            "data_cause": "Top 3 products account for more than 50% of total sales volume."
        },
        {
            "title": "🔁 Low Customer Retention",
            "desc": """
            Most customers complete a single purchase and never return.
            This increases Customer Acquisition Cost (CAC) and lowers overall Lifetime Value (LTV).
            """,
            "data_cause": "Over 70% of users in the orders table have only one recorded purchase."
        }
    ]

    # Styled info boxes for cleaner presentation
    for p in problems:
        st.markdown(f"""
        <div style="background-color:#F8F9FA;padding:16px;border-radius:8px;margin-bottom:12px;
                    border-left:5px solid #007BFF;">
            <h5 style="margin:0;">{p['title']}</h5>
            <p style="margin:6px 0;color:#444;">{p['desc']}</p>
            <p style="margin:6px 0;color:#666;font-size:13px;">
                <b>Data Insight:</b> {p['data_cause']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ==================================================
    # 4. SOLUTIONS
    # ==================================================

    st.subheader("4️⃣ Proposed Solutions")

    solutions = pd.DataFrame({

        "Problem":[

            "Low Conversion Rate",
            "Low Conversion Rate",
            "Low Conversion Rate",

            "Revenue Concentration",
            "Revenue Concentration",
            "Revenue Concentration",

            "Low Customer Retention",
            "Low Customer Retention",
            "Low Customer Retention"
        ],

        "Solution":[

            "Improve AI recommendation accuracy",
            "Optimize product pages",
            "Add social proof and reviews",

            "Introduce cross-sell recommendations",
            "Create product bundles",
            "Promote long-tail products",

            "Launch loyalty program",
            "Remarketing email campaigns",
            "Personalized recommendations"
        ]

    })

    st.dataframe(solutions, use_container_width=True)

    st.divider()
    # ==================================================
    # 5. PRIORITIZED PRODUCT BACKLOG
    # ==================================================

    st.subheader("5️⃣ Prioritized Product Backlog")

    st.markdown("""
    This matrix prioritizes initiatives based on **Impact (business value)** 
    and **Effort (implementation complexity)**.

    High‑impact and low‑effort initiatives are **Quick Wins** and should be prioritized first.
    """)

    # -----------------------------
    # DATA
    # -----------------------------
    backlog = pd.DataFrame({
        "Task": [
            "Improve recommendation ranking",
            "Cross‑sell recommendation engine",
            "Loyalty program implementation",
            "Optimize product page UX",
            "Launch remarketing campaigns",
            "Create product bundles",
            "Promote long‑tail products",
            "Integrate reviews & rating system",
            "AI‑based personalization engine"
        ],

        "Impact": [9, 9, 8, 7, 8, 7, 6, 6, 8],
        "Effort": [5, 6, 8, 5, 4, 6, 5, 3, 8],

        "BusinessValue": [90, 80, 85, 70, 88, 65, 50, 60, 95]
    })


    # -----------------------------
    # CLASSIFY ZONES
    # -----------------------------
    def classify(row):

        if row["Impact"] >= 8 and row["Effort"] <= 5:
            return "Quick Wins"

        if row["Impact"] >= 8 and row["Effort"] > 5:
            return "Strategic Bets"

        if row["Impact"] < 7 and row["Effort"] <= 5:
            return "Low Value"

        return "Heavy Projects"


    backlog["Zone"] = backlog.apply(classify, axis=1)

    zone_colors = {
        "Quick Wins": "#2ecc71",
        "Strategic Bets": "#f1c40f",
        "Low Value": "#e74c3c",
        "Heavy Projects": "#e67e22"
    }

    # -----------------------------
    # SCATTER PLOT
    # -----------------------------
    fig = px.scatter(

        backlog,
        x="Effort",
        y="Impact",
        size="BusinessValue",
        color="Zone",

        hover_name="Task",

        hover_data={
            "Impact": True,
            "Effort": True,
            "BusinessValue": True,
            "Zone": True
        },

        color_discrete_map=zone_colors,

        title="Impact vs Effort Prioritization Matrix"
    )

    # -----------------------------
    # QUADRANT LINES
    # -----------------------------
    fig.add_vline(x=5.5, line_dash="dot", line_color="gray")
    fig.add_hline(y=7.5, line_dash="dot", line_color="gray")

    # -----------------------------
    # ZONE LABELS
    # -----------------------------
    fig.add_annotation(x=2.5, y=9,
                       text="Quick Wins",
                       showarrow=False,
                       font=dict(size=13),
                       bgcolor="rgba(46,204,113,0.2)")

    fig.add_annotation(x=8, y=9,
                       text="Strategic Bets",
                       showarrow=False,
                       font=dict(size=13),
                       bgcolor="rgba(241,196,15,0.25)")

    fig.add_annotation(x=2.5, y=3,
                       text="Low Value",
                       showarrow=False,
                       font=dict(size=13),
                       bgcolor="rgba(231,76,60,0.2)")

    fig.add_annotation(x=8, y=3,
                       text="Heavy Projects",
                       showarrow=False,
                       font=dict(size=13),
                       bgcolor="rgba(230,126,34,0.25)")

    # -----------------------------
    # STYLE CLEANUP
    # -----------------------------
    fig.update_traces(
        marker=dict(
            opacity=0.8,
            line=dict(width=1, color="black")
        )
    )

    fig.update_layout(

        template="plotly_white",

        height=600,

        legend_title="Strategy Category",

        xaxis=dict(
            title="Effort (Implementation Complexity →)",
            range=[0, 10],
            gridcolor="#ECECEC"
        ),

        yaxis=dict(
            title="Impact (Business Value ↑)",
            range=[0, 10],
            gridcolor="#ECECEC"
        ),

        margin=dict(l=40, r=40, t=70, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
# ==================================================
# 6. BACKLOG EXPLANATION
# ==================================================

st.subheader("6️⃣ Strategic Interpretation")

st.markdown("""
Below is a strategic interpretation of the initiatives shown in the Impact–Effort matrix.
Each category represents a different product strategy approach.
""")


# -----------------------------
# QUICK WINS
# -----------------------------
st.markdown("### ✅ Quick Wins")

st.markdown("""
**Definition:**  
High impact initiatives that require relatively low implementation effort.

**Strategy:**  
These should be prioritized immediately because they deliver strong business value quickly.

**Examples in our backlog:**

- Optimize product page UX  
- Launch remarketing campaigns  

**Expected outcome:**

- Faster conversion improvements  
- Immediate revenue uplift
""")


# -----------------------------
# STRATEGIC BETS
# -----------------------------
st.markdown("### 🚀 Strategic Bets")

st.markdown("""
**Definition:**  
High impact initiatives that require significant effort or long‑term investment.

**Strategy:**  
These are long‑term product investments that can create strong competitive advantages.

**Examples in our backlog:**

- Cross‑sell recommendation engine  
- Loyalty program implementation  
- AI‑based personalization engine  

**Expected outcome:**

- Stronger customer retention  
- Higher lifetime value (LTV)
""")


# -----------------------------
# LOW VALUE
# -----------------------------
st.markdown("### 💤 Low Value Initiatives")

st.markdown("""
**Definition:**  
Low impact initiatives with relatively small effort.

**Strategy:**  
These should usually be deprioritized unless they support a broader strategic initiative.

**Examples in our backlog:**

- Promote long‑tail products  

**Expected outcome:**

- Limited revenue impact
""")


# -----------------------------
# HEAVY PROJECTS
# -----------------------------
st.markdown("### ⚙️ Heavy Projects")

st.markdown("""
**Definition:**  
Initiatives that require substantial development effort while offering moderate impact.

**Strategy:**  
These should be carefully evaluated before committing resources.

**Examples in our backlog:**

- Product bundle creation  

**Expected outcome:**

- Moderate revenue improvements but slower ROI
""")

