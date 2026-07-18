import streamlit as st
from utils import dynamic_charts as dc
from utils.detector import get_basic_stats
from utils.statistics import get_numeric_summary

def render_dashboard(df, types):
    st.title(" Dynamic Dashboard")
    
    # Empty state handling
    if df.empty:
        st.warning("The dataset is empty after filtering. Please adjust your filters.")
        return

    # 1. KPIs
    stats = get_basic_stats(df)
    st.markdown("###  Key Performance Indicators")
    cols = st.columns(6)
    cols[0].metric("Total Rows", f"{stats['total_rows']:,}")
    cols[1].metric("Total Columns", f"{stats['total_columns']:,}")
    cols[2].metric("Missing Cells", f"{stats['total_missing']:,}")
    cols[3].metric("Duplicate Rows", f"{stats['duplicate_rows']:,}")
    cols[4].metric("Numeric Cols", len(types['numeric']))
    cols[5].metric("Category Cols", len(types['categorical']))
    
    # Optional Numeric KPIs
    if types['numeric']:
        st.markdown("---")
        st.markdown("###  Numeric Summaries")
        num_summary = get_numeric_summary(df, types['numeric'])
        st.dataframe(num_summary, use_container_width=True)
        
    st.markdown("---")
    st.markdown("###  Dynamic Visualizations")
    
    # 2. Charts
    chart_cols = st.columns(2)
    col_idx = 0
    
    # Categorical Charts
    for col in types['categorical'][:4]: # Limit to avoid overload
        with chart_cols[col_idx % 2]:
            if df[col].nunique() <= 10:
                st.plotly_chart(dc.plot_pie(df, col), use_container_width=True)
            else:
                st.plotly_chart(dc.plot_count(df, col), use_container_width=True)
        col_idx += 1
        
    # Numeric Charts
    for col in types['numeric'][:4]:
        with chart_cols[col_idx % 2]:
            st.plotly_chart(dc.plot_histogram(df, col), use_container_width=True)
        col_idx += 1
        
    # Datetime Charts
    for d_col in types['datetime'][:2]:
        if types['numeric']:
            num_col = types['numeric'][0]
            with chart_cols[col_idx % 2]:
                st.plotly_chart(dc.plot_time_series(df, d_col, num_col), use_container_width=True)
            col_idx += 1
            
    # Scatter (if at least 2 numerics)
    if len(types['numeric']) >= 2:
        st.plotly_chart(dc.plot_scatter(df, types['numeric'][0], types['numeric'][1]), use_container_width=True)
        
    # Correlation Heatmap (if at least 3 numerics)
    if len(types['numeric']) >= 3:
        st.plotly_chart(dc.plot_correlation_heatmap(df, types['numeric']), use_container_width=True)
