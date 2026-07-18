import pandas as pd
import os

os.makedirs("data/samples/edge_cases", exist_ok=True)

# 1. Empty CSV
pd.DataFrame().to_csv("data/samples/edge_cases/empty.csv", index=False)

# 2. Numeric Only
pd.DataFrame({"A": [1, 2, 3], "B": [4.0, 5.5, 6.1]}).to_csv("data/samples/edge_cases/numeric_only.csv", index=False)

# 3. Categorical Only
pd.DataFrame({"C": ["Apple", "Banana", "Cherry"], "D": ["Red", "Yellow", "Red"]}).to_csv("data/samples/edge_cases/cat_only.csv", index=False)

# 4. Single Column
pd.DataFrame({"Single": [10, 20, 30, 40]}).to_csv("data/samples/edge_cases/single_col.csv", index=False)

# 5. Duplicates
pd.DataFrame({"ID": [1, 1, 2], "Val": [10, 10, 20]}).to_csv("data/samples/edge_cases/duplicates.csv", index=False)

# 6. High Missing
pd.DataFrame({"A": [1, None, None], "B": [None, None, 2]}).to_csv("data/samples/edge_cases/missing.csv", index=False)
