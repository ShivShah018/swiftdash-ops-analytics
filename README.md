# SwiftDash Operations Analytics — Food Delivery Platform

An end-to-end data analytics project for a food delivery platform, covering data generation, cleaning, SQL analysis, and interactive dashboards. Designed to demonstrate industry-ready skills for Data Analyst and Data Engineer roles.

---

## Project Overview

**Domain:** Food Delivery / E-commerce Operations  
**Timeline:** Jan 2022 – Jun 2025 (3.5 years of transactional data)  
**Scale:** 65,000+ orders | 12,000 customers | 250 restaurants | 800 drivers | 15 cities

### Business Problem

SwiftDash, a growing food delivery platform, has rich transactional data but lacks actionable insights into:
- Revenue drivers and growth trends
- Customer segments and retention patterns
- Delivery operational efficiency
- Restaurant and cuisine performance
- City-level market dynamics

### Objective

Transform raw transactional data into an analytics platform that enables data-driven decision-making across revenue management, operations, customer retention, and market expansion.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.14 |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **Database** | MySQL 8.0 |
| **Analytics** | 50 SQL Queries (CTEs, Window Functions, Aggregations) |
| **Dashboard** | Power BI (DAX, Drill-through, Time Intelligence) |
| **Version Control** | Git, GitHub |

---

## Dataset

Realistic synthetic data generated using Python (Faker + NumPy) modeling real-world food delivery distributions:

| Table | Rows | Description |
|-------|------|-------------|
| `customers` | 12,000 | Demographics, signup date, city, activity status |
| `restaurants` | 250 | Cuisine type, rating, prep time, location |
| `drivers` | 800 | Vehicle type, rating, join date, location |
| `orders` | 65,000 | Order value breakdown, payment, status, ratings |
| `order_items` | 134,383 | Items per order, categories, pricing |
| `delivery_logs` | 59,767 | Travel time, distance, traffic, weather, on-time status |

Data generation scripts include realistic patterns: peak hour ordering, weekday/weekend variation, traffic impact on delivery times, and seasonal trends.

---

## Project Structure

```
swiftdash-ops-analytics/
├── data/
│   ├── raw/              # Generated raw data
│   ├── cleaned/          # Cleaned & validated data
│   └── processed/        # Feature-engineered tables
├── scripts/
│   ├── generate_data.py           # Synthetic data generation
│   ├── clean_data.py              # Data cleaning pipeline
│   ├── feature_engineering.py     # RFM, segments, aggregations
│   ├── generate_visualizations.py # EDA screenshots
│   └── load_to_mysql.py           # MySQL bulk loader
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb
├── sql/
│   ├── 01_schema.sql              # Database schema (6 tables)
│   ├── 02_revenue_analysis.sql    # 10 revenue queries
│   ├── 03_customer_analysis.sql   # 10 customer queries
│   ├── 04_operational_analysis.sql # 10 operations queries
│   ├── 05_restaurant_analysis.sql # 10 restaurant queries
│   └── 06_kpi_dashboard.sql       # 10 KPI & executive queries
├── dashboard/
│   └── swiftdash_dashboard.pbix   # Power BI file
├── reports/
│   ├── business_recommendations.md
│   ├── power_bi_dashboard_guide.md
│   ├── interview_questions.md
│   └── resume_bullets.md
├── screenshots/         # EDA visualizations
├── assets/              # Logos, icons
├── requirements.txt
└── README.md
```

---

## Pipeline

```
Generate Data  →  Clean & Validate  →  Feature Engineering
     ↓                    ↓                    ↓
 Raw CSVs          Cleaned CSVs          Processed Tables
     ↓                    ↓                    ↓
  └──────────────────────┴──────────────────────┘
                        ↓
              Load to MySQL (schema.sql)
                        ↓
              50 Business SQL Queries
                        ↓
              Power BI Dashboard
                        ↓
         Business Recommendations
```

---

## SQL Analysis (50 Queries)

### Revenue (10 queries)
- Monthly revenue with MoM growth rate (window functions)
- Revenue by payment method, city, hour, cuisine
- Revenue lost to cancellations
- Discount impact analysis
- Weekday vs weekend comparison

### Customer (10 queries)
- RFM segmentation (Platinum/Gold/Silver/At Risk/Churned)
- Customer lifetime value (top 20)
- Repeat customer rate by month
- Cohort retention analysis
- Age group and gender analysis

### Operations (10 queries)
- Delivery time by hour, traffic, weather
- Driver efficiency ranking
- Vehicle type performance
- Peak hour analysis
- Outlier detection (long deliveries)

### Restaurant (10 queries)
- Top restaurants by revenue and rating
- Most popular items
- Cross-selling analysis (items bought together)
- Revenue concentration (Pareto analysis)
- Cuisine popularity by city

### KPI Dashboard (10 queries)
- Executive summary scorecard
- Month-over-month KPI comparison
- Daily active users trend
- Payment method adoption trends
- Platform economics breakdown

---

## Power BI Dashboard

The interactive dashboard includes 5 pages:

| Page | Focus | Visuals |
|------|-------|---------|
| **Executive Summary** | High-level KPIs, revenue trends, city performance | KPI cards, line charts, bar charts, donut chart |
| **Customer Analytics** | Segments, demographics, retention | Treemap, stacked bars, matrix (cohort), scatter |
| **Operations & Delivery** | Delivery times, driver performance, on-time rates | Map, histograms, clustered bars, tables |
| **Restaurant & Menu** | Top restaurants, cuisines, popular items, cross-sell | Bar charts, treemap, scatter plot, table |
| **Trends & Forecasting** | Monthly trends, YoY growth, heatmap | Line chart with forecast, waterfall, heatmap |

### Key DAX Measures
- `Total Revenue`, `Total Orders`, `Avg Order Value`
- `On-Time Delivery %`, `Cancellation Rate`
- `Revenue MoM/YoY Growth`
- `Repeat Customer Rate`
- `Avg Customer LTV`
- `Dynamic Segmentation`

---

## Key Insights

### Revenue
- **Monthly revenue** shows consistent growth with seasonal peaks in Q4 (festive season)
- **UPI** dominates payment methods (45%+), followed by Credit Cards (20%)
- **Discount rate** averages 8-12% with deep discounts (>150 INR) showing lower ROI

### Customers
- **Top 10% of customers** contribute ~35-40% of total revenue
- **Gold + Platinum segments** (high-value, regular) represent only 15% of customers but 40%+ of revenue
- **Customer retention** drops significantly after first month (M0→M1 retention ~35-40%)
- **Age group 25-34** drives the highest order volume and revenue

### Operations
- **Average delivery time**: 25-35 minutes
- **Motorcycle riders** have best on-time rate across traffic conditions
- **Gridlock traffic** reduces on-time delivery rate below 60%
- **Heavy Rain** increases delivery time by 30%+ and cancellation rates by 2x

### Restaurants
- **North Indian, South Indian, Chinese** cuisines drive 60%+ of revenue
- **Restaurants with prep time >30 mins** have 2x higher cancellation rates
- **Bottom 20% restaurants** by rating show significantly higher order cancellation

---

## Business Recommendations

The full recommendations document is at `reports/business_recommendations.md`. Key highlights:

1. **Loyalty Program** — Tiered rewards for Platinum/Gold segments (P0, +15% retention)
2. **Delivery Optimization** — Dynamic dispatch based on traffic, more scooter riders at peak hours (P0, +8% on-time rate)
3. **Discount Strategy** — Shift from broad discounts to targeted loyalty rewards (P1, +5% margin)
4. **City Expansion** — Increase marketing in high-growth Tier-2 cities (Pune, Jaipur) (P1, +20% user growth)
5. **Reactivation Campaign** — Target At Risk customers with personalized offers (P1, recover 15% churned)
6. **Prepayment Incentives** — Discount for Net Banking/Wallet to diversify payment mix (P2)

---

## Screenshots

| KPI Dashboard | Monthly Revenue Trend | Customer Segmentation |
|:---:|:---:|:---:|
| ![KPI Summary](screenshots/kpi_summary.png) | ![Monthly Revenue](screenshots/monthly_revenue_trend.png) | ![Segmentation](screenshots/customer_segmentation.png) |

| Top Cuisines | Delivery Performance | Time Patterns |
|:---:|:---:|:---:|
| ![Cuisines](screenshots/top_cuisines.png) | ![Delivery](screenshots/delivery_performance.png) | ![Patterns](screenshots/time_patterns.png) |

| City Revenue |
|:---:|
| ![Cities](screenshots/city_revenue.png) |

---

## How to Run

### Prerequisites
- Python 3.10+
- MySQL 8.0+ (optional, for SQL analysis)
- Power BI Desktop (for dashboard)

### Setup
```bash
# Clone repository
git clone https://github.com/yourusername/swiftdash-ops-analytics.git
cd swiftdash-ops-analytics

# Install dependencies
pip install -r requirements.txt

# Step 1: Generate data
python scripts/generate_data.py

# Step 2: Clean data
python scripts/clean_data.py

# Step 3: Feature engineering
python scripts/feature_engineering.py

# Step 4 (optional): Load to MySQL
# First run sql/01_schema.sql in MySQL
python scripts/load_to_mysql.py

# Step 5: Generate EDA screenshots
python scripts/generate_visualizations.py

# Step 6: Open Power BI dashboard
# Open dashboard/swiftdash_dashboard.pbix and connect to cleaned CSVs
```

---

## Skills Demonstrated

- **Data Engineering**: Pipeline architecture, data cleaning, feature engineering, MySQL schema design, indexing
- **Data Analysis**: EDA, statistical analysis, correlation analysis, trend decomposition
- **SQL**: Window functions, CTEs, cohort analysis, aggregations, joins, subqueries
- **Dashboard Development**: Power BI, DAX measures, time intelligence, drill-through, data modeling
- **Business Acumen**: Revenue analysis, customer segmentation, operational efficiency, recommendation formulation
- **Communication**: Technical documentation, executive summaries, presentation-ready outputs

---

## License

MIT
