"""
SwiftDash Operations Analytics --- Data Generation Script
Generates realistic synthetic data for a food delivery platform.
Outputs: customers, restaurants, drivers, orders, order_items, delivery_logs
"""

import os
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
np.random.seed(SEED)
random.seed(SEED)
fake = Faker()
Faker.seed(SEED)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

N_CUSTOMERS = 12_000
N_RESTAURANTS = 250
N_DRIVERS = 800
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 6, 30)
TOTAL_ORDERS = 65_000

INDIAN_CITIES = [
    ("Mumbai", 19.0760, 72.8777), ("Delhi", 28.7041, 77.1025),
    ("Bangalore", 12.9716, 77.5946), ("Hyderabad", 17.3850, 78.4867),
    ("Chennai", 13.0827, 80.2707), ("Kolkata", 22.5726, 88.3639),
    ("Pune", 18.5204, 73.8567), ("Ahmedabad", 23.0225, 72.5714),
    ("Jaipur", 26.9124, 75.7873), ("Lucknow", 26.8467, 80.9462),
    ("Surat", 21.1702, 72.8311), ("Chandigarh", 30.7333, 76.7794),
    ("Bhopal", 23.2599, 77.4126), ("Indore", 22.7196, 75.8577),
    ("Coimbatore", 11.0168, 76.9558),
]

CUISINE_TYPES = [
    "North Indian", "South Indian", "Chinese", "Italian", "Fast Food",
    "Bakery", "Desserts", "Beverages", "Continental", "Mughlai",
    "Street Food", "Healthy", "Seafood", "Korean", "Japanese",
]

ITEM_CATEGORIES = {
    "North Indian": ["Butter Chicken", "Dal Makhani", "Naan", "Biryani", "Paneer Tikka"],
    "South Indian": ["Dosa", "Idli", "Vada", "Sambhar Rice", "Rasam"],
    "Chinese": ["Noodles", "Fried Rice", "Manchurian", "Spring Roll", "Schezwan Rice"],
    "Italian": ["Pasta", "Pizza", "Risotto", "Lasagna", "Garlic Bread"],
    "Fast Food": ["Burger", "French Fries", "Sandwich", "Wrap", "Momos"],
    "Bakery": ["Croissant", "Cake Slice", "Muffin", "Cookie", "Brownie"],
    "Desserts": ["Gulab Jamun", "Ice Cream", "Kulfi", "Rasgulla", "Falooda"],
    "Beverages": ["Tea", "Coffee", "Lassi", "Fresh Juice", "Smoothie"],
    "Continental": ["Grilled Chicken", "Steak", "Salad", "Soup", "Pasta Alfredo"],
    "Mughlai": ["Chicken Tikka", "Sheekh Kebab", "Biryani", "Korma", "Nihari"],
    "Street Food": ["Pani Puri", "Vada Pav", "Pav Bhaji", "Samosa", "Bhel Puri"],
    "Healthy": ["Salad Bowl", "Smoothie Bowl", "Grilled Fish", "Quinoa Bowl", "Oatmeal"],
    "Seafood": ["Fish Curry", "Prawn Fry", "Crab Masala", "Tandoori Fish"],
    "Korean": ["Kimchi", "Bibimbap", "Bulgogi", "Korean Fried Chicken", "Tteokbokki"],
    "Japanese": ["Sushi", "Ramen", "Tempura", "Teriyaki", "Miso Soup"],
}

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet", "COD"]
TRAFFIC_CONDITIONS = ["Low", "Moderate", "High", "Gridlock"]
WEATHER_CONDITIONS = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Foggy"]


def _city_choice():
    return random.choice(INDIAN_CITIES)


def generate_customers(n):
    records = []
    for i in range(1, n + 1):
        city_name, lat, lng = _city_choice()
        age_bucket = random.choices([0, 1, 2, 3], weights=[0.35, 0.35, 0.20, 0.10])[0]
        age = {0: random.randint(18, 27), 1: random.randint(27, 40),
               2: random.randint(40, 55), 3: random.randint(55, 75)}[age_bucket]
        signup = fake.date_between(start_date=datetime(2020, 1, 1), end_date=END_DATE)
        records.append((
            f"CUST_{i:05d}", fake.name(), age,
            random.choices(["Male", "Female", "Other"], weights=[0.48, 0.48, 0.04])[0],
            city_name, round(lat + random.uniform(-0.05, 0.05), 6),
            round(lng + random.uniform(-0.05, 0.05), 6),
            fake.phone_number(), fake.email(), signup,
            random.choices([True, False], weights=[0.85, 0.15])[0],
        ))
    return pd.DataFrame(records, columns=[
        "customer_id", "name", "age", "gender", "city", "latitude", "longitude",
        "phone", "email", "signup_date", "is_active"
    ])


