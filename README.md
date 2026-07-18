# SwiftDash – Universal CSV Analytics Platform 📊

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-Dynamic_Charts-3f4f75?logo=plotly)](https://plotly.com)
[![Testing](https://img.shields.io/badge/Playwright-Automated_QA-2EAD33?logo=playwright)](https://playwright.dev)

A Python data analytics platform that ingests, profiles, and visualizes uploaded CSV datasets without hardcoded column dependencies.

---

## 🌟 Key Features

### 1. Type Inference Engine
- Parses datasets and identifies columns as `Numeric`, `Categorical`, `Boolean`, or `Datetime`.
- Generates a dataset profile detailing memory usage, row/column counts, missing values, and duplicates.

### 2. Interactive Dashboard
- **KPIs**: Calculates summary statistics based on the uploaded data.
- **Visualizations**: Renders Plotly charts depending on the data type (e.g., Pie charts for low-cardinality categories, Histograms for distributions).
- **Correlation Mapping**: Builds a Pearson correlation heatmap if numeric columns are detected.

### 3. Filtering System
- Generates sidebar controls based on inferred types:
  - Multi-select dropdowns for categorical data.
  - Date range pickers for chronologies.
  - Min/Max sliders for numeric data.
- The dashboard updates in real-time.

### 4. Data Quality Module
- Exposes anomalies using the Interquartile Range method for Outlier Detection.
- Visualizes missing data patterns using a heatmap.
- Highlights null counts and duplicate counts.

### 5. Built-in Demo Environment
- Contains a hardcoded Demo Dashboard as the default option to demonstrate domain-specific KPIs and custom joins using Pandas.

---

## 🛠️ Technologies Used

| Category | Technology | Purpose |
|----------|------------|---------|
| **Core** | Python 3.10+ | Application logic |
| **Data Engine** | Pandas, NumPy | Data manipulation and statistical aggregation |
| **Frontend** | Streamlit | UI and routing |
| **Visualization**| Plotly Express | Interactive charting |
| **Testing** | Playwright, Pytest | UI automation and testing |

---

## 📂 Project Structure

```text
├── app.py                      # Main application entry point & router
├── views/
│   ├── demo_dashboard.py       # Legacy Demo Dashboard
│   ├── dashboard.py            # KPI & Visualization engine
│   ├── overview.py             # Dataset preview & schema inspector
│   └── data_quality.py         # Missing values, outliers, & heatmaps
├── scripts/
│   ├── qa_upload.py            # Playwright QA test suite
│   └── qa_e2e_final.py         # End-to-end test suite
├── utils/
│   ├── detector.py             # Column type profiling
│   ├── statistics.py           # Statistical aggregations
│   ├── filters.py              # UI filter generators
│   └── dynamic_charts.py       # Plotly chart routing
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Installation & Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ShivShah018/swiftdash-ops-analytics.git
   cd swiftdash-ops-analytics
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the platform:**
   ```bash
   streamlit run app.py
   ```
   *The platform will start locally at `http://localhost:8501`*

---

## 🧪 Automated Testing

The project uses **Playwright** for UI testing to ensure the engine handles edge-case datasets correctly.

Run the test suite:
```bash
playwright install
python scripts/qa_e2e_final.py
```

---

## 🔮 Future Improvements

- Automatic K-Means clustering for unlabelled datasets.
- PDF report generation of the active dashboard state.
- Connect directly to PostgreSQL/MySQL instead of flat CSV files.
- UI controls to drop columns and fill missing values.
