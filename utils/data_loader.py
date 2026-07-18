# utils/data_loader.py
"""Data loading utilities for the SwiftDash Streamlit dashboard.
All CSVs are read from the project's cleaned data directory and cached for
performance. The functions return pandas DataFrames ready for analysis.
"""

import pandas as pd
from pathlib import Path
import streamlit as st
from config import CLEAN_DIR, PROC_DIR

# Helper to construct file paths
def _csv_path(filename: str) -> Path:
    return CLEAN_DIR / filename

@st.cache_data(ttl=600)
def load_customers() -> pd.DataFrame:
    """Load cleaned customers CSV."""
    return pd.read_csv(_csv_path("customers_clean.csv"))

@st.cache_data(ttl=600)
def load_restaurants() -> pd.DataFrame:
    """Load cleaned restaurants CSV."""
    return pd.read_csv(_csv_path("restaurants_clean.csv"))

@st.cache_data(ttl=600)
def load_orders() -> pd.DataFrame:
    """Load cleaned orders CSV and parse dates."""
    df = pd.read_csv(_csv_path("orders_clean.csv"), parse_dates=["order_date"])
    # Ensure expected column names for downstream joins
    if "restaurant_id" not in df.columns:
        df = df.rename(columns={"restaurant": "restaurant_id"})
    return df

@st.cache_data(ttl=600)
def load_delivery_logs() -> pd.DataFrame:
    """Load cleaned delivery logs CSV."""
    return pd.read_csv(_csv_path("delivery_logs_clean.csv"))

@st.cache_data(ttl=600)
def load_customer_features() -> pd.DataFrame:
    """Load customer features CSV (RFM segments)."""
    return pd.read_csv(PROC_DIR / "customer_features.csv")

def get_unique_cities() -> list:
    """Return a list of distinct city names from the orders data.
    Uses 'customer_city' if present, otherwise falls back to any column containing 'city'.
    Returns empty list if no suitable column found."""
    orders = load_orders()
    if "customer_city" in orders.columns:
        city_col = "customer_city"
    elif "city" in orders.columns:
        city_col = "city"
    else:
        return []
    return sorted(orders[city_col].dropna().unique().tolist())

def get_unique_restaurants() -> list:
    """Return a list of distinct restaurant names from the restaurants data."""
    restaurants = load_restaurants()
    # Use 'name' column (exists in restaurants_clean.csv)
    if "name" in restaurants.columns:
        return sorted(restaurants["name"].dropna().unique().tolist())
    elif "restaurant_name" in restaurants.columns:
        return sorted(restaurants["restaurant_name"].dropna().unique().tolist())
    else:
        return []
