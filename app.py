import streamlit as st
import pandas as pd
from utils.detector import detect_column_types
from utils.filters import apply_smart_filters

# Import our modular views
from views import demo_dashboard, overview, data_quality, dashboard

st.set_page_config(
    page_title="SwiftDash – Universal CSV Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

def reset_state():
    for key in ['df', 'is_demo', 'types', 'filename']:
        if key in st.session_state:
            del st.session_state[key]

def process_upload(uploaded_file, sidebar=False):
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            msg = "Unable to load dataset. CSV is empty."
            if sidebar:
                st.sidebar.error(msg)
            else:
                st.error(msg)
            return False
        st.session_state['df'] = df
        st.session_state['types'] = detect_column_types(df)
        st.session_state['filename'] = uploaded_file.name
        st.session_state['is_demo'] = False
        return True
    except Exception as e:
        msg = f"Unable to read CSV: {e}"
        if sidebar:
            st.sidebar.error(msg)
        else:
            st.error(msg)
        return False

# ----------------------------------------------------------------------------
# Startup Screen
# ----------------------------------------------------------------------------
if 'df' not in st.session_state and 'is_demo' not in st.session_state:
    st.title("SwiftDash – Universal CSV Analytics Platform")
    st.markdown("Choose an option to get started:")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("Experience the platform using the built-in demo dataset.")
        if st.button("Load Demo Dataset", use_container_width=True):
            st.session_state['is_demo'] = True
            st.rerun()
            
    with col2:
        st.info("Upload your own CSV to generate a custom analytics dashboard.")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file is not None:
            with st.spinner("Analyzing dataset..."):
                if process_upload(uploaded_file):
                    st.success("Dataset loaded successfully.")
                    st.rerun()
                    
    st.stop()

# ----------------------------------------------------------------------------
# Main App / Sidebar
# ----------------------------------------------------------------------------
st.sidebar.title("Data Controls")

new_upload = st.sidebar.file_uploader("Replace Current Dataset", type=['csv'], key="sidebar_upload")
if new_upload is not None and ('filename' not in st.session_state or new_upload.name != st.session_state.get('filename')):
    with st.sidebar.status("Analyzing new dataset...", expanded=True) as status:
        if process_upload(new_upload, sidebar=True):
            status.update(label=f"Loaded {new_upload.name}", state="complete", expanded=False)
            st.rerun()
        else:
            status.update(label="Failed to load dataset.", state="error", expanded=False)

if st.sidebar.button("Close Dataset", use_container_width=True):
    reset_state()
    st.rerun()

# ----------------------------------------------------------------------------
# Demo Dashboard Route
# ----------------------------------------------------------------------------
if st.session_state.get('is_demo'):
    st.sidebar.markdown("---")
    st.sidebar.success("Viewing Demo Dataset")
    demo_dashboard.render_demo()
    
# ----------------------------------------------------------------------------
# Universal Dashboard Route
# ----------------------------------------------------------------------------
else:
    df = st.session_state['df']
    types = st.session_state['types']
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"Active File: **{st.session_state.get('filename')}**")
    
    with st.sidebar.expander("Dataset Profile", expanded=True):
        st.markdown(f"**Rows:** {len(df):,}")
        st.markdown(f"**Columns:** {len(df.columns)}")
        st.markdown(f"- Numeric: {len(types['numeric'])}")
        st.markdown(f"- Categorical: {len(types['categorical'])}")
        st.markdown(f"- Datetime: {len(types['datetime'])}")
        missing = df.isnull().sum().sum()
        st.markdown(f"**Missing Values:** {missing:,}")
        dupes = df.duplicated().sum()
        st.markdown(f"**Duplicate Rows:** {dupes:,}")
        
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio("Navigation", [
        "Dynamic Dashboard",
        "Data Overview",
        "Data Quality"
    ])
    
    # Smart Filters
    filtered_df = apply_smart_filters(df, types)
    
    if page == "Dynamic Dashboard":
        dashboard.render_dashboard(filtered_df, types)
    elif page == "Data Overview":
        overview.render_overview(filtered_df, types)
    elif page == "Data Quality":
        data_quality.render_data_quality(filtered_df, types)
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export Options")
    csv_data = filtered_df.to_csv(index=False).encode()
    st.sidebar.download_button(
        label="Download Filtered CSV",
        data=csv_data,
        file_name="filtered_export.csv",
        mime="text/csv",
    )