def generate_restaurants(n):
    records = []
    for i in range(1, n + 1):
        city_name, lat, lng = _city_choice()
        cuisine = random.choice(CUISINE_TYPES)
        prep = int(np.random.gamma(shape=3, scale=5)) + 5
        records.append((
            f"REST_{i:03d}",
            fake.company() + " " + random.choice(["Kitchen", "Foods", "Eatery", "Bites", "Cafe"]),
            cuisine, city_name, round(lat + random.uniform(-0.02, 0.02), 6),
            round(lng + random.uniform(-0.02, 0.02), 6),
            round(random.choices(
                [random.uniform(1.0, 2.5), random.uniform(2.5, 3.5),
                 random.uniform(3.5, 4.2), random.uniform(4.2, 5.0)],
                weights=[0.05, 0.15, 0.40, 0.40]
            )[0], 1),
            random.randint(150, 1200),
            fake.date_between(start_date=datetime(2019, 1, 1), end_date=datetime(2024, 12, 31)),
            random.choices([True, False], weights=[0.90, 0.10])[0],
            prep,
        ))
    return pd.DataFrame(records, columns=[
        "restaurant_id", "name", "cuisine_type", "city", "latitude", "longitude",
        "rating", "avg_cost_for_two", "join_date", "is_active", "preparation_time_mins"
    ])


def generate_drivers(n):
    records = []
    for i in range(1, n + 1):
        city_name, lat, lng = _city_choice()
        records.append((
            f"DRV_{i:04d}", fake.name(), random.randint(20, 50),
            city_name, round(lat + random.uniform(-0.05, 0.05), 6),
            round(lng + random.uniform(-0.05, 0.05), 6),
            random.choices(["Bicycle", "Motorcycle", "Scooter", "Car"],
                           weights=[0.15, 0.50, 0.25, 0.10])[0],
            round(random.uniform(3.0, 5.0), 1),
            fake.date_between(start_date=datetime(2020, 6, 1), end_date=datetime(2024, 12, 31)),
            random.choices([True, False], weights=[0.80, 0.20])[0],
        ))
    return pd.DataFrame(records, columns=[
        "driver_id", "name", "age", "city", "latitude", "longitude",
        "vehicle_type", "rating", "join_date", "is_active"
    ])


def generate_orders(customers, restaurants, drivers, n):
    active_custs = customers[customers["is_active"]].to_dict("records")
    active_rests = restaurants[restaurants["is_active"]].to_dict("records")
    active_drvs = drivers[drivers["is_active"]].to_dict("records")

    days_range = (END_DATE - START_DATE).days
    hour_weights = [2, 1, 1, 1, 1, 2, 4, 6, 8, 6, 5, 7,
                    8, 6, 5, 4, 5, 7, 10, 12, 10, 8, 5, 3]

    records = []
    for i in range(1, n + 1):
        cust = random.choice(active_custs)
        rest = random.choice(active_rests)
        drv = random.choice(active_drvs)

        order_date = START_DATE + timedelta(days=random.randint(0, days_range))
        hour = random.choices(range(24), weights=hour_weights)[0]
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        dt = order_date.replace(hour=hour, minute=minute, second=second)

        order_amt = round(random.uniform(80, 800), 2)
        del_fee = round(random.choices([0, random.uniform(10, 60)], weights=[0.15, 0.85])[0], 2)
        disc = round(random.choices([0, random.uniform(5, order_amt * 0.3)], weights=[0.6, 0.4])[0], 2)
        surge = 1.0
        if 18 <= hour <= 21 and dt.weekday() >= 5:
            surge = round(random.uniform(1.1, 1.5), 2)

        taxable = order_amt + del_fee
        tax = round(taxable * 0.05, 2)
        plat_fee = round(random.uniform(3, 10), 2)
        total = round((order_amt + del_fee + tax + plat_fee - disc) * surge, 2)

        status = random.choices(
            ["Delivered", "Cancelled", "Delivered", "Delivered", "Refunded"],
            weights=[0.78, 0.08, 0.10, 0.02, 0.02]
        )[0]

        rating = None
        if status == "Delivered":
            rating = random.choices([random.randint(1, 3), random.randint(4, 5)], weights=[0.15, 0.85])[0]

        records.append((
            f"ORD_{i:05d}", cust["customer_id"], rest["restaurant_id"],
            drv["driver_id"] if status != "Cancelled" else None,
            dt, dt.date(), hour, WEEKDAYS[dt.weekday()], dt.weekday() >= 5,
            order_amt, del_fee, disc, tax, plat_fee, surge, total,
            random.choices(PAYMENT_METHODS, weights=[0.45, 0.20, 0.10, 0.05, 0.10, 0.10])[0],
            status, cust["city"], rest["city"], rating,
        ))

    return pd.DataFrame(records, columns=[
        "order_id", "customer_id", "restaurant_id", "driver_id",
        "order_datetime", "order_date", "order_hour", "weekday", "is_weekend",
        "order_amount", "delivery_fee", "discount", "tax", "platform_fee",
        "surge_multiplier", "total_amount", "payment_method", "order_status",
        "customer_city", "restaurant_city", "customer_rating",
    ])


