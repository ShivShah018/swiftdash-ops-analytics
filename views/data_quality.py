import streamlit as st
import pandas as pd
import plotly.express as px
from utils.detector import get_missing_stats

def render_data_quality(df, types):
    st.title(" Data Quality")
    
    if df.empty:
        st.warning("The dataset is empty after filtering. Please adjust your filters.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("###  Missing Values")
        missing_df = get_missing_stats(df)
        st.dataframe(missing_df, use_container_width=True)
        
    with col2:
        st.markdown("###  Duplicates")
        dupes = df.duplicated().sum()
        st.metric("Duplicate Rows", f"{dupes:,}")
        if dupes > 0:
            st.warning(f"Found {dupes} duplicate rows.")
            
    st.markdown("### ️ Missing Value Heatmap")
    if missing_df['Missing Values'].sum() > 0:
        # Generate a smaller boolean df for heatmap to save memory
        sample_size = min(len(df), 5000)
        missing_sample = df.sample(sample_size).isnull()
        fig = px.imshow(missing_sample, template="plotly_dark", title=f"Missing Values (Sample of {sample_size})", color_continuous_scale="gray")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No missing values found!")
        
    st.markdown("###  Outlier Detection (Numeric)")
    if types['numeric']:
        outliers_data = []
        for col in types['numeric']:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outliers_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            outliers_data.append({"Column": col, "Outliers": outliers_count, "% Outliers": round((outliers_count/len(df))*100, 2)})
        st.dataframe(pd.DataFrame(outliers_data), use_container_width=True)
    else:
        st.info("No numeric columns found for outlier detection.")
