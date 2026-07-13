"""
Generate EDA + Power BI-style dashboard screenshots.
"""

import sys
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import CLEAN_DIR, PROC_DIR, SCREENSHOTS, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("viz")

sns.set_style("whitegrid")
plt.rcParams.update({"figure.figsize": (12, 6), "font.size": 12})

# ── Power BI colour palette ────────────────────────────────────────────────
PBI_BG = "#1e1e1e"
PBI_CARD = "#252526"
PBI_ACCENT = "#0078d4"
PBI_GREEN = "#2ecc71"
PBI_RED = "#e74c3c"
PBI_ORANGE = "#f39c12"
PBI_BLUE = "#3498db"
PBI_PURPLE = "#9b59b6"
PBI_TEAL = "#1abc9c"
CHART_COLORS = [PBI_ACCENT, PBI_GREEN, PBI_ORANGE, PBI_RED, PBI_PURPLE, PBI_TEAL, "#e67e22", "#1f77b4"]


def _load(name):
    path = CLEAN_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path)


def _dark_fig(nrows=1, ncols=1, figsize=(16, 9)):
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    fig.patch.set_facecolor(PBI_BG)
    if nrows == 1 and ncols == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
    for ax in axes:
        ax.set_facecolor(PBI_CARD)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#555")
        ax.spines["bottom"].set_color("#555")
        ax.tick_params(colors="#ccc")
        ax.yaxis.label.set_color("#ccc")
        ax.xaxis.label.set_color("#ccc")
    return fig, axes


def _kpi_card(ax, title, value, color=PBI_ACCENT, subtitle=""):
    ax.set_facecolor(PBI_CARD)
    ax.text(0.5, 0.65, value, ha="center", va="center", fontsize=28, fontweight="bold", color=color)
    ax.text(0.5, 0.25, title, ha="center", va="center", fontsize=11, color="#aaa")
    if subtitle:
        ax.text(0.5, 0.08, subtitle, ha="center", va="center", fontsize=9, color="#666")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def _page_title(ax, title, subtitle=""):
    ax.set_facecolor(PBI_BG)
    ax.text(0.02, 0.7, title, fontsize=20, fontweight="bold", color="#fff")
    if subtitle:
        ax.text(0.02, 0.2, subtitle, fontsize=11, color="#aaa")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")


