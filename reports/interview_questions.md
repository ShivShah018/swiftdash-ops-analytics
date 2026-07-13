# SwiftDash Project — Interview Questions & Answers

## Common Questions Interviewers Ask From This Project

---

### Data Cleaning & Python

**Q1: What data quality issues did you find and how did you handle them?**
- Standardized string fields (city names, cuisine types) with inconsistent casing
- Clipped outlier ages (16-90) and monetary values to realistic ranges
- Validated categorical fields against defined enumerations
- Used `drop_duplicates` for ID deduplication and `clip()` for outlier capping

**Q2: How did you handle missing values in the dataset?**
- Dropped rows with missing critical identifiers (customer_id, order_id)
- Categorical nulls filled with mode/fallback values (e.g., payment_method -> 'UPI')
- Numerical nulls in derived fields filled with 0
- Optional ratings left as NULL rather than imputing (represents genuine missing data)

**Q3: Explain your feature engineering approach.**
- **RFM features:** Recency (days since last order), Frequency (order count), Monetary (total spend) for customer segmentation
- **Customer segments:** Platinum/Gold/Silver/At Risk/Churned using value thresholds
- **Driver efficiency score:** Weighted composite of on-time rate (50%), speed (30%), rating (20%)
- **Restaurant revenue tier:** Quartile-based classification
- **Time-series aggregations:** Daily/monthly rollups for trend analysis

**Q4: Why did you choose to create a separate feature engineering script rather than doing it all in the EDA notebook?**
Modular design keeps concerns separated — cleaning is a one-time pipeline step, EDA is exploratory, and feature engineering produces reusable artifacts (customer_features.csv) that both SQL and Power BI consume.

---

### SQL

**Q5: Write a query to find customers who have placed more than 5 orders but haven't ordered in the last 90 days.**
```sql
SELECT c.customer_id, c.name, COUNT(o.order_id) AS total_orders,
       MAX(o.order_date) AS last_order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Delivered'
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) > 5
   AND MAX(o.order_date) < DATE_SUB(CURDATE(), INTERVAL 90 DAY)
ORDER BY last_order_date;
```

**Q6: How would you calculate month-over-month revenue growth in SQL?**
Using window functions with LAG():
```sql
WITH monthly_rev AS (
    SELECT DATE_FORMAT(order_date, '%Y-%m') AS ym,
           SUM(total_amount) AS revenue
    FROM orders WHERE order_status = 'Delivered'
    GROUP BY ym
)
SELECT ym, revenue,
       LAG(revenue) OVER (ORDER BY ym) AS prev_revenue,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY ym))
           / LAG(revenue) OVER (ORDER BY ym) * 100, 2) AS mom_growth_pct
FROM monthly_rev ORDER BY ym;
```

**Q7: What indexing strategy did you use and why?**
Added indexes on `order_date` (range queries), `customer_id`/`restaurant_id` (frequent JOINs), `order_status` (filtering), and `payment_method` (segmentation). Composite indexes are not needed given the query patterns.

**Q8: How would you identify the top 20% of restaurants contributing to 80% of revenue (Pareto analysis)?**
Using NTILE(5) or calculating cumulative revenue share with window functions. The revenue concentration query in `sql/05_restaurant_analysis.sql` demonstrates this.

**Q9: Explain the cohort retention query and how it works.**
The cohort query identifies each customer's first order month (cohort), then tracks how many return in subsequent months (month_offset 0, 1, 2, 3...). Retention % = active in month N / cohort size.

---

### Power BI

**Q10: How did you design the data model for the dashboard?**
Star schema with `orders` as the fact table, connected to `customers`, `restaurants`, `drivers`, and `delivery_logs` dimension tables. A separate `Calendar` table drives time intelligence.

**Q11: What DAX measures did you create?**
- Core KPIs: Total Revenue, Total Orders, AOV, On-Time %, Cancellation Rate
- Time intelligence: Revenue MoM Growth, Revenue YoY Growth, Rolling 30-day Revenue
- Customer metrics: Repeat Customer Rate, Avg Customer LTV
- Operational: Avg Delivery Time, Peak Hour Orders

