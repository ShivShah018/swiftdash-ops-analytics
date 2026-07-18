# utils/kpi.py
"""KPI calculation helpers for the SwiftDash Streamlit dashboard.
All functions accept pandas DataFrames and return simple scalars suitable for
`st.metric` display.
"""

import pandas as pd
from config import ON_TIME_CUTOFF_MINUTES

def total_orders(df_orders: pd.DataFrame) -> int:
    """Return the total number of orders."""
    return int(df_orders.shape[0])

def total_revenue(df_orders: pd.DataFrame) -> float:
    """Calculate total revenue from the `total_amount` column.
    If the column is missing, a fallback of 0 is returned.
    """
    if "total_amount" in df_orders.columns:
        return float(df_orders["total_amount"].sum())
    return 0.0

def on_time_rate(df_orders: pd.DataFrame) -> float:
    """Proportion of orders delivered on time.
    Uses the `travel_time_mins` column from delivery logs if present; otherwise
    falls back to a column `on_time` (boolean).
    Returns a float between 0 and 1.
    """
    if "travel_time_mins" in df_orders.columns:
        on_time = df_orders["travel_time_mins"] <= ON_TIME_CUTOFF_MINUTES
        return on_time.mean()
    if "on_time" in df_orders.columns:
        return df_orders["on_time"].mean()
    return 0.0

def active_customers(df_customers: pd.DataFrame) -> int:
    """Count active customers. Assumes a boolean `is_active` column.
    If missing, counts all customers.
    """
    if "is_active" in df_customers.columns:
        return int(df_customers[df_customers["is_active"]].shape[0])
    return int(df_customers.shape[0])
