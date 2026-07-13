# Data Dictionary — SwiftDash Food Delivery Analytics

## Entity-Relationship Overview

Six tables form the database: `customers`, `restaurants`, `drivers`, `orders`, `order_items`, and `delivery_logs`. The `orders` table is the central fact table linking customers, restaurants, and drivers.

---

## Table: customers

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| customer_id | VARCHAR(20) | Unique identifier for each customer | PRIMARY KEY |
| name | VARCHAR(100) | Customer's full name | NOT NULL |
| age | INT | Customer's age in years | 16-90 |
| gender | ENUM | 'Male', 'Female', or 'Other' | Default: 'Other' |
| city | VARCHAR(50) | City of residence | NOT NULL |
| latitude | DECIMAL(9,6) | Approximate geo-location latitude | Nullable |
| longitude | DECIMAL(9,6) | Approximate geo-location longitude | Nullable |
| phone | VARCHAR(20) | Contact phone number | Nullable |
| email | VARCHAR(100) | Email address | Nullable |
| signup_date | DATE | Date when customer joined the platform | Nullable |
| is_active | BOOLEAN | Whether the customer is currently active | Default: TRUE |

**Sample Row:**
```
CUST_00001 | Aarav Sharma | 28 | Male | Mumbai | 19.0760 | 72.8777 | +91-... | aarav@email.com | 2021-06-15 | TRUE
```

---

## Table: restaurants

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| restaurant_id | VARCHAR(20) | Unique identifier for each restaurant | PRIMARY KEY |
| name | VARCHAR(150) | Restaurant business name | NOT NULL |
| cuisine_type | VARCHAR(50) | Primary cuisine category | NOT NULL |
| city | VARCHAR(50) | City where restaurant is located | NOT NULL |
| latitude | DECIMAL(9,6) | Restaurant location latitude | Nullable |
| longitude | DECIMAL(9,6) | Restaurant location longitude | Nullable |
| rating | DECIMAL(2,1) | Average restaurant rating (out of 5) | 1.0-5.0 |
| avg_cost_for_two | INT | Approximate cost for two people (INR) | >= 50 |
| join_date | DATE | Date restaurant onboarded to platform | Nullable |
| is_active | BOOLEAN | Whether restaurant is currently active | Default: TRUE |
| preparation_time_mins | INT | Average food preparation time in minutes | 2-60 |

**Cuisine Types:** North Indian, South Indian, Chinese, Italian, Fast Food, Bakery, Desserts, Beverages, Continental, Mughlai, Street Food, Healthy, Seafood, Korean, Japanese

---

## Table: drivers

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| driver_id | VARCHAR(20) | Unique identifier for each delivery driver | PRIMARY KEY |
| name | VARCHAR(100) | Driver's full name | NOT NULL |
| age | INT | Driver's age in years | 18-65 |
| city | VARCHAR(50) | City where driver operates | NOT NULL |
| latitude | DECIMAL(9,6) | Driver home location latitude | Nullable |
| longitude | DECIMAL(9,6) | Driver home location longitude | Nullable |
| vehicle_type | ENUM | 'Bicycle', 'Motorcycle', 'Scooter', 'Car' | Default: 'Motorcycle' |
| rating | DECIMAL(2,1) | Average driver rating | 1.0-5.0 |
| join_date | DATE | Date driver joined the platform | Nullable |
| is_active | BOOLEAN | Whether driver is currently active | Default: TRUE |

---

