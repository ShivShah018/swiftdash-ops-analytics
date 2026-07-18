import streamlit as st
import pandas as pd
import datetime
from utils import data_loader as dl, kpi, charts

@st.cache_data(ttl=600, show_spinner=False)
def get_filtered_data(date_range, city_filter, restaurant_filter, segment_filter):
    df_orders = dl.load_orders()
    df_customers = dl.load_customers()
    df_restaurants = dl.load_restaurants()
    df_delivery = dl.load_delivery_logs()
    df_features = dl.load_customer_features()

    df_orders = df_orders.merge(
        df_delivery[["order_id", "travel_time_mins", "traffic_condition", "is_on_time"]],
        on="order_id", how="left"
    )
    if "traffic_condition" in df_orders.columns:
        df_orders["traffic"] = df_orders.pop("traffic_condition")

    df_rest_names = df_restaurants[["restaurant_id", "name"]].copy()
    df_rest_names.columns = ["restaurant_id", "restaurant_name"]
    df_orders = df_orders.merge(df_rest_names, on="restaurant_id", how="left")

    if "customer_segment" in df_features.columns:
        df_customers = df_customers.merge(
            df_features[["customer_id", "customer_segment"]],
            on="customer_id", how="left"
        )
        df_customers.rename(columns={"customer_segment": "segment"}, inplace=True)

    if "segment" in df_customers.columns:
        df_orders = df_orders.merge(
            df_customers[["customer_id", "segment"]],
            on="customer_id", how="left"
        )

    if date_range:
        if len(date_range) == 2:
            start, end = date_range
            df_orders = df_orders[(df_orders["order_date"] >= pd.to_datetime(start)) & (df_orders["order_date"] <= pd.to_datetime(end))]
        elif len(date_range) == 1:
            start = date_range[0]
            df_orders = df_orders[df_orders["order_date"] >= pd.to_datetime(start)]

    if city_filter:
        city_col = "customer_city" if "customer_city" in df_orders.columns else ("city" if "city" in df_orders.columns else None)
        if city_col:
            df_orders = df_orders[df_orders[city_col].isin(city_filter)]

    if restaurant_filter and "restaurant_name" in df_orders.columns:
        df_orders = df_orders[df_orders["restaurant_name"].isin(restaurant_filter)]

    if segment_filter and "segment" in df_orders.columns:
        df_orders = df_orders[df_orders["segment"].isin(segment_filter)]

    return df_orders, df_customers, df_restaurants


def render_demo():
    st.sidebar.title("Global Filters")
    today = datetime.date.today()
    date_range = st.sidebar.date_input("Date Range", value=None, max_value=today)
    
    city_options = dl.get_unique_cities()
    city_filter = st.sidebar.multiselect("Cities", options=city_options, default=city_options)
    
    restaurant_options = dl.get_unique_restaurants()
    restaurant_filter = st.sidebar.multiselect("Restaurants", options=restaurant_options, default=restaurant_options)
    
    segment_options = ["Platinum", "Gold", "Silver", "At Risk", "Churned", "Other"]
    segment_filter = st.sidebar.multiselect("Customer Segments", options=segment_options, default=segment_options)

    orders_df, customers_df, restaurants_df = get_filtered_data(date_range, city_filter, restaurant_filter, segment_filter)

    page = st.sidebar.radio("Navigation", [
        "Executive Dashboard",
        "Restaurant Analytics",
        "Delivery Performance",
        "Customer Insights",
        "About"
    ], key="demo_nav")

    if page == "Executive Dashboard":
        st.title("Executive Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Orders", kpi.total_orders(orders_df))
        with col2:
            st.metric("Revenue ($)", f"{kpi.total_revenue(orders_df):,.2f}")
        with col3:
            st.metric("On‑time Delivery %", f"{kpi.on_time_rate(orders_df):.1%}")
        with col4:
            st.metric("Active Customers", kpi.active_customers(customers_df))
        st.plotly_chart(charts.monthly_revenue_trend(orders_df), use_container_width=True)
        st.plotly_chart(charts.top_cities(orders_df), use_container_width=True)
    elif page == "Restaurant Analytics":
        st.title("Restaurant Analytics")
        st.plotly_chart(charts.revenue_by_cuisine(orders_df, restaurants_df), use_container_width=True)
        st.plotly_chart(charts.top_restaurants(orders_df), use_container_width=True)
    elif page == "Delivery Performance":
        st.title("Delivery Performance")
        st.plotly_chart(charts.delivery_time_distribution(orders_df), use_container_width=True)
        st.plotly_chart(charts.on_time_by_traffic(orders_df), use_container_width=True)
    elif page == "Customer Insights":
        st.title("Customer Insights")
        st.plotly_chart(charts.segment_distribution(customers_df), use_container_width=True)
        st.plotly_chart(charts.revenue_by_segment(orders_df, customers_df), use_container_width=True)
    elif page == "About":
        st.title("About SwiftDash Demo Dataset")
        st.markdown("* This is a built-in demo simulating a Food Delivery operations dataset.\n* The app works completely offline.")
        csv = orders_df.to_csv(index=False).encode()
        st.download_button(
            label="Download Filtered Orders CSV",
            data=csv,
            file_name="filtered_orders.csv",
            mime="text/csv",
        )
