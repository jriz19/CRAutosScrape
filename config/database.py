from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Database paths
RAW_DATABASE_PATH = PROJECT_ROOT / "data" / "vehicles_raw.db"
CLEAN_DATABASE_PATH = PROJECT_ROOT / "data" / "vehicles_clean.db"

# Data directories
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
JSON_DATA_DIR = RAW_DATA_DIR / "json"
CSV_DATA_DIR = RAW_DATA_DIR / "csv"
ARCHIVE_DATA_DIR = RAW_DATA_DIR / "archive"

# ETL configuration
ETL_CONFIG = {
    'batch_size': 1000,
    'max_retries': 3,
    'timeout_seconds': 300,
    'log_level': 'INFO'
}

# Data quality thresholds
QUALITY_THRESHOLDS = {
    'max_missing_percentage': 50.0,
    'min_year': 1950,
    'max_year': 2026,
    'max_mileage': 500000,
    'min_engine_cc': 500,
    'max_engine_cc': 6000,
    'min_exchange_rate': 400,
    'max_exchange_rate': 600
}