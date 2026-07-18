# utils/charts.py
"""Plotly chart helpers for the SwiftDash Streamlit dashboard.
Each function receives the relevant pandas DataFrames and returns a Plotly
Figure ready to be rendered via `st.plotly_chart`.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import ON_TIME_CUTOFF_MINUTES

def monthly_revenue_trend(df_orders: pd.DataFrame):
    """Line chart of total revenue per month."""
    df = df_orders.copy()
    df["month"] = pd.to_datetime(df["order_date"]).dt.to_period("M").astype(str)
    monthly = df.groupby("month")["total_amount"].sum().reset_index()
    fig = px.line(monthly, x="month", y="total_amount", title="Monthly Revenue Trend")
    fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
    return fig

def top_cities(df_orders: pd.DataFrame, top_n: int = 10):
    """Bar chart of revenue by city (top N).
    Uses 'customer_city' if present, otherwise falls back to 'city'.
    Returns an empty figure with a message when no city column is available.
    """
    # Determine city column
    if "customer_city" in df_orders.columns:
        city_col = "customer_city"
    elif "city" in df_orders.columns:
        city_col = "city"
    else:
        # No city information – return empty figure
        fig = go.Figure()
        fig.update_layout(title="No city data available")
        return fig
    city_rev = (
        df_orders.groupby(city_col)["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
    )
    fig = px.bar(city_rev.head(top_n), x=city_col, y="total_amount", title="Top Cities by Revenue")
    fig.update_layout(xaxis_title="City", yaxis_title="Revenue ($)")
    return fig

def revenue_by_cuisine(df_orders: pd.DataFrame, df_restaurants: pd.DataFrame):
    """Bar chart of revenue per cuisine type."""
    merged = df_orders.merge(df_restaurants, left_on="restaurant_id", right_on="restaurant_id", how="left")
    cuisine_rev = (
        merged.groupby("cuisine_type")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
    )
    fig = px.bar(cuisine_rev, x="cuisine_type", y="total_amount", title="Revenue by Cuisine")
    fig.update_layout(xaxis_title="Cuisine", yaxis_title="Revenue ($)")
    return fig

def top_restaurants(df_orders: pd.DataFrame, top_n: int = 10):
    """Bar chart of top restaurants by revenue."""
    top = (
        df_orders.groupby("restaurant_name")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
    )
    fig = px.bar(top.head(top_n), x="restaurant_name", y="total_amount", title="Top Restaurants by Revenue")
    fig.update_layout(xaxis_title="Restaurant", yaxis_title="Revenue ($)")
    return fig

def delivery_time_distribution(df_orders: pd.DataFrame):
    """Histogram of delivery travel times."""
    if "travel_time_mins" not in df_orders.columns:
        return go.Figure()
    fig = px.histogram(df_orders, x="travel_time_mins", nbins=30, title="Delivery Time Distribution")
    fig.update_layout(xaxis_title="Travel Time (minutes)", yaxis_title="Orders")
    return fig

def on_time_by_traffic(df_orders: pd.DataFrame):
    """Bar chart of on‑time delivery rate per traffic condition."""
    if "traffic" not in df_orders.columns:
        return go.Figure()
    df = df_orders.copy()
    df["on_time"] = df["travel_time_mins"] <= ON_TIME_CUTOFF_MINUTES
    traffic_rate = df.groupby("traffic")["on_time"].mean().reset_index()
    fig = px.bar(traffic_rate, x="traffic", y="on_time", title="On‑Time Delivery Rate by Traffic")
    fig.update_layout(xaxis_title="Traffic", yaxis_title="On‑Time Rate", yaxis_tickformat="%")
    return fig

def segment_distribution(df_customers: pd.DataFrame):
    """Pie chart of customer segment distribution."""
    if "segment" not in df_customers.columns:
        return go.Figure()
    seg_counts = df_customers["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    fig = px.pie(seg_counts, names="segment", values="count", title="Customer Segment Distribution")
    return fig

def revenue_by_segment(df_orders: pd.DataFrame, df_customers: pd.DataFrame):
    """Bar chart of revenue per customer segment.
    Uses the 'segment' column already merged into df_orders by get_filtered_data."""
    if "segment" not in df_orders.columns:
        return go.Figure()
    seg_rev = (
        df_orders.groupby("segment")["total_amount"].sum().reset_index().sort_values("total_amount", ascending=False)
    )
    fig = px.bar(seg_rev, x="segment", y="total_amount", title="Revenue by Customer Segment")
    fig.update_layout(xaxis_title="Segment", yaxis_title="Revenue ($)")
    return fig
