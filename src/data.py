from pathlib import Path
import pandas as pd


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Raw data directory
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def load_data(filename: str) -> pd.DataFrame:
    """Load a CSV file from the raw data directory."""
    
    file_path = RAW_DATA_DIR / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    
    return pd.read_csv(file_path)