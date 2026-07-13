# SwiftDash Operations Analytics — Presentation Deck

## Slide-by-Slide Outline (15-18 slides)

---

### Slide 1: Title Slide
**SwiftDash Operations Analytics**  
*Data-Driven Insights for Food Delivery Platform Performance*  
[Your Name] | [Date]

---

### Slide 2: Problem Statement
- SwiftDash is a growing food delivery platform across 15 Indian cities
- Rich transaction data exists but no systematic analytics pipeline
- Management needs: Revenue insights, customer understanding, operational efficiency, growth opportunities
- **Goal:** Convert raw data into actionable business intelligence

---

### Slide 3: Project Scope
| Metric | Value |
|--------|-------|
| Timeline | Jan 2022 – Jun 2025 |
| Customers | 12,000 |
| Restaurants | 250 |
| Drivers | 800 |
| Orders | 65,000+ |
| Cities | 15 |
| Deliveries | 59,767 |

---

### Slide 4: Tech Stack & Architecture
Visual: Pipeline flowchart
- Python (Pandas, NumPy) → Data Cleaning & EDA
- MySQL → Schema & 50 Analytical Queries
- Power BI → Interactive Dashboard (5 pages)
- Git → Version Control

---

### Slide 5: Data Pipeline
1. **Generate** realistic synthetic data (Faker + NumPy)
2. **Clean & Validate** — 6 tables, dedup, outlier capping, standardization
3. **Feature Engineering** — RFM segmentation, driver scores, time series
4. **Load to MySQL** — Star schema with foreign keys and indexes
5. **Query** — 50 business SQL queries across 5 categories
6. **Visualize** — Power BI interactive dashboards
7. **Recommend** — Data-driven business recommendations

---

### Slide 6: Data Quality & Cleaning
- 6 relational tables, 272K+ total records
- Outlier capping (age, prices, delivery times)
- Categorical validation (payment methods, order statuses, traffic conditions)
- Duplicate removal, missing value handling
- Type standardization (dates, strings, booleans)
- **Result:** Analysis-ready clean dataset

---

### Slide 7: Revenue Analysis
Visual: Monthly Revenue Trend chart
- **Total Revenue:** INR X (delivered orders)
- **Monthly Growth:** Avg X% MoM
- **Peak Hours:** 7-9 PM (30%+ of daily orders)
- **Top Payment:** UPI (45% share)
- **Revenue Lost to Cancellations:** INR X
- **Discount Impact:** Deep discounts show diminishing returns

Key Insight: Weekend peak hours generate 2x surge premium but 1.5x cancellation rate — balancing act.

---

### Slide 8: Customer Segmentation (RFM)
Visual: Segmentation Pie + Revenue by Segment
| Segment | % Customers | Revenue Share |
|---------|------------|---------------|
| Platinum | 3% | 15% |
| Gold | 12% | 28% |
| Silver | 35% | 32% |
| At Risk | 15% | 12% |
| Churned | 25% | 8% |
| New | 10% | 5% |

**Key Insight:** Top 15% customers (Platinum + Gold) drive 43% of revenue. At Risk + Churned = 40% of customers representing 20% of potential revenue.

---

### Slide 9: Customer Retention
- **First-month retention:** ~35-40% (M0 → M1)
- **Repeat customer rate:** 45-50%
- **Avg orders per customer:** 5.4
- **Avg customer lifetime value:** INR X
- Top 10% customers contribute ~35-40% of total revenue

**Insight:** Reactivating At Risk customers costs 5x less than acquiring new ones.

---

### Slide 10: Operational Analysis
Visual: Delivery Time Distribution + On-Time Rate by Traffic
- **Avg delivery time:** 28 minutes
- **On-time delivery rate:** 82%
- **Motorcycles** outperform cars in high traffic (88% vs 72% on-time)
- **Heavy Rain:** +30% delivery time, 2x cancellation rate
- **Gridlock traffic:** On-time rate drops to 55%

**Insight:** Dynamic dispatch (more scooters during peak + rain) can improve on-time rate by 8-10%.

---

