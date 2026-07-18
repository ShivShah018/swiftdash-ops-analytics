import streamlit as st
import pandas as pd

def apply_smart_filters(df, types):
    """
    Dynamically generates sidebar filters for categorical, datetime, and numeric columns.
    Returns the filtered dataframe.
    """
    filtered_df = df.copy()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Dynamic Filters")
    
    # Categorical filters (max 10 categorical columns to avoid overwhelming the sidebar)
    cat_cols_to_filter = [c for c in types['categorical'] if filtered_df[c].nunique() <= 50][:10]
    for col in cat_cols_to_filter:
        options = filtered_df[col].dropna().unique().tolist()
        if options:
            selected = st.sidebar.multiselect(f"{col}", options=options, default=[])
            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]
                
    import datetime
    today = datetime.date.today()
    # Datetime filters
    for col in types['datetime'][:2]:  # Limit to 2 datetimes
        min_date = filtered_df[col].min()
        max_date = filtered_df[col].max()
        if pd.notna(min_date) and pd.notna(max_date):
            max_allowed = min(max_date.date(), today)
            date_range = st.sidebar.date_input(
                f"{col} Range",
                value=(min_date.date(), max_allowed),
                min_value=min_date.date(),
                max_value=max_allowed
            )
            if date_range:
                if len(date_range) == 2:
                    start, end = date_range
                    # Only filter if the user explicitly narrowed the range
                    if start > min_date.date() or end < max_allowed:
                        filtered_df = filtered_df[(filtered_df[col] >= pd.to_datetime(start)) & (filtered_df[col] <= pd.to_datetime(end))]
                elif len(date_range) == 1:
                    start = date_range[0]
                    if start > min_date.date():
                        filtered_df = filtered_df[filtered_df[col] >= pd.to_datetime(start)]
                
    # Numeric filters (Range Slider)
    num_cols_to_filter = types['numeric'][:5] # Limit to 5 numerics
    for col in num_cols_to_filter:
        min_val = float(filtered_df[col].min())
        max_val = float(filtered_df[col].max())
        if pd.notna(min_val) and pd.notna(max_val) and min_val < max_val:
            range_val = st.sidebar.slider(
                f"{col} Range",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                key=f"filter_num_final_{col}"
            )
            # Only apply the filter if the user adjusted the bounds (with small epsilon for float precision)
            if (range_val[0] > min_val + 1e-5) or (range_val[1] < max_val - 1e-5):
                filtered_df = filtered_df[
                    (filtered_df[col].isna()) | 
                    ((filtered_df[col] >= range_val[0]) & (filtered_df[col] <= range_val[1]))
                ]
            
    return filtered_df
