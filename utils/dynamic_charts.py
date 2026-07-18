import plotly.express as px
import pandas as pd

def plot_histogram(df, column):
    fig = px.histogram(df, x=column, title=f"Distribution of {column}", marginal="box", template="plotly_dark")
    return fig

def plot_box(df, column):
    fig = px.box(df, y=column, title=f"Box Plot of {column}", template="plotly_dark")
    return fig

def plot_count(df, column, top_n=20):
    counts = df[column].value_counts().reset_index().head(top_n)
    counts.columns = [column, 'Count']
    counts = counts.sort_values('Count', ascending=True) # Sort so highest is at the top of the horizontal chart
    fig = px.bar(counts, y=column, x='Count', orientation='h', title=f"Top {top_n} {column}", template="plotly_dark")
    return fig

def plot_pie(df, column):
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, 'Count']
    fig = px.pie(counts, names=column, values='Count', title=f"Proportion of {column}", template="plotly_dark", hole=0.4)
    return fig

def plot_time_series(df, date_col, num_col):
    temp = df.groupby(pd.Grouper(key=date_col, freq='M'))[num_col].sum().reset_index()
    fig = px.line(temp, x=date_col, y=num_col, title=f"{num_col} over Time (Monthly)", template="plotly_dark", markers=True)
    return fig

def plot_scatter(df, col_x, col_y):
    fig = px.scatter(df, x=col_x, y=col_y, title=f"{col_y} vs {col_x}", template="plotly_dark", opacity=0.6)
    return fig

def plot_correlation_heatmap(df, num_cols):
    if len(num_cols) < 2:
        return None
    corr = df[num_cols].corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap", template="plotly_dark", color_continuous_scale="RdBu_r")
    return fig
