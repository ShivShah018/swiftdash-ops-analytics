import streamlit as st
import pandas as pd
from utils.detector import get_basic_stats

def render_overview(df, types):
    st.title(" Data Overview")
    
    if df.empty:
        st.warning("The dataset is empty after filtering. Please adjust your filters.")
        return
        
    col1, col2, col3, col4 = st.columns(4)
    stats = get_basic_stats(df)
    
    col1.metric("Total Rows", f"{stats['total_rows']:,}")
    col2.metric("Total Columns", f"{stats['total_columns']:,}")
    col3.metric("Numeric Columns", len(types['numeric']))
    col4.metric("Categorical Columns", len(types['categorical']))
    
    st.markdown("###  Dataset Preview (First 20 Rows)")
    st.dataframe(df.head(20), use_container_width=True)
    
    st.markdown("###  Dataset Preview (Last 20 Rows)")
    st.dataframe(df.tail(20), use_container_width=True)
    
    st.markdown("###  Memory Usage")
    mem = df.memory_usage(deep=True).sum() / (1024 ** 2)
    st.info(f"Total memory usage: **{mem:.2f} MB**")
    
    st.markdown("###  Column Information")
    info_df = pd.DataFrame({
        "Column Type": df.dtypes.astype(str),
        "Non-Null Count": df.notnull().sum(),
        "Unique Values": df.nunique()
    })
    st.dataframe(info_df, use_container_width=True)
