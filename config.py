from pathlib import Path
import os

# Base directory for the project
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) if "utils" in __file__ else Path(os.path.dirname(os.path.abspath(__file__)))

# Data Directories
DATA_DIR = BASE_DIR / "data"
CLEAN_DIR = DATA_DIR / "cleaned"
PROC_DIR = DATA_DIR / "processed"

# Business Logic Constants
ON_TIME_CUTOFF_MINUTES = 30
