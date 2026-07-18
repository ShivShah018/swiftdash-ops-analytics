import pandas as pd
import numpy as np

def detect_column_types(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    bool_cols = df.select_dtypes(include=[bool]).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
    
    # Categorical columns: object/string types, or categoricals.
    # Exclude datetime and bool.
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Sometimes numeric columns with few unique values act as categories
    # but we'll stick to strict types first, maybe adjust later if needed.
    
    # check for string columns that could be datetime
    for col in cat_cols.copy():
        if df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}').all() or df[col].astype(str).str.match(r'^\d{2}/\d{2}/\d{4}').all():
            try:
                df[col] = pd.to_datetime(df[col])
                datetime_cols.append(col)
                cat_cols.remove(col)
            except Exception:
                pass

    # Ensure mutually exclusive
    numeric_cols = [c for c in numeric_cols if c not in bool_cols]

    return {
        "numeric": numeric_cols,
        "categorical": cat_cols,
        "boolean": bool_cols,
        "datetime": datetime_cols
    }

def get_missing_stats(df):
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    return pd.DataFrame({
        "Missing Values": missing,
        "Percentage (%)": missing_pct
    })

def get_basic_stats(df):
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicate_rows": df.duplicated().sum(),
        "total_missing": df.isnull().sum().sum()
    }
