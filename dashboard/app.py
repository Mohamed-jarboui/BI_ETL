"""
Sales dashboard on top of the PostgreSQL data warehouse.

Run from the repository root (after the ETL has loaded the warehouse):
    streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etl.config import Config  # noqa: E402

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e8e7e3"

st.set_page_config(page_title="E-commerce Sales Dashboard", page_icon="📊", layout="wide")


@st.cache_data(ttl=600)
def load_sales() -> pd.DataFrame:
    engine = create_engine(Config().PG_CONNECTION_STRING)
    query = """
        SELECT fs.order_id, fs.quantity, fs.revenue, fs.profit,
               d.date, d.year, d.month, d.day_name, d.day_of_week,
               p.product_name, p.category_name,
               c.customer_id, c.full_name,
               r.region_name
        FROM fact_sales fs
        JOIN dim_date d     ON fs.date_id = d.date_id
        JOIN dim_product p  ON fs.product_id = p.product_id
        JOIN dim_customer c ON fs.customer_id = c.customer_id
        JOIN dim_region r   ON fs.region_id = r.region_id
    """
    df = pd.read_sql(query, engine)
    df["date"] = pd.to_datetime(df["date"])
    df[["revenue", "profit"]] = df[["revenue", "profit"]].astype(float)
    return df


def money(x: float) -> str:
    if abs(x) >= 1_000_000:
        return f"{x / 1_000_000:.2f}M TND"
    if abs(x) >= 1_000:
        return f"{x / 1_000:.1f}K TND"
    return f"{x:,.0f} TND"


def style(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=INK, size=13),
        hoverlabel=dict(bgcolor="white", font_color=INK),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color=MUTED)),
        bargap=0.25,
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    return fig


def hbar(series: pd.Series, title: str) -> go.Figure:
    series = series.sort_values()
    fig = go.Figure(go.Bar(
        x=series.values, y=series.index, orientation="h",
        marker=dict(color=BLUE, cornerradius=4),
        text=[money(v) for v in series.values], textposition="outside",
        textfont=dict(color=MUTED, size=12),
        hovertemplate="%{y}<br>" + title + ": %{x:,.0f} TND<extra></extra>",
    ))
    fig = style(fig, height=max(260, 34 * len(series)))
    fig.update_xaxes(showticklabels=False, showgrid=False, range=[0, series.max() * 1.22])
    fig.update_yaxes(showgrid=False)
    return fig


try:
    sales = load_sales()
except Exception as e:  # warehouse not reachable or not loaded yet
    st.error(f"Could not read the data warehouse. Start PostgreSQL and run the ETL first.\n\n{e}")
    st.stop()

if sales.empty:
    st.warning("The warehouse is empty. Run the ETL first: `python -m etl.main`")
    st.stop()

# ---------- Header and filters ----------
st.title("E-commerce Sales Dashboard")
st.caption("Star-schema data warehouse (PostgreSQL), loaded by the Python ETL pipeline from MongoDB")

f1, f2, f3 = st.columns([2, 2, 2])
min_d, max_d = sales["date"].min().date(), sales["date"].max().date()
date_range = f1.date_input("Period", (min_d, max_d), min_value=min_d, max_value=max_d)
categories = f2.multiselect("Category", sorted(sales["category_name"].unique()))
regions = f3.multiselect("Region", sorted(sales["region_name"].unique()))

df = sales
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df = df[(df["date"] >= start) & (df["date"] <= end)]
if categories:
    df = df[df["category_name"].isin(categories)]
if regions:
    df = df[df["region_name"].isin(regions)]

if df.empty:
    st.info("No sales match these filters.")
    st.stop()

# ---------- KPIs ----------
revenue, profit = df["revenue"].sum(), df["profit"].sum()
orders = df["order_id"].nunique()
k = st.columns(5)
k[0].metric("Revenue", money(revenue))
k[1].metric("Profit", money(profit))
k[2].metric("Margin", f"{profit / revenue * 100:.1f}%")
k[3].metric("Orders", f"{orders:,}")
k[4].metric("Avg order value", money(revenue / orders))

st.divider()

# ---------- Trend ----------
st.subheader("Monthly revenue and profit")
monthly = df.set_index("date").resample("MS")[["revenue", "profit"]].sum().reset_index()
fig = go.Figure()
for col, color, name in [("revenue", BLUE, "Revenue"), ("profit", ORANGE, "Profit")]:
    fig.add_trace(go.Scatter(
        x=monthly["date"], y=monthly[col], name=name, mode="lines+markers",
        line=dict(color=color, width=2), marker=dict(size=8, line=dict(color="white", width=2)),
        hovertemplate="%{x|%b %Y}<br>" + name + ": %{y:,.0f} TND<extra></extra>",
    ))
fig = style(fig, height=360)
fig.update_layout(hovermode="x unified")
fig.update_yaxes(title_text="TND", title_font=dict(color=MUTED))
st.plotly_chart(fig, use_container_width=True)

# ---------- Category and region ----------
c1, c2 = st.columns(2)
with c1:
    st.subheader("Revenue by category")
    st.plotly_chart(hbar(df.groupby("category_name")["revenue"].sum(), "Revenue"), use_container_width=True)
with c2:
    st.subheader("Revenue by region")
    st.plotly_chart(hbar(df.groupby("region_name")["revenue"].sum(), "Revenue"), use_container_width=True)

# ---------- Tables ----------
t1, t2 = st.columns(2)
with t1:
    st.subheader("Top 10 products")
    top_products = (
        df.groupby(["product_name", "category_name"])
        .agg(units=("quantity", "sum"), revenue=("revenue", "sum"), profit=("profit", "sum"))
        .sort_values("revenue", ascending=False).head(10).reset_index()
    )
    top_products.columns = ["Product", "Category", "Units", "Revenue (TND)", "Profit (TND)"]
    st.dataframe(
        top_products, hide_index=True, use_container_width=True,
        column_config={c: st.column_config.NumberColumn(format="%.0f") for c in ["Revenue (TND)", "Profit (TND)"]},
    )
with t2:
    st.subheader("Top 10 customers")
    top_customers = (
        df.groupby(["full_name", "region_name"])
        .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False).head(10).reset_index()
    )
    top_customers.columns = ["Customer", "Region", "Orders", "Revenue (TND)"]
    st.dataframe(
        top_customers, hide_index=True, use_container_width=True,
        column_config={"Revenue (TND)": st.column_config.NumberColumn(format="%.0f")},
    )

st.caption("Demo data: generated with scripts/seed_mongo.py. Cancelled, refunded and failed orders are excluded by the ETL.")