### Slide 11: Restaurant & Cuisine Analysis
Visual: Top Cuisines chart
- **Top 3 cuisines:** North Indian, South Indian, Chinese (60%+ revenue)
- **Top 20% restaurants** contribute 65% of revenue (Pareto)
- **Korean/Japanese** have highest AOV but low volume — niche premium segment
- Prep time >30 mins = 2x cancellation rate

---

### Slide 12: Power BI Dashboard
Visual: Dashboard screenshots (thumbnails)
- **5 pages:** Executive Summary, Customer Analytics, Operations, Restaurant, Trends
- **15+ DAX measures** (MoM growth, YoY comparison, dynamic segmentation)
- **Drill-through** from executive summary to individual driver detail
- **Interactive slicers:** City, Year, Quarter, Cuisine Type
- **Mobile-optimized layout** for on-the-go monitoring

---

### Slide 13: SQL Capabilities Demonstrated
- **Window Functions:** LAG for MoM growth, NTILE for decile analysis, ROW_NUMBER for ranking
- **CTEs:** RFM segmentation, cohort retention, revenue decomposition
- **Complex Joins:** Multi-table (orders + customers + restaurants + delivery)
- **Aggregations:** GROUP BY ROLL-UP patterns, conditional SUM
- **Performance:** 15+ indexes, sub-second query execution on 65K+ records

---

### Slide 14: Business Recommendations
| Priority | Initiative | Impact |
|----------|-----------|--------|
| **P0** | Tiered Loyalty Program | +15% retention, +10% revenue |
| **P0** | Dynamic Delivery Dispatch | +8% on-time rate, -5% cancellations |
| **P1** | Discount Strategy Optimization | +5% margin |
| **P1** | Tier-2 City Expansion | +20% user growth |
| **P1** | Customer Reactivation Campaign | Recover 15% churned |
| **P2** | Cuisine Portfolio Expansion | +8% order frequency |
| **P2** | Weather Contingency Planning | -10% rain-day cancellations |

---

### Slide 15: Implementation Roadmap
Quarterly breakdown:
- **Q1:** Loyalty program, delivery optimization (quick wins)
- **Q2:** Discount refinement, Tier-2 expansion, reactivation campaigns
- **Q3:** Cuisine optimization, surge pricing refinement, weather planning
- **Q4:** Review, iterate, ML readiness assessment

Expected 12-month impact: +20% revenue, +15% retention, +10% operational efficiency

---

### Slide 16: Skills Demonstrated
| Category | Skills |
|----------|--------|
| **Data Engineering** | Pipelines, ETL, MySQL schema, indexing, Python automation |
| **Data Analysis** | EDA, RFM, cohort analysis, statistical analysis, correlations |
| **SQL** | Advanced queries, window functions, CTEs, query optimization |
| **Visualization** | Power BI, DAX, data modeling, dashboard design |
| **Business** | Revenue management, customer strategy, operations optimization |
| **Communication** | Technical documentation, executive presentations, recommendations |

---

### Slide 17: Thank You
- [Your Name]
- [Email/LinkedIn]
- [GitHub Repository URL]
- [Power BI Dashboard Link]

---

## Speaker Notes Template

**Slide 7 (Revenue):** "Notice the consistent upward trend with seasonal peaks during Q4 — this aligns with festive season ordering. The dip in early 2023 was addressed by our surge pricing optimization. Currently, our biggest revenue leakage is through cancellations during peak hours."

**Slide 8 (Segmentation):** "This slide reveals a critical insight. While Platinum and Gold customers are only 15% of our base, they contribute 43% of revenue. Meanwhile, 40% of our customers are at risk of churning or have already churned. Each percentage point recovered from At Risk translates to INR X in revenue."

**Slide 14 (Recommendations):** "We've prioritized initiatives using impact vs. effort. The loyalty program and delivery dispatch changes are P0 because they address our biggest pain points — retention and operations — with measurable ROI within one quarter."

---

## Design Tips

- Use consistent color palette: Blue (#3498DB), Green (#2ECC71), Orange (#F39C12)
- One key message per slide (max 3 bullet points)
- Visuals > Text — use charts, not tables of numbers
- Include data source references on each slide
- Practice 1 minute per slide pace (15-18 min total)
- Prepare 2-3 backup slides with detailed methodology for Q&A
