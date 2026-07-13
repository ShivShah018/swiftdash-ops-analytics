"""
Build Power BI project (PbixProj) from pipeline outputs.

Generates a complete .pbixproj folder structure with:
  - TMDL data model (9 tables, relationships, 25+ DAX measures)
  - M queries for CSV import from data/cleaned/ and data/processed/
  - Report layout with 5 pages + all required PBIX part files

The folder can be compiled into a .pbit using pbi-tools:
    pbi-tools compile dashboard/swiftdash_dashboard.pbip dashboard/swiftdash_dashboard.pbit PBIT True

Open the .pbit in Power BI Desktop → Refresh → Save As → .pbix

Usage:
    python scripts/build_powerbi.py
"""

import json, shutil, sys, logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import PROJECT_ROOT, CLEAN_DIR, PROC_DIR

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("build_powerbi")

# ── Paths ──────────────────────────────────────────────────────────────────
PBI_PROJ = PROJECT_ROOT / "dashboard" / "swiftdash_dashboard.pbip"
PBI_MODEL = PBI_PROJ / "model"
PBI_MASHUP = PBI_PROJ / "mashup"
PBI_REPORT = PBI_PROJ / "report"
PBI_TMDL = PBI_MODEL / ".tmdl"
OUTPUT_PBIT = PROJECT_ROOT / "dashboard" / "swiftdash_dashboard.pbit"


def clean():
    if PBI_PROJ.exists():
        shutil.rmtree(PBI_PROJ)
    for d in [PBI_TMDL, PBI_MASHUP, PBI_REPORT]:
        d.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════
# 1.  PROJECT SETTINGS + PBIX BOILERPLATE PARTS
# ═══════════════════════════════════════════════════════════════════════════
def write_settings():
    settings = {
        "$schema": "https://pbi.tools/schema/settings.json",
        "version": "1.0",
        "modelSerialization": "Tmdl",
        "mashupSerialization": "Default",
    }
    (PBI_PROJ / ".pbixproj.json").write_text(json.dumps(settings, indent=2))

    # Boilerplate PBIX part files required by pbi-tools compile
    (PBI_PROJ / "Version.txt").write_text("3.0")
    (PBI_PROJ / "ReportMetadata.json").write_text(
        '{"ReportMetadata":{"ReportId":"00000000-0000-0000-0000-000000000000",'
        '"PBIFileVersion":"2.141","PBIFileProductVersion":"2.141.1286.0"}}'
    )
    (PBI_PROJ / "ReportSettings.json").write_text(
        '{"ReportSettings":{"PageSizeType":"16by9","PageSize":{"Width":1280,"Height":720}}}'
    )
    (PBI_PROJ / "[Content_Types].xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="json" ContentType="application/json"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="txt" ContentType="text/plain"/>'
        '<Default Extension="tmdl" ContentType="application/json"/>'
        '<Override PartName="/report/report.json" ContentType="application/json"/>'
        "</Types>"
    )

    for sub, content in [
        ("Settings/settings.json", '{"userScope":[],"userScopeS":[]}'),
        ("Metadata/Metadata.json", '{"DaxOption":0}'),
        ("Connections/connections.json", "[]"),
        ("DiagramState/state.json", "{}"),
        ("DiagramLayout/layout.json", '{"DiagramLayout":{"Schema":{"Tables":[],"Relationships":[],"DisplayOptions":{}}}}'),
    ]:
        p = PBI_PROJ / sub
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    # SecurityBindings — empty binary file
    sb_dir = PBI_PROJ / "SecurityBindings"
    sb_dir.mkdir(parents=True, exist_ok=True)
    (sb_dir / "bindings").write_text("")


# ═══════════════════════════════════════════════════════════════════════════
# 2.  MASHUP —  M queries + [Content_Types].xml
# ═══════════════════════════════════════════════════════════════════════════
CSV_TABLES = {
    "customers":       CLEAN_DIR / "customers_clean.csv",
    "restaurants":     CLEAN_DIR / "restaurants_clean.csv",
    "drivers":         CLEAN_DIR / "drivers_clean.csv",
    "orders":          CLEAN_DIR / "orders_clean.csv",
    "order_items":     CLEAN_DIR / "order_items_clean.csv",
    "delivery_logs":   CLEAN_DIR / "delivery_logs_clean.csv",
    "customer_features": PROC_DIR / "customer_features.csv",
    "restaurant_features": PROC_DIR / "restaurant_features.csv",
    "daily_metrics":   PROC_DIR / "daily_metrics.csv",
}

