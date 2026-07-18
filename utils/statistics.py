import pandas as pd

def get_numeric_summary(df, numeric_cols):
    if not numeric_cols:
        return pd.DataFrame()
    
    summary = df[numeric_cols].describe().T
    summary = summary[['mean', 'std', 'min', '50%', 'max']]
    summary.rename(columns={'50%': 'median'}, inplace=True)
    return summary