**Q12: How do slicers interact with your dashboard pages?**
Slicers on Year, Quarter, City, and Cuisine Type are synced across pages using the Sync Slicers pane. Drill-through filters allow navigating from city-level to driver-level detail.

---

### Business & Analytics

**Q13: What is the most interesting business insight you discovered?**
The "At Risk" segment (customers inactive for 90-180 days) represents ~15% of customers but 20%+ of potential revenue. Reactivating them costs 5x less than acquiring new customers. This is a high-ROI opportunity that the business was not addressing.

**Q14: How would you present these findings to a non-technical executive?**
Lead with the business impact: "We have INR X in potential revenue sitting idle from customers who used to order regularly but stopped. Here's a 3-step plan to win them back at 1/5th the cost of new acquisition."

**Q15: What metrics would you track to measure the success of a loyalty program?**
- Enrollment rate (% of eligible customers joining)
- Redemption rate (% of earned rewards used)
- Incremental order frequency (orders/month before vs after joining)
- Segment migration (Silver -> Gold -> Platinum)
- Program ROI (incremental revenue / program cost)

**Q16: How would you validate that surge pricing isn't hurting long-term retention?**
Conduct an A/B test: Randomly segment cities into control (no surge) and treatment (dynamic surge). Track 30/60/90-day retention, cancellation rates, and average order frequency for each group.

---

### System Design & Engineering

**Q17: How would you productionize this analytics pipeline?**
- Airflow for orchestration (data gen -> cleaning -> feature engineering -> DB load)
- MySQL for structured storage, dbt for transformations
- Power BI Premium for scheduled dashboard refresh
- Great Expectations for data quality assertions
- MLflow if adding prediction models

**Q18: How would you handle incremental data loads instead of full reloads?**
Use watermark columns (`last_updated`, `order_datetime`) to identify new/modified records. Implement upsert logic using INSERT ... ON DUPLICATE KEY UPDATE in MySQL. Maintain a changelog table for append-only events.

**Q19: What if the dataset grew to 10 million orders? How would you scale?**
- Partition MySQL tables by month (range partitioning on `order_date`)
- Use materialized views for pre-aggregated metrics
- Implement data archiving (orders older than 2 years to cold storage)
- Consider columnar storage (ClickHouse) for real-time analytics
- Power BI DirectQuery mode for live data access

---

### Behavioral / Project Walkthrough

**Q20: Walk me through this project as if I were a hiring manager.**
"I built an end-to-end food delivery analytics platform. Starting with raw transactional data, I built a Python pipeline to clean and validate it across 6 related tables. I then engineered customer RFM features to create behavioral segments. I loaded the data into MySQL and wrote 50 analytical SQL queries covering revenue, operations, customer retention, and restaurant performance. Finally, I built a multi-page Power BI dashboard with DAX measures, time intelligence, and interactive drill-downs. The output includes data-driven business recommendations with an implementation roadmap."

**Q21: What was your biggest challenge and how did you overcome it?**
"Generating realistic synthetic data that preserves the relationships between multiple tables (customers->orders->items->delivery). I solved this by carefully modeling real-world distributions — peak hours, traffic patterns, weekday trends — and using foreign key integrity across all generated records."

**Q22: How is this project different from typical tutorial projects?**
"Three key differences: (1) The analytical focus is on **operational efficiency and delivery logistics** rather than just customer behavior, (2) The dataset has **6 related tables** enabling complex multi-table SQL queries, and (3) The business recommendations are **quantified with expected ROI** and implementation timelines."

---

## Before the Interview

1. Be able to explain **why you chose each technology**
2. Have **specific numbers ready** (revenue, order counts, segment sizes)
3. Understand **limitations** of your analysis (synthetic data, no ML models)
4. Demonstrate **business thinking** — connect technical choices to business value
5. Show **trade-off awareness** — e.g., "I chose not to add predictive models because the brief was focused on descriptive analytics"