def _load(name):
    path = CLEAN_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path)


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE 1 — Executive Summary
# ═══════════════════════════════════════════════════════════════════════════
def dashboard_executive_summary(orders, delivered, delivery_logs):
    fig, axes = _dark_fig(5, 3, (16, 9))
    _page_title(axes[0], "Executive Summary", "SwiftDash — High-level business performance overview")

    total_rev = delivered["total_amount"].sum()
    total_orders = delivered["order_id"].nunique()
    aov = total_rev / total_orders if total_orders else 0
    on_time = delivery_logs["is_on_time"].mean() * 100 if len(delivery_logs) else 0
    cancellation = (orders["order_status"] == "Cancelled").mean() * 100
    avg_rating = orders["customer_rating"].mean()

    _kpi_card(axes[1], "Total Revenue", f"INR {total_rev:,.0f}", PBI_ACCENT)
    _kpi_card(axes[2], "Total Orders", f"{total_orders:,}", PBI_GREEN)
    _kpi_card(axes[3], "Avg Order Value", f"INR {aov:,.0f}", PBI_ORANGE)
    _kpi_card(axes[4], "On-Time Delivery", f"{on_time:.1f}%", PBI_GREEN)
    _kpi_card(axes[5], "Cancellation Rate", f"{cancellation:.1f}%", PBI_RED)
    _kpi_card(axes[6], "Avg Rating", f"{avg_rating:.1f}/5", PBI_PURPLE)

    monthly = delivered.set_index("order_date").resample("ME")["total_amount"].sum()
    ax = axes[7]
    ax.fill_between(monthly.index, monthly.values, alpha=0.15, color=PBI_ACCENT)
    ax.plot(monthly.index, monthly.values, color=PBI_ACCENT, linewidth=2, marker="o", markersize=3)
    ax.set_title("Monthly Revenue", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("Revenue (INR)")

    city_rev = delivered.groupby("restaurant_city")["total_amount"].sum().sort_values(ascending=False).head(8)
    ax = axes[8]
    bars = ax.barh(range(len(city_rev)), city_rev.values / 1e6, color=CHART_COLORS)
    ax.set_yticks(range(len(city_rev)))
    ax.set_yticklabels(city_rev.index, fontsize=9)
    ax.set_title("Top Cities by Revenue", fontsize=13, fontweight="bold", color="#fff")
    ax.set_xlabel("Revenue (Millions INR)")
    ax.invert_yaxis()

    fig.tight_layout(pad=2)
    fig.savefig(SCREENSHOTS / "dashboard_executive_summary.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved dashboard_executive_summary.png")


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE 2 — Customer Analytics
# ═══════════════════════════════════════════════════════════════════════════
def dashboard_customer_analytics(orders, delivered):
    fig, axes = _dark_fig(5, 3, (16, 9))
    _page_title(axes[0], "Customer Analytics", "Segmentation, retention, and customer value")

    cf = pd.read_csv(PROC_DIR / "customer_features.csv")
    unique_cust = delivered["customer_id"].nunique()
    repeat_rate = (cf[cf["frequency"] > 1].shape[0] / cf.shape[0] * 100) if cf.shape[0] else 0
    avg_clv = delivered["total_amount"].sum() / unique_cust if unique_cust else 0
    avg_orders = cf["frequency"].mean()
    _kpi_card(axes[1], "Unique Customers", f"{unique_cust:,}", PBI_ACCENT)
    _kpi_card(axes[2], "Repeat Rate", f"{repeat_rate:.1f}%", PBI_GREEN)
    _kpi_card(axes[3], "Avg CLV", f"INR {avg_clv:,.0f}", PBI_ORANGE)
    _kpi_card(axes[4], "Avg Orders/Customer", f"{avg_orders:.1f}", PBI_PURPLE)

    seg_counts = cf["customer_segment"].value_counts()
    ax = axes[5]
    seg_colors = {"Platinum": PBI_ACCENT, "Gold": PBI_ORANGE, "Silver": PBI_BLUE,
                  "At Risk": PBI_RED, "Churned": "#666"}
    wedges, texts, autotexts = ax.pie(
        seg_counts.values, labels=None, autopct="%1.1f%%",
        colors=[seg_colors.get(s, "#95a5a6") for s in seg_counts.index],
        startangle=90, textprops={"color": "#fff", "fontsize": 9}
    )
    for t in autotexts: t.set_color("#fff")
    ax.set_title("Customer Segments", fontsize=13, fontweight="bold", color="#fff")
    legend_labels = [f"{s} ({c})" for s, c in zip(seg_counts.index, seg_counts.values)]
    ax.legend(wedges, legend_labels, loc="lower center", ncol=3, fontsize=8,
              bbox_to_anchor=(0.5, -0.15), facecolor=PBI_CARD, labelcolor="#ccc")

    seg_rev = cf.groupby("customer_segment")["monetary"].sum().sort_values(ascending=False)
    ax = axes[6]
    bars = ax.bar(seg_rev.index, seg_rev.values / 1e6,
                  color=[seg_colors.get(s, "#95a5a6") for s in seg_rev.index])
    ax.set_title("Revenue by Segment", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("Revenue (Millions INR)")
    ax.tick_params(axis="x", rotation=20)

    wd = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly = delivered["weekday"].value_counts().reindex(wd).fillna(0)
    ax = axes[7]
    ax.bar(weekly.index, weekly.values, color=CHART_COLORS, width=0.6)
    ax.set_title("Orders by Day of Week", fontsize=13, fontweight="bold", color="#fff")
    ax.tick_params(axis="x", rotation=25, labelsize=8)

    hourly = delivered.groupby("order_hour").size()
    ax = axes[8]
    ax.bar(hourly.index, hourly.values, color=PBI_ACCENT, width=0.8)
    ax.set_title("Orders by Hour", fontsize=13, fontweight="bold", color="#fff")
    ax.set_xlabel("Hour")
    ax.set_xticks(range(0, 24, 3))
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=2)
    fig.savefig(SCREENSHOTS / "dashboard_customer_analytics.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved dashboard_customer_analytics.png")


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE 3 — Restaurant Analytics
# ═══════════════════════════════════════════════════════════════════════════
def dashboard_restaurant_analytics(orders, delivered, restaurants):
    fig, axes = _dark_fig(5, 3, (16, 9))
    _page_title(axes[0], "Restaurant Analytics", "Cuisine performance, restaurant tiers, and revenue")

    rf = pd.read_csv(PROC_DIR / "restaurant_features.csv")
    active_rest = restaurants["is_active"].sum()
    avg_rest_rating = restaurants["rating"].mean()
    total_cuisines = restaurants["cuisine_type"].nunique()
    total_rest_rev = rf["total_revenue"].sum()

    _kpi_card(axes[1], "Active Restaurants", f"{int(active_rest)}", PBI_ACCENT)
    _kpi_card(axes[2], "Avg Restaurant Rating", f"{avg_rest_rating:.2f}/5", PBI_ORANGE)
    _kpi_card(axes[3], "Cuisine Types", f"{total_cuisines}", PBI_GREEN)
    _kpi_card(axes[4], "Total Restaurant Rev", f"INR {total_rest_rev:,.0f}", PBI_PURPLE)

    merged = delivered.merge(restaurants[["restaurant_id", "cuisine_type"]], on="restaurant_id")
    cuisines = merged.groupby("cuisine_type").agg(revenue=("total_amount", "sum")).sort_values("revenue", ascending=False).head(10)
    ax = axes[5]
    bars = ax.barh(range(len(cuisines)), cuisines["revenue"].values / 1e6, color=CHART_COLORS)
    ax.set_yticks(range(len(cuisines)))
    ax.set_yticklabels(cuisines.index, fontsize=9)
    ax.set_title("Top 10 Cuisines by Revenue", fontsize=13, fontweight="bold", color="#fff")
    ax.set_xlabel("Revenue (Millions INR)")
    ax.invert_yaxis()

    tier_counts = rf["revenue_tier"].value_counts()
    ax = axes[6]
    tier_colors = {"High": PBI_GREEN, "Medium": PBI_ORANGE, "Low": PBI_RED}
    ax.bar(tier_counts.index, tier_counts.values, color=[tier_colors.get(t, "#95a5a6") for t in tier_counts.index])
    ax.set_title("Restaurants by Revenue Tier", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("Count")
    for i, v in enumerate(tier_counts.values):
        ax.text(i, v + 0.5, str(v), ha="center", fontsize=10, color="#fff")

    top_rest = rf.nlargest(10, "total_revenue")[["name", "total_revenue"]].copy()
    top_rest["total_revenue_m"] = top_rest["total_revenue"] / 1e6
    ax = axes[7]
    bars = ax.barh(range(len(top_rest)), top_rest["total_revenue_m"].values, color=PBI_ACCENT)
    ax.set_yticks(range(len(top_rest)))
    ax.set_yticklabels(top_rest["name"].str[:18], fontsize=8)
    ax.set_title("Top 10 Restaurants by Revenue", fontsize=13, fontweight="bold", color="#fff")
    ax.set_xlabel("Revenue (Millions INR)")
    ax.invert_yaxis()
    ax.tick_params(labelsize=8)

    canc = rf.nlargest(10, "cancellation_rate")[["name", "cancellation_rate"]]
    ax = axes[8]
    ax.barh(range(len(canc)), canc["cancellation_rate"].values * 100, color=PBI_RED)
    ax.set_yticks(range(len(canc)))
    ax.set_yticklabels(canc["name"].str[:18], fontsize=8)
    ax.set_title("Highest Cancellation Rates", fontsize=13, fontweight="bold", color="#fff")
    ax.set_xlabel("Cancellation Rate (%)")
    ax.invert_yaxis()
    ax.tick_params(labelsize=8)

    fig.tight_layout(pad=2)
    fig.savefig(SCREENSHOTS / "dashboard_restaurant_analytics.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved dashboard_restaurant_analytics.png")


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE 4 — Delivery Operations
# ═══════════════════════════════════════════════════════════════════════════
def dashboard_delivery_operations(orders, delivered, delivery_logs):
    fig, axes = _dark_fig(5, 3, (16, 9))
    _page_title(axes[0], "Delivery Operations", "Driver performance, travel times, and traffic impact")

    active_drivers = delivery_logs["driver_id"].nunique()
    avg_travel = delivery_logs["travel_time_mins"].mean()
    avg_distance = delivery_logs["distance_km"].mean()
    on_time_rate = delivery_logs["is_on_time"].mean() * 100

    _kpi_card(axes[1], "Active Drivers", f"{active_drivers:,}", PBI_ACCENT)
    _kpi_card(axes[2], "Avg Travel Time", f"{avg_travel:.0f} min", PBI_ORANGE)
    _kpi_card(axes[3], "Avg Distance", f"{avg_distance:.1f} km", PBI_BLUE)
    _kpi_card(axes[4], "On-Time Rate", f"{on_time_rate:.1f}%", PBI_GREEN)

    ax = axes[5]
    ax.hist(delivery_logs["travel_time_mins"], bins=30, color=PBI_ACCENT, edgecolor="white", alpha=0.8)
    ax.axvline(delivery_logs["travel_time_mins"].median(), color=PBI_RED,
               linestyle="--", linewidth=2, label=f"Median: {delivery_logs['travel_time_mins'].median():.0f} min")
    ax.set_title("Travel Time Distribution", fontsize=13, fontweight="bold", color="#fff")
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Deliveries")
    ax.legend(facecolor=PBI_CARD, labelcolor="#ccc")

    traffic_rate = delivery_logs.groupby("traffic_condition")["is_on_time"].mean() * 100
    ax = axes[6]
    t_colors = {"Low": PBI_GREEN, "Moderate": PBI_BLUE, "High": PBI_ORANGE, "Gridlock": PBI_RED}
    bars = ax.bar(traffic_rate.index, traffic_rate.values,
                  color=[t_colors.get(t, "#95a5a6") for t in traffic_rate.index])
    ax.set_title("On-Time Rate by Traffic", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("On-Time Rate (%)")
    for i, v in enumerate(traffic_rate.values):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9, color="#fff")

    weather_rate = delivery_logs.groupby("weather_condition")["is_on_time"].mean() * 100
    ax = axes[7]
    w_colors = {"Clear": PBI_GREEN, "Cloudy": PPI_BLUE if 'PPI' in dir() else PBI_BLUE, "Rainy": PBI_ORANGE, "Stormy": PBI_RED}
    w_colors = {"Clear": PBI_GREEN, "Cloudy": PBI_BLUE, "Rainy": PBI_ORANGE, "Stormy": PBI_RED}
    ax.bar(weather_rate.index, weather_rate.values,
           color=[w_colors.get(w, "#95a5a6") for w in weather_rate.index])
    ax.set_title("On-Time Rate by Weather", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("On-Time Rate (%)")

    vehicle_counts = delivery_logs.groupby("driver_id").first().reset_index().merge(
        pd.read_csv(CLEAN_DIR / "drivers_clean.csv")[["driver_id", "vehicle_type"]], on="driver_id"
    )["vehicle_type"].value_counts()
    ax = axes[8]
    ax.pie(vehicle_counts.values, labels=vehicle_counts.index, autopct="%1.1f%%",
           colors=[PBI_ACCENT, PBI_GREEN, PBI_ORANGE, PBI_PURPLE],
           textprops={"color": "#fff", "fontsize": 9})
    ax.set_title("Vehicle Type Distribution", fontsize=13, fontweight="bold", color="#fff")

    fig.tight_layout(pad=2)
    fig.savefig(SCREENSHOTS / "dashboard_delivery_operations.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved dashboard_delivery_operations.png")


# ═══════════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE 5 — Business Insights
# ═══════════════════════════════════════════════════════════════════════════
def dashboard_business_insights(orders, delivered):
    fig, axes = _dark_fig(5, 3, (16, 9))
    _page_title(axes[0], "Business Insights",
                "Growth metrics, time intelligence, and revenue drivers")

    total_rev = delivered["total_amount"].sum()
    total_orders = delivered["order_id"].nunique()
    aov = total_rev / total_orders if total_orders else 0
    cancellation = (orders["order_status"] == "Cancelled").mean() * 100
    surge_rev = (delivered["total_amount"] - delivered["total_amount"] / delivered["surge_multiplier"]).sum()
    discount_pct = delivered["discount"].sum() / total_rev * 100 if total_rev else 0

    _kpi_card(axes[1], "Surge Revenue", f"INR {surge_rev:,.0f}", PBI_ORANGE,
              "Additional revenue from surge pricing")
    _kpi_card(axes[2], "Discount % of Revenue", f"{discount_pct:.1f}%", PBI_PURPLE)
    _kpi_card(axes[3], "Items/Order", f"{delivered['order_id'].count() / total_orders:.1f}", PBI_TEAL)
    _kpi_card(axes[4], "Weekend Orders", f"{delivered['is_weekend'].sum():,}", PBI_ACCENT)

    monthly = delivered.set_index("order_date").resample("ME")["total_amount"].sum()
    monthly_pct = monthly.pct_change() * 100
    ax = axes[5]
    colors = [PBI_GREEN if v >= 0 else PBI_RED for v in monthly_pct.values]
    ax.bar(range(len(monthly_pct)), monthly_pct.values, color=colors, width=0.7)
    ax.set_title("Month-over-Month Revenue Growth %", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("Growth (%)")
    ax.axhline(0, color="#555", linewidth=0.5)
    ax.set_xticks(range(len(monthly_pct)))
    ax.set_xticklabels([d.strftime("%b\n%Y") for d in monthly_pct.index], fontsize=6, rotation=0)

    payment = delivered["payment_method"].value_counts()
    ax = axes[6]
    wedges, texts, autotexts = ax.pie(
        payment.values, labels=payment.index, autopct="%1.1f%%",
        colors=CHART_COLORS, startangle=90,
        textprops={"color": "#fff", "fontsize": 9}
    )
    for t in autotexts: t.set_color("#fff")
    ax.set_title("Payment Method Split", fontsize=13, fontweight="bold", color="#fff")

    weekend_rate = delivered.groupby("is_weekend")["total_amount"].sum()
    ax = axes[7]
    ax.bar(["Weekday", "Weekend"], weekend_rate.values / 1e6,
           color=[PBI_BLUE, PBI_ORANGE], width=0.5)
    ax.set_title("Revenue: Weekday vs Weekend", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("Revenue (Millions INR)")
    for i, v in enumerate(weekend_rate.values):
        ax.text(i, v / 1e6 + 0.1, f"INR {v / 1e6:.1f}M", ha="center", fontsize=9, color="#fff")

    payment_aov = delivered.groupby("payment_method")["total_amount"].mean()
    ax = axes[8]
    ax.bar(payment_aov.index, payment_aov.values, color=CHART_COLORS, width=0.5)
    ax.set_title("Avg Order Value by Payment", fontsize=13, fontweight="bold", color="#fff")
    ax.set_ylabel("Avg Order Value (INR)")
    ax.tick_params(axis="x", rotation=20, labelsize=8)

    fig.tight_layout(pad=2)
    fig.savefig(SCREENSHOTS / "dashboard_business_insights.png", dpi=150, bbox_inches="tight")
    plt.close()
    logger.info("Saved dashboard_business_insights.png")


# ═══════════════════════════════════════════════════════════════════════════
def main():
    logger.info("=" * 50)
    logger.info("START: Visualization export")
    logger.info("=" * 50)

    try:
        orders = _load("orders_clean.csv")
        restaurants = _load("restaurants_clean.csv")
        delivery_logs = _load("delivery_logs_clean.csv")

        orders["order_date"] = pd.to_datetime(orders["order_date"])
        delivered = orders[orders["order_status"].isin(["Delivered", "Refunded"])].copy()

        logger.info("Generating Power BI-style dashboard page screenshots...")
        dashboard_executive_summary(orders, delivered, delivery_logs)
        dashboard_customer_analytics(orders, delivered)
        dashboard_restaurant_analytics(orders, delivered, restaurants)
        dashboard_delivery_operations(orders, delivered, delivery_logs)
        dashboard_business_insights(orders, delivered)

        logger.info("All dashboard screenshots exported to %s", SCREENSHOTS)
        logger.info("=" * 50)
        logger.info("Visualization export complete.")
        logger.info("=" * 50)
    except Exception as exc:
        logger.critical("Visualization export failed: %s", exc, exc_info=True)
        raise


if __name__ == "__main__":
    main()
