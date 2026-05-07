import streamlit as st
import plotly.express as px
import pandas as pd
from utils import *

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ---------------- CLEAN CORPORATE UI ----------------
st.markdown("""
<style>

/* -------- GLOBAL -------- */
.stApp {
    background: #0b1220;
    color: #cbd5e1;
    font-family: "Segoe UI", Roboto, sans-serif;
}

/* -------- MAIN -------- */
.block-container {
    padding: 2rem;
    animation: fadeIn 0.5s ease-in-out;
}

/* -------- TITLE -------- */
h1 {
    color: #f1f5f9;
    font-weight: 600;
}

/* -------- SIDEBAR -------- */
section[data-testid="stSidebar"] {
    background-color: #020617;
    border-right: 1px solid #1e293b;
}

/* -------- KPI -------- */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2937;
    padding: 16px;
    border-radius: 10px;
}

[data-testid="metric-container"]:hover {
    border: 1px solid #334155;
    transition: 0.2s;
}

/* -------- CHART CARDS -------- */
.element-container:has(.js-plotly-plot) {
    background: #111827;
    border-radius: 10px;
    padding: 12px;
    border: 1px solid #1f2937;
}

/* -------- TABLE -------- */
.stDataFrame {
    border: 1px solid #1f2937;
    border-radius: 10px;
}

/* -------- SUBHEADINGS -------- */
h2, h3 {
    color: #94a3b8;
}

/* -------- UPLOADER -------- */
[data-testid="stFileUploader"] {
    border: 1px dashed #334155;
    border-radius: 10px;
    padding: 12px;
}

/* -------- ANIMATION -------- */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("Sales Dashboard")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    df = clean_data(df)

    st.subheader("Data Preview")
    st.dataframe(df)

    # ---------------- FILTERS ----------------
    st.sidebar.header("Filters")

    region = st.sidebar.multiselect(
        "Select Region",
        df['Region'].unique(),
        default=df['Region'].unique()
    )

    product = st.sidebar.multiselect(
        "Select Product",
        df['Product'].unique(),
        default=df['Product'].unique()
    )

    df = df[(df['Region'].isin(region)) & (df['Product'].isin(product))]

    # ---------------- KPIs ----------------
    st.subheader("Key Metrics")

    col1, col2, col3 = st.columns(3)

    total_sales_value = total_sales(df)
    total_orders_value = total_orders(df)
    avg_order_value = total_sales_value / total_orders_value if total_orders_value else 0

    col1.metric("Total Sales", f"${total_sales_value:,.2f}")
    col2.metric("Total Orders", total_orders_value)
    col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")

    # ---------------- SALES TREND ----------------
    st.subheader("Sales Trend")

    monthly_df = monthly_sales(df)

    fig1 = px.line(
        monthly_df,
        x='Month',
        y='Sales',
        markers=True
    )

    fig1.update_traces(line=dict(color="#3b82f6", width=2))

    fig1.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font=dict(color="#cbd5e1")
    )

    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- TRENDING PRODUCT ----------------
    st.subheader("Trending Product")

    trend_df = df.groupby(["OrderDate", "Product"])["Sales"].sum().reset_index()
    pivot = trend_df.pivot(index="OrderDate", columns="Product", values="Sales").fillna(0)

    if len(pivot) > 2:
        growth = pivot.pct_change().sum()
        trending_product = growth.idxmax()
        st.success(f"{trending_product}")
    else:
        st.info("Not enough data for trend analysis")

    # ---------------- MOST BOUGHT ----------------
    st.subheader("Most Bought Product")

    most_bought = df.groupby("Product")["Quantity"].sum().sort_values(ascending=False)

    if not most_bought.empty:
        top_product = most_bought.index[0]
        top_qty = most_bought.iloc[0]
        st.info(f"{top_product} ({top_qty} units)")
    else:
        st.info("No data available")

    # ---------------- OTHER CHARTS ----------------
    st.subheader("Sales Analysis")

    col4, col5 = st.columns(2)

    # Region Pie
    region_df = sales_by_region(df)
    fig2 = px.pie(region_df, names='Region', values='Sales')

    fig2.update_traces(
        marker=dict(colors=["#3b82f6", "#6366f1", "#14b8a6", "#475569"])
    )

    fig2.update_layout(
        paper_bgcolor="#111827",
        font=dict(color="#cbd5e1")
    )

    col4.plotly_chart(fig2, use_container_width=True)

    # Product Bar
    product_df = sales_by_product(df)
    fig3 = px.bar(product_df, x='Product', y='Sales')

    fig3.update_traces(marker_color="#10b981")

    fig3.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font=dict(color="#cbd5e1")
    )

    col5.plotly_chart(fig3, use_container_width=True)

    # ---------------- TOP PRODUCTS ----------------
    st.subheader("Top Products")

    top_df = top_products(df)

    fig4 = px.bar(top_df, x='Product', y='Sales', text_auto=True)

    fig4.update_traces(marker_color="#64748b")

    fig4.update_layout(
        plot_bgcolor="#111827",
        paper_bgcolor="#111827",
        font=dict(color="#cbd5e1")
    )

    st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("Upload your dataset to begin")