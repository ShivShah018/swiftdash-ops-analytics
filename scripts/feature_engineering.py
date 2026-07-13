"""
SwiftDash --- Feature Engineering
Creates derived features and aggregated tables for analytics and dashboards.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

CLEAN_DIR = Path(__file__).resolve().parents[1] / "data" / "cleaned"
PROC_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(CLEAN_DIR / name)


def save(df: pd.DataFrame, name: str):
    path = PROC_DIR / name
    df.to_csv(path, index=False)
    print(f"  Saved {name} ({len(df)} rows)")


def build_customer_features(orders, customers):
    """Customer-level features: RFM, segmentation, lifetime value."""
    delivered = orders[orders["order_status"].isin(["Delivered", "Refunded"])].copy()
    delivered["order_date"] = pd.to_datetime(delivered["order_date"])

    rfm = delivered.groupby("customer_id").agg(
        recency_days=("order_date", lambda x: (delivered["order_date"].max() - x.max()).days),
        frequency=("order_id", "count"),
        monetary=("total_amount", "sum"),
        avg_order_value=("total_amount", "mean"),
        avg_discount_used=("discount", "mean"),
        preferred_payment=("payment_method", lambda x: x.mode().iloc[0] if not x.mode().empty else "UPI"),
        preferred_cuisine=("restaurant_id", "nunique"),
        first_order_date=("order_date", "min"),
        last_order_date=("order_date", "max"),
    ).reset_index()

    rfm["days_since_first_order"] = (delivered["order_date"].max() - rfm["first_order_date"]).dt.days

    rfm["customer_segment"] = "Silver"
    rfm.loc[(rfm["frequency"] >= 10) & (rfm["monetary"] >= 5000), "customer_segment"] = "Gold"
    rfm.loc[(rfm["frequency"] >= 25) & (rfm["monetary"] >= 15000), "customer_segment"] = "Platinum"
    rfm.loc[rfm["recency_days"] > 180, "customer_segment"] = "Churned"
    rfm.loc[(rfm["recency_days"] > 90) & (rfm["recency_days"] <= 180), "customer_segment"] = "At Risk"

    rfm["customer_tenure_months"] = rfm["days_since_first_order"].clip(0) // 30
    rfm["avg_order_frequency_days"] = np.where(
        rfm["frequency"] > 1,
        rfm["days_since_first_order"] / rfm["frequency"],
        0
    )

    customers_enhanced = customers.merge(rfm, on="customer_id", how="left")
    for col in ["recency_days", "frequency", "monetary", "avg_order_value",
                "avg_discount_used", "days_since_first_order", "customer_tenure_months",
                "avg_order_frequency_days"]:
        customers_enhanced[col] = customers_enhanced[col].fillna(0).astype(int) if col in [
            "recency_days", "frequency", "days_since_first_order", "customer_tenure_months",
            "avg_order_frequency_days"] else customers_enhanced[col].fillna(0)

    customers_enhanced["customer_segment"] = customers_enhanced["customer_segment"].fillna("New")
    customers_enhanced["preferred_payment"] = customers_enhanced["preferred_payment"].fillna("UPI")
    customers_enhanced["preferred_cuisine"] = customers_enhanced["preferred_cuisine"].fillna(0).astype(int)
    customers_enhanced["first_order_date"] = customers_enhanced["first_order_date"].fillna(customers_enhanced["signup_date"])
    customers_enhanced["last_order_date"] = customers_enhanced["last_order_date"].fillna(customers_enhanced["signup_date"])

    return customers_enhanced


def build_restaurant_features(orders, order_items, restaurants):
    """Restaurant performance metrics."""
    delivered = orders[orders["order_status"].isin(["Delivered", "Refunded"])].copy()

    perf = delivered.groupby("restaurant_id").agg(
        total_orders=("order_id", "count"),
        total_revenue=("total_amount", "sum"),
        avg_order_value=("total_amount", "mean"),
        total_discount_given=("discount", "sum"),
        unique_customers=("customer_id", "nunique"),
        cancellation_rate=("order_status", lambda x: (x == "Cancelled").mean()),
    ).reset_index()

    items_summary = order_items.groupby("order_id").agg(
        items_per_order=("quantity", "sum")
    ).reset_index()
    orders_with_items = delivered.merge(items_summary, on="order_id", how="left")
    items_per_rest = orders_with_items.groupby("restaurant_id")["items_per_order"].mean().reset_index()
    items_per_rest.columns = ["restaurant_id", "avg_items_per_order"]

    perf = perf.merge(items_per_rest, on="restaurant_id", how="left")

    rest_enhanced = restaurants.merge(perf, on="restaurant_id", how="left")
    for col in ["total_orders", "total_revenue", "avg_order_value", "total_discount_given",
                "unique_customers", "cancellation_rate", "avg_items_per_order"]:
        rest_enhanced[col] = rest_enhanced[col].fillna(0)

    rest_enhanced["revenue_per_customer"] = np.where(
        rest_enhanced["unique_customers"] > 0,
        rest_enhanced["total_revenue"] / rest_enhanced["unique_customers"],
        0
    )
    rest_enhanced["revenue_tier"] = pd.qcut(
        rest_enhanced["total_revenue"].clip(lower=1),
        q=4, labels=["Low", "Medium", "High", "Top"]
    )

    return rest_enhanced


def build_driver_features(delivery_logs, drivers):
    """Driver performance metrics."""
    perf = delivery_logs.groupby("driver_id").agg(
        total_deliveries=("delivery_id", "count"),
        avg_travel_time=("travel_time_mins", "mean"),
        avg_distance=("distance_km", "mean"),
        on_time_rate=("is_on_time", "mean"),
    ).reset_index()

    drv_enhanced = drivers.merge(perf, on="driver_id", how="left")
    for col in ["total_deliveries", "avg_travel_time", "avg_distance", "on_time_rate"]:
        drv_enhanced[col] = drv_enhanced[col].fillna(0)

    drv_enhanced["efficiency_score"] = (
        drv_enhanced["on_time_rate"] * 0.5 +
        (1 - drv_enhanced["avg_travel_time"] / drv_enhanced["avg_travel_time"].max()) * 0.3 +
        drv_enhanced["rating"] / 5 * 0.2
    ) * 100

    return drv_enhanced


def build_time_series(orders):
    """Daily/Monthly aggregated metrics."""
    delivered = orders[orders["order_status"].isin(["Delivered", "Refunded"])].copy()
    delivered["order_date"] = pd.to_datetime(delivered["order_date"])
    delivered["year_month"] = delivered["order_date"].dt.to_period("M").astype(str)

    daily = delivered.groupby("order_date").agg(
        orders_count=("order_id", "count"),
        revenue=("total_amount", "sum"),
        avg_order_value=("total_amount", "mean"),
        unique_customers=("customer_id", "nunique"),
        unique_restaurants=("restaurant_id", "nunique"),
    ).reset_index()

    monthly = delivered.groupby("year_month").agg(
        orders_count=("order_id", "count"),
        revenue=("total_amount", "sum"),
        avg_order_value=("total_amount", "mean"),
        unique_customers=("customer_id", "nunique"),
        unique_restaurants=("restaurant_id", "nunique"),
        total_discount=("discount", "sum"),
        total_delivery_fee=("delivery_fee", "sum"),
    ).reset_index().sort_values("year_month")

    return daily, monthly


def main():
    print("SwiftDash Feature Engineering")
    print("=" * 40)

    print("\n[1/4] Loading cleaned data...")
    orders = load("orders_clean.csv")
    customers = load("customers_clean.csv")
    restaurants = load("restaurants_clean.csv")
    drivers = load("drivers_clean.csv")
    order_items = load("order_items_clean.csv")
    delivery_logs = load("delivery_logs_clean.csv")

    print("\n[2/4] Building customer features (RFM + segmentation)...")
    customer_features = build_customer_features(orders, customers)
    save(customer_features, "customer_features.csv")

    print("\n[3/4] Building restaurant & driver features...")
    restaurant_features = build_restaurant_features(orders, order_items, restaurants)
    save(restaurant_features, "restaurant_features.csv")

    driver_features = build_driver_features(delivery_logs, drivers)
    save(driver_features, "driver_features.csv")

    print("\n[4/4] Building time-series aggregations...")
    daily, monthly = build_time_series(orders)
    save(daily, "daily_metrics.csv")
    save(monthly, "monthly_metrics.csv")

    print("\n" + "=" * 40)
    print("Feature engineering complete!")
    print("=" * 40)


if __name__ == "__main__":
    main()