## Table: orders (Fact Table)

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| order_id | VARCHAR(20) | Unique order identifier | PRIMARY KEY |
| customer_id | VARCHAR(20) | Reference to the customer who placed the order | FK -> customers |
| restaurant_id | VARCHAR(20) | Reference to the restaurant | FK -> restaurants |
| driver_id | VARCHAR(20) | Reference to the delivery driver | FK -> drivers, Nullable |
| order_datetime | DATETIME | Exact timestamp when order was placed | NOT NULL |
| order_date | DATE | Date portion of order (for partitioning) | Nullable |
| order_hour | TINYINT | Hour of the day (0-23) | 0-23 |
| weekday | VARCHAR(10) | Day of week (Monday-Sunday) | Nullable |
| is_weekend | BOOLEAN | Flag for Saturday/Sunday | Default: FALSE |
| order_amount | DECIMAL(10,2) | Cost of food items before fees/discount | >= 0 |
| delivery_fee | DECIMAL(8,2) | Delivery charge | Default: 0 |
| discount | DECIMAL(8,2) | Discount applied to order | Default: 0 |
| tax | DECIMAL(8,2) | Tax amount | Default: 0 |
| platform_fee | DECIMAL(6,2) | Platform service fee | Default: 0 |
| surge_multiplier | DECIMAL(3,2) | Peak pricing multiplier | Default: 1.00 |
| total_amount | DECIMAL(10,2) | Final amount paid by customer | >= 0 |
| payment_method | ENUM | 'UPI', 'Credit Card', 'Debit Card', 'Net Banking', 'Wallet', 'COD' | Nullable |
| order_status | ENUM | 'Delivered', 'Cancelled', 'Refunded' | Default: 'Delivered' |
| customer_city | VARCHAR(50) | Denormalized customer city | Nullable |
| restaurant_city | VARCHAR(50) | Denormalized restaurant city | Nullable |
| customer_rating | TINYINT | Rating given by customer (1-5) | 1-5 or NULL |

**Formula:** `total_amount = (order_amount + delivery_fee + tax + platform_fee - discount) * surge_multiplier`

---

## Table: order_items

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| order_item_id | INT | Auto-incrementing item identifier | PRIMARY KEY |
| order_id | VARCHAR(20) | Reference to parent order | FK -> orders |
| item_name | VARCHAR(100) | Name of the food item | NOT NULL |
| category | VARCHAR(50) | Cuisine category of the item | Nullable |
| quantity | INT | Number of units ordered | > 0 |
| unit_price | DECIMAL(10,2) | Price per unit | > 0 |
| line_total | DECIMAL(10,2) | Total for this line item | >= 0 |

---

## Table: delivery_logs

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| delivery_id | VARCHAR(30) | Unique delivery identifier | PRIMARY KEY |
| order_id | VARCHAR(20) | Reference to the delivered order | FK -> orders, UNIQUE |
| driver_id | VARCHAR(20) | Reference to the driver | FK -> drivers |
| pickup_datetime | DATETIME | Time when driver picked up the order | Nullable |
| drop_datetime | DATETIME | Time when driver dropped off the order | Nullable |
| distance_km | DECIMAL(8,2) | Distance traveled for delivery | > 0 |
| travel_time_mins | INT | Total delivery time in minutes | > 0 |
| traffic_condition | ENUM | 'Low', 'Moderate', 'High', 'Gridlock' | Nullable |
| weather_condition | ENUM | 'Clear', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Foggy' | Nullable |
| is_on_time | BOOLEAN | Whether delivery was completed within 40 mins | Default: TRUE |

---

## Calculated / Derived Fields (Feature Engineering)

These are not stored in the database but computed during analysis:

| Field | Source Table | Description |
|-------|-------------|-------------|
| recency_days | orders | Days since customer's last order |
| frequency | orders | Total number of orders placed by customer |
| monetary | orders | Total amount spent by customer |
| avg_order_value | orders | Average amount per order |
| customer_segment | orders | Platinum/Gold/Silver/At Risk/Churned/New |
| customer_tenure_months | orders + customers | Months since first order |
| on_time_rate | delivery_logs | % of deliveries completed within 40 mins |
| efficiency_score | delivery_logs + drivers | Weighted composite score |
| revenue_per_customer | orders | Total revenue / unique customers |
| revenue_tier | orders | Low/Medium/High/Top (quartile-based) |
