# Contributing to SwiftDash

Thank you for your interest in contributing!

## Local Setup

1. Fork the Project
2. Clone your fork:
   ```bash
   git clone https://github.com/ShivShah018/swiftdash-ops-analytics.git
   cd swiftdash-ops-analytics
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```
5. Run automated QA:
   ```bash
   playwright install
   python scripts/qa_e2e_final.py
   ```

## Before Committing

- Ensure your code follows PEP-8 style guidelines.
- Test your changes thoroughly.
- Do not check in large datasets directly.