def generate_order_items(orders, restaurants):
    rest_cuisine = restaurants.set_index("restaurant_id")["cuisine_type"].to_dict()
    delivered = orders[orders["order_status"] != "Cancelled"]
    records = []
    oid = 1
    for _, row in delivered.iterrows():
        cuisine = rest_cuisine.get(row["restaurant_id"], "Fast Food")
        menu = ITEM_CATEGORIES.get(cuisine, ITEM_CATEGORIES["Fast Food"])
        n = random.choices([1, 2, 3, 4, 5], weights=[0.30, 0.35, 0.20, 0.10, 0.05])[0]
        selected = random.sample(menu, min(n, len(menu)))
        remaining = row["order_amount"]
        for j, item_name in enumerate(selected):
            qty = random.choices([1, 2, 3], weights=[0.65, 0.25, 0.10])[0]
            if j == len(selected) - 1 and remaining > 0:
                unit_price = round(remaining / qty, 2)
            else:
                unit_price = round(random.uniform(50, 350), 2)
            line_total = round(qty * unit_price, 2)
            remaining -= line_total
            records.append((oid, row["order_id"], item_name, cuisine, qty, unit_price, line_total))
            oid += 1
    return pd.DataFrame(records, columns=[
        "order_item_id", "order_id", "item_name", "category", "quantity", "unit_price", "line_total"
    ])


def generate_delivery_logs(orders):
    delivered = orders[orders["order_status"].isin(["Delivered", "Refunded"])]
    records = []
    for _, row in delivered.iterrows():
        pickup_delay = random.randint(0, 20)
        pickup = row["order_datetime"] + timedelta(minutes=pickup_delay)
        travel = int(np.random.gamma(shape=4, scale=5)) + 5
        drop = pickup + timedelta(minutes=travel)
        records.append((
            f"DEL_{row['order_id']}", row["order_id"], row["driver_id"],
            pickup, drop, round(random.uniform(0.5, 15.0), 2), travel,
            random.choices(TRAFFIC_CONDITIONS, weights=[0.30, 0.35, 0.25, 0.10])[0],
            random.choices(WEATHER_CONDITIONS, weights=[0.50, 0.25, 0.15, 0.07, 0.03])[0],
            travel <= 40,
        ))
    return pd.DataFrame(records, columns=[
        "delivery_id", "order_id", "driver_id", "pickup_datetime", "drop_datetime",
        "distance_km", "travel_time_mins", "traffic_condition", "weather_condition", "is_on_time"
    ])


def main():
    print("[1/5] Generating customers...")
    customers = generate_customers(N_CUSTOMERS)
    customers.to_csv(RAW_DIR / "customers.csv", index=False)
    print(f"  -> {len(customers)} customers")

    print("[2/5] Generating restaurants...")
    restaurants = generate_restaurants(N_RESTAURANTS)
    restaurants.to_csv(RAW_DIR / "restaurants.csv", index=False)
    print(f"  -> {len(restaurants)} restaurants")

    print("[3/5] Generating drivers...")
    drivers = generate_drivers(N_DRIVERS)
    drivers.to_csv(RAW_DIR / "drivers.csv", index=False)
    print(f"  -> {len(drivers)} drivers")

    print("[4/5] Generating orders...")
    orders = generate_orders(customers, restaurants, drivers, TOTAL_ORDERS)
    orders.to_csv(RAW_DIR / "orders.csv", index=False)
    print(f"  -> {len(orders)} orders")

    print("[5/5] Generating order items & delivery logs...")
    oi = generate_order_items(orders, restaurants)
    oi.to_csv(RAW_DIR / "order_items.csv", index=False)
    print(f"  -> {len(oi)} order items")

    dl = generate_delivery_logs(orders)
    dl.to_csv(RAW_DIR / "delivery_logs.csv", index=False)
    print(f"  -> {len(dl)} delivery logs")

    print("\nAll data generated in", RAW_DIR)
    for f in ["customers.csv", "restaurants.csv", "drivers.csv", "orders.csv",
              "order_items.csv", "delivery_logs.csv"]:
        fp = RAW_DIR / f
        print(f"  {f}: {round(fp.stat().st_size / 1024, 1)} KB")


if __name__ == "__main__":
    main()
