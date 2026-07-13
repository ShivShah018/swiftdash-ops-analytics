"""
SwiftDash --- Data Cleaning & Preprocessing
Reads raw CSVs --- validates, cleans, standardizes --- outputs cleaned CSVs.
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
CLEAN_DIR = Path(__file__).resolve().parents[1] / "data" / "cleaned"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

REPORT = []


def log(msg: str):
    print(f"  [OK] {msg}")
    REPORT.append(msg)


def load_csv(name: str) -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / name)
    log(f"Loaded {name} ({len(df)} rows, {len(df.columns)} cols)")
    return df


def save_clean(df: pd.DataFrame, name: str):
    path = CLEAN_DIR / name
    df.to_csv(path, index=False)
    log(f"Saved cleaned {name} ({len(df)} rows)")


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates(subset=["customer_id"])
    df = df.dropna(subset=["customer_id", "name", "city"])
    df["age"] = df["age"].clip(16, 90)
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    df["email"] = df["email"].str.lower().str.strip()
    df["phone"] = df["phone"].str.replace(r"[^\d+]", "", regex=True)
    df["gender"] = df["gender"].str.strip().str.title()
    df["gender"] = df["gender"].where(df["gender"].isin(["Male", "Female", "Other"]), "Other")
    df["city"] = df["city"].str.strip().str.title()
    df["is_active"] = df["is_active"].astype(bool)
    log(f"Customers: {before} --- {len(df)} after dedup/na removal")
    return df


def clean_restaurants(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["restaurant_id"])
    df = df.dropna(subset=["restaurant_id", "name"])
    df["cuisine_type"] = df["cuisine_type"].str.strip().str.title()
    df["city"] = df["city"].str.strip().str.title()
    df["rating"] = df["rating"].clip(1.0, 5.0)
    df["avg_cost_for_two"] = df["avg_cost_for_two"].clip(50, 5000)
    df["preparation_time_mins"] = df["preparation_time_mins"].clip(2, 60).astype(int)
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
    df["is_active"] = df["is_active"].astype(bool)
    log(f"Restaurants: {len(df)} cleaned")
    return df


def clean_drivers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["driver_id"])
    df = df.dropna(subset=["driver_id", "name"])
    df["age"] = df["age"].clip(18, 65)
    df["city"] = df["city"].str.strip().str.title()
    df["vehicle_type"] = df["vehicle_type"].str.strip().str.title()
    df["rating"] = df["rating"].clip(1.0, 5.0)
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
    df["is_active"] = df["is_active"].astype(bool)
    log(f"Drivers: {len(df)} cleaned")
    return df


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    df = df.dropna(subset=["order_id", "customer_id", "restaurant_id"])
    df["order_datetime"] = pd.to_datetime(df["order_datetime"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["order_hour"] = df["order_hour"].clip(0, 23).astype(int)

    for col in ["order_amount", "delivery_fee", "discount", "tax", "platform_fee", "total_amount"]:
        df[col] = df[col].clip(0, None)

    df["surge_multiplier"] = df["surge_multiplier"].clip(1.0, 3.0)
    df["order_status"] = df["order_status"].str.strip().str.title()
    valid_status = ["Delivered", "Cancelled", "Refunded"]
    df = df[df["order_status"].isin(valid_status)]
    df["customer_city"] = df["customer_city"].str.strip().str.title()
    df["restaurant_city"] = df["restaurant_city"].str.strip().str.title()
    df["payment_method"] = df["payment_method"].str.strip().str.title()

    log(f"Orders: {before} --- {len(df)} after dedup/validation")
    return df


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["order_item_id"])
    df = df.dropna(subset=["order_id", "item_name"])
    df["quantity"] = df["quantity"].clip(1, 20).astype(int)
    df["unit_price"] = df["unit_price"].clip(5, 2000)
    df["line_total"] = df["line_total"].clip(0, None)
    df["category"] = df["category"].str.strip().str.title()
    df["item_name"] = df["item_name"].str.strip().str.title()
    log(f"Order items: {len(df)} cleaned")
    return df


def clean_delivery_logs(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["delivery_id"])
    df = df.dropna(subset=["order_id", "driver_id"])
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    df["drop_datetime"] = pd.to_datetime(df["drop_datetime"], errors="coerce")
    df["distance_km"] = df["distance_km"].clip(0.1, 50.0)
    df["travel_time_mins"] = df["travel_time_mins"].clip(1, 120).astype(int)
    df["traffic_condition"] = df["traffic_condition"].str.strip().str.title()
    df["weather_condition"] = df["weather_condition"].str.strip().str.title()
    valid_traffic = ["Low", "Moderate", "High", "Gridlock"]
    valid_weather = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Foggy"]
    df = df[df["traffic_condition"].isin(valid_traffic)]
    df = df[df["weather_condition"].isin(valid_weather)]
    log(f"Delivery logs: {len(df)} cleaned")
    return df


def main():
    print("=" * 50)
    print("SwiftDash Data Cleaning Pipeline")
    print("=" * 50)

    customers = clean_customers(load_csv("customers.csv"))
    save_clean(customers, "customers_clean.csv")

    restaurants = clean_restaurants(load_csv("restaurants.csv"))
    save_clean(restaurants, "restaurants_clean.csv")

    drivers = clean_drivers(load_csv("drivers.csv"))
    save_clean(drivers, "drivers_clean.csv")

    orders = clean_orders(load_csv("orders.csv"))
    save_clean(orders, "orders_clean.csv")

    order_items = clean_order_items(load_csv("order_items.csv"))
    save_clean(order_items, "order_items_clean.csv")

    delivery_logs = clean_delivery_logs(load_csv("delivery_logs.csv"))
    save_clean(delivery_logs, "delivery_logs_clean.csv")

    print("\n" + "=" * 50)
    print("Data Cleaning Complete --- Summary")
    print("=" * 50)
    for r in REPORT:
        print(f"  {r}")


if __name__ == "__main__":
    main()