def m_query(table_name):
    return f'''let
    Source = Csv.Document(
        File.Contents("{CSV_TABLES[table_name].resolve().as_posix()}"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers"'''

MASHUP_TEMPLATE = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="m" ContentType="text/plain" />
  <Default Extension="xml" ContentType="application/xml" />
</Types>'''

def write_mashup():
    (PBI_MASHUP / "[Content_Types].xml").write_text(MASHUP_TEMPLATE)
    partitions_dir = PBI_MASHUP / "partitions"
    partitions_dir.mkdir(exist_ok=True)
    for name in CSV_TABLES:
        (partitions_dir / f"{name}.m").write_text(m_query(name))
    logger.info("Mashup: wrote %d M partition queries", len(CSV_TABLES))


# ═══════════════════════════════════════════════════════════════════════════
# 3.  TABULAR MODEL  — TMDL files
# ═══════════════════════════════════════════════════════════════════════════

COLUMN_TYPES = {
    "customers": {
        "customer_id": "string", "name": "string", "age": "int64",
        "gender": "string", "city": "string", "latitude": "double",
        "longitude": "double", "phone": "int64", "email": "string",
        "signup_date": "string", "is_active": "boolean",
    },
    "restaurants": {
        "restaurant_id": "string", "name": "string", "cuisine_type": "string",
        "city": "string", "latitude": "double", "longitude": "double",
        "rating": "double", "avg_cost_for_two": "int64", "join_date": "string",
        "is_active": "boolean", "preparation_time_mins": "int64",
    },
    "drivers": {
        "driver_id": "string", "name": "string", "age": "int64", "city": "string",
        "latitude": "double", "longitude": "double", "vehicle_type": "string",
        "rating": "double", "join_date": "string", "is_active": "boolean",
    },
    "orders": {
        "order_id": "string", "customer_id": "string", "restaurant_id": "string",
        "driver_id": "string", "order_datetime": "string", "order_date": "string",
        "order_hour": "int64", "weekday": "string", "is_weekend": "boolean",
        "order_amount": "double", "delivery_fee": "double", "discount": "double",
        "tax": "double", "platform_fee": "double", "surge_multiplier": "double",
        "total_amount": "double", "payment_method": "string",
        "order_status": "string", "customer_city": "string",
        "restaurant_city": "string", "customer_rating": "double",
    },
    "order_items": {
        "order_item_id": "int64", "order_id": "string", "item_name": "string",
        "category": "string", "quantity": "int64", "unit_price": "double",
        "line_total": "double",
    },
    "delivery_logs": {
        "delivery_id": "string", "order_id": "string", "driver_id": "string",
        "pickup_datetime": "string", "drop_datetime": "string",
        "distance_km": "double", "travel_time_mins": "int64",
        "traffic_condition": "string", "weather_condition": "string",
        "is_on_time": "boolean",
    },
    "customer_features": {
        "customer_id": "string", "name": "string", "age": "int64",
        "gender": "string", "city": "string", "latitude": "double",
        "longitude": "double", "phone": "int64", "email": "string",
        "signup_date": "string", "is_active": "boolean",
        "recency_days": "double", "frequency": "double", "monetary": "double",
        "avg_order_value": "double", "avg_discount_used": "double",
        "preferred_payment": "string", "cuisine_variety": "double",
        "first_order_date": "string", "last_order_date": "string",
        "days_since_first": "double", "customer_segment": "string",
        "customer_tenure_months": "double", "avg_order_frequency_days": "double",
    },
    "restaurant_features": {
        "restaurant_id": "string", "name": "string", "cuisine_type": "string",
        "city": "string", "latitude": "double", "longitude": "double",
        "rating": "double", "avg_cost_for_two": "int64", "join_date": "string",
        "is_active": "boolean", "preparation_time_mins": "int64",
        "total_orders": "double", "total_revenue": "double",
        "avg_order_value": "double", "total_discount": "double",
        "unique_customers": "double", "avg_items_per_order": "double",
        "cancellation_rate": "double", "revenue_per_customer": "double",
        "revenue_tier": "string",
    },
    "daily_metrics": {
        "order_date": "string", "orders_count": "int64", "revenue": "double",
        "avg_order_value": "double", "unique_customers": "int64",
        "unique_restaurants": "int64",
    },
}

KEYS = {
    "customers": "customer_id", "restaurants": "restaurant_id",
    "drivers": "driver_id", "orders": "order_id",
    "order_items": "order_item_id", "delivery_logs": "delivery_id",
    "customer_features": "customer_id",
    "restaurant_features": "restaurant_id",
    "daily_metrics": "order_date",
}

RELATIONSHIPS = [
    ("orders_customer", "orders", "customer_id", "customers", "customer_id", "oneDirection"),
    ("orders_restaurant", "orders", "restaurant_id", "restaurants", "restaurant_id", "oneDirection"),
    ("orders_driver", "orders", "driver_id", "drivers", "driver_id", "oneDirection"),
    ("order_items_order", "order_items", "order_id", "orders", "order_id", "oneDirection"),
    ("delivery_logs_order", "delivery_logs", "order_id", "orders", "order_id", "oneDirection"),
    ("delivery_logs_driver", "delivery_logs", "driver_id", "drivers", "driver_id", "oneDirection"),
    ("customer_features_customer", "customer_features", "customer_id", "customers", "customer_id", "oneDirection"),
    ("restaurant_features_restaurant", "restaurant_features", "restaurant_id", "restaurants", "restaurant_id", "oneDirection"),
]

DAX_MEASURES = {
    # Core KPIs
    "Total Revenue": 'CALCULATE(SUM(orders[total_amount]), orders[order_status] = "Delivered")',
    "Total Orders": 'CALCULATE(COUNTROWS(orders), orders[order_status] = "Delivered")',
    "Avg Order Value": "DIVIDE([Total Revenue], [Total Orders])",
    "Total Delivered Orders": 'CALCULATE(COUNTROWS(orders), orders[order_status] = "Delivered")',
    "Cancellation Rate": "VAR AllOrders = COUNTROWS(orders) VAR Cancelled = CALCULATE(COUNTROWS(orders), orders[order_status] = \"Cancelled\") RETURN DIVIDE(Cancelled, AllOrders, 0)",
    "OnTime Delivery Rate": "VAR TotalDeliveries = COUNTROWS(delivery_logs) VAR OnTime = COUNTROWS(FILTER(delivery_logs, delivery_logs[is_on_time] = TRUE)) RETURN DIVIDE(OnTime, TotalDeliveries, 0)",
    "Avg Customer Rating": "CALCULATE(AVERAGE(orders[customer_rating]), orders[customer_rating] > 0)",
    "Total Discounts Given": "SUM(orders[discount])",
    "Active Restaurants": 'CALCULATE(COUNTROWS(restaurants), restaurants[is_active] = TRUE)',
    "Active Drivers": 'CALCULATE(COUNTROWS(drivers), drivers[is_active] = TRUE)',
    "Unique Customers": "DISTINCTCOUNT(orders[customer_id])",
    # Time Intelligence
    "Revenue MoM Growth": "VAR CurrentMonth = [Total Revenue] VAR PrevMonth = CALCULATE([Total Revenue], PREVIOUSMONTH('Calendar'[Date])) RETURN DIVIDE(CurrentMonth - PrevMonth, PrevMonth, 0)",
    "Revenue YoY Growth": "VAR CurrentPeriod = [Total Revenue] VAR PrevPeriod = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Calendar'[Date])) RETURN DIVIDE(CurrentPeriod - PrevPeriod, PrevPeriod, 0)",
    "Revenue Rolling30D": "CALCULATE([Total Revenue], DATESINPERIOD('Calendar'[Date], MAX('Calendar'[Date]), -30, DAY))",
    "Revenue MTD": "TOTALMTD([Total Revenue], 'Calendar'[Date])",
    "Revenue QTD": "TOTALQTD([Total Revenue], 'Calendar'[Date])",
    "Revenue YTD": "TOTALYTD([Total Revenue], 'Calendar'[Date])",
    # Customer
    "Repeat Customer Rate": """VAR CustomersWithOrders = SUMMARIZE(orders, orders[customer_id])
VAR RepeatCustomers = FILTER(CustomersWithOrders, CALCULATE(COUNTROWS(orders), orders[order_status] = "Delivered") > 1)
RETURN DIVIDE(COUNTROWS(RepeatCustomers), COUNTROWS(CustomersWithOrders), 0)""",
    "Avg Customer Lifetime Value": "DIVIDE([Total Revenue], [Unique Customers], 0)",
    "Customer Segment Count": "DISTINCTCOUNT(customer_features[customer_segment])",
    # Operations
    "Avg Delivery Time Mins": "AVERAGE(delivery_logs[travel_time_mins])",
    "Avg Delivery Distance KM": "AVERAGE(delivery_logs[distance_km])",
    "Peak Hour Orders": """MAXX(VALUES(orders[order_hour]),
    CALCULATE(COUNTROWS(orders), orders[order_status] = "Delivered"))""",
    "Orders Per Driver": "DIVIDE([Total Delivered Orders], [Active Drivers], 0)",
    # Revenue Mix
    "Surge Revenue Premium": "SUM(orders[total_amount]) - SUMX(orders, orders[total_amount] / orders[surge_multiplier])",
}

def tmdl_type(dtype):
    return {"string": "string", "int64": "int64", "double": "double", "boolean": "boolean"}.get(dtype, "string")

def generate_table_tmdl(name):
    lines = [f"table {name} {{"]
    cols = COLUMN_TYPES[name]
    pk = KEYS[name]
    for cname, dtype in cols.items():
        t = tmdl_type(dtype)
        is_key = "true" if cname == pk else "false"
        if cname == pk:
            lines.append(f"    column {cname} dataType: {t} {{ isKey: true }}")
        elif dtype == "boolean":
            lines.append(f"    column {cname} dataType: {t} {{ trueValue: \"True\", falseValue: \"False\" }}")
        else:
            lines.append(f"    column {cname} dataType: {t}")
    lines.append("")
    # Partition referencing M query
    lines.append(f"    partition 'Partition' mode: import {{ source: #\"{name}\" }}")
    lines.append("")
    # Add DAX measures that reference this table
    for mname, expr in DAX_MEASURES.items():
        table_ref = mname.split("_")[0].lower() if "_" in mname else ""
        # Simple heuristic: measure references this table if its name appears in the expression
        if name in mname.lower() or any(tok in expr.lower() for tok in [name, name + "["]):
            lines.append(f"    measure '{mname}' := {expr}")
    lines.append("}")
    return "\n".join(lines)

def write_model():
    # Write table TMDL files
    for tname in COLUMN_TYPES:
        tmdl = generate_table_tmdl(tname)
        (PBI_TMDL / f"{tname}.tmdl").write_text(tmdl)
    # Write Calendar table
    cal_tmdl = """table 'Calendar' {
    column Date dataType: dateTime {
        isKey: true
        formatString: "yyyy-MM-dd"
    }
    column Year dataType: int64
    column Quarter dataType: string
    column Month dataType: string
    column MonthNo dataType: int64
    column YearMonth dataType: string
    column Weekday dataType: string
    column IsWeekend dataType: boolean { trueValue: "True", falseValue: "False" }

    partition 'Calendar' mode: import {
        source: #"Calendar"
    }
}"""
    (PBI_TMDL / "Calendar.tmdl").write_text(cal_tmdl)
    # Write M query for Calendar
    cal_m = """let
    StartDate = #date(2022, 1, 1),
    EndDate = #date(2025, 6, 30),
    Dates = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    ToTable = Table.FromList(Dates, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    Renamed = Table.RenameColumns(ToTable, {{"Column1", "Date"}}),
    #"Changed Type" = Table.TransformColumnTypes(Renamed, {{"Date", type date}}),
    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Quarter" = Table.AddColumn(#"Added Year", "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    #"Added Month" = Table.AddColumn(#"Added Quarter", "Month", each Date.MonthName([Date]), type text),
    #"Added MonthNo" = Table.AddColumn(#"Added Month", "MonthNo", each Date.Month([Date]), Int64.Type),
    #"Added YearMonth" = Table.AddColumn(#"Added MonthNo", "YearMonth", each Text.From(Date.Year([Date])) & "-" & Text.PadStart(Text.From(Date.Month([Date])), 2, "0"), type text),
    #"Added Weekday" = Table.AddColumn(#"Added YearMonth", "Weekday", each Date.DayOfWeekName([Date]), type text),
    #"Added IsWeekend" = Table.AddColumn(#"Added Weekday", "IsWeekend", each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical)
in
    #"Added IsWeekend"""
    partitions_dir = PBI_MASHUP / "partitions"
    (partitions_dir / "Calendar.m").write_text(cal_m)
    # Write relationships
    rel_lines = []
    for rel_id, from_tab, from_col, to_tab, to_col, direction in RELATIONSHIPS:
        cf = "crossFilteringBehavior: oneDirection;" if direction == "oneDirection" else ""
        rel_lines.append(f"relationship '{rel_id}' : {from_tab}[{from_col}] -> {to_tab}[{to_col}] {{{cf}}}")
    # Add Calendar relationships
    rel_lines.append("relationship 'orders_date' : orders[order_date] -> 'Calendar'[Date] { crossFilteringBehavior: oneDirection; }")
    (PBI_TMDL / "relationships.tmdl").write_text("\n".join(rel_lines))
    # Write model settings
    model_tmdl = """model {
    culture: "en-US"
    defaultPowerBIDataSourceVersion: powerBI_V3
}"""
    (PBI_TMDL / "model.tmdl").write_text(model_tmdl)
    logger.info("Model: wrote %d table TMDL + Calendar + relationships", len(COLUMN_TYPES))


# ═══════════════════════════════════════════════════════════════════════════
# 4.  REPORT LAYOUT  (simplified — user customises visuals in Power BI Desktop)
# ═══════════════════════════════════════════════════════════════════════════
def write_report():
    report = {
        "name": "SwiftDash Dashboard",
        "pages": [
            {"name": "ExecutiveSummary", "displayName": "Executive Summary",
             "order": 0, "visuals": [], "pageBinding": {"type": 0}},
            {"name": "CustomerAnalytics", "displayName": "Customer Analytics",
             "order": 1, "visuals": [], "pageBinding": {"type": 0}},
            {"name": "RestaurantAnalytics", "displayName": "Restaurant Analytics",
             "order": 2, "visuals": [], "pageBinding": {"type": 0}},
            {"name": "DeliveryOperations", "displayName": "Delivery Operations",
             "order": 3, "visuals": [], "pageBinding": {"type": 0}},
            {"name": "BusinessInsights", "displayName": "Business Insights",
             "order": 4, "visuals": [], "pageBinding": {"type": 0}},
        ],
    }
    (PBI_REPORT / "report.json").write_text(json.dumps(report, indent=2))
    logger.info("Report: wrote 5-page layout structure")


# ═══════════════════════════════════════════════════════════════════════════
def main():
    logger.info("Building SwiftDash Power BI Project...")
    clean()
    write_settings()
    write_mashup()
    write_model()
    write_report()
    logger.info("")
    logger.info("=== SwiftDash Power BI Project ===")
    logger.info("PbixProj folder: %s", PBI_PROJ)
    logger.info("")
    logger.info("To create .pbit, compile with pbi-tools (requires Power BI Desktop):")
    logger.info('  pbi-tools compile "%s" "%s" PBIT True', PBI_PROJ, OUTPUT_PBIT)
    logger.info("")
    logger.info("Or manually in Power BI Desktop:")
    logger.info("  1. File → Open → PbixProj folder")
    logger.info("  2. Data → Transform Data → Source → Set CSV paths")
    logger.info("  3. Close & Apply → Wait for model refresh")
    logger.info("  4. Drag visuals onto pages from Fields pane")
    logger.info("  5. File → Save As → .pbix")
    logger.info("")

if __name__ == "__main__":
    main()
