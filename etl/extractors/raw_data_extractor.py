import sqlite3
import pandas as pd
from pathlib import Path

class RawDataExtractor:
    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.db_path = project_root / "data" / "vehicles_raw.db"
        else:
            self.db_path = Path(db_path)
    
    def extract_all_vehicles(self) -> pd.DataFrame:
        """Extract all vehicle data from raw database"""
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT * FROM vehicles"
            return pd.read_sql_query(query, conn)
    
    def extract_recent_vehicles(self, hours: int = 24) -> pd.DataFrame:
        """Extract vehicles scraped in the last N hours"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
            SELECT * FROM vehicles 
            WHERE datetime(scraped_at) >= datetime('now', '-{} hours')
            """.format(hours)
            return pd.read_sql_query(query, conn)