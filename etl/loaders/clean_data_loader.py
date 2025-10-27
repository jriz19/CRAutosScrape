import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

class CleanDataLoader:
    def __init__(self, db_path: str = None):
        if db_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.db_path = project_root / "data" / "vehicles_clean.db"
        else:
            self.db_path = Path(db_path)
    
    def create_clean_schema(self):
        """Create optimized schema for clean data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Drop existing table if it exists
            cursor.execute("DROP TABLE IF EXISTS vehicles_clean")
            
            # Create clean vehicles table
            cursor.execute("""
                CREATE TABLE vehicles_clean (
                    id INTEGER PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    vehicle_id TEXT UNIQUE NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT,
                    year INTEGER,
                    price_colones INTEGER NOT NULL,
                    price_usd INTEGER NOT NULL,
                    mileage REAL,
                    fuel_type TEXT,
                    transmission TEXT,
                    engine_cc REAL,
                    color_exterior TEXT,
                    color_interior TEXT,
                    seller_phone TEXT,
                    seller_whatsapp TEXT,
                    description TEXT,
                    images TEXT,
                    exchange_rate REAL,
                    price_flag BOOLEAN,
                    vehicle_age INTEGER,
                    price_per_year REAL,
                    is_luxury BOOLEAN,
                    scraped_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX idx_brand ON vehicles_clean(brand)")
            cursor.execute("CREATE INDEX idx_year ON vehicles_clean(year)")
            cursor.execute("CREATE INDEX idx_price_usd ON vehicles_clean(price_usd)")
            cursor.execute("CREATE INDEX idx_fuel_type ON vehicles_clean(fuel_type)")
            cursor.execute("CREATE INDEX idx_is_luxury ON vehicles_clean(is_luxury)")
            cursor.execute("CREATE INDEX idx_scraped_at ON vehicles_clean(scraped_at)")
            
            conn.commit()
    
    def load_clean_data(self, df: pd.DataFrame, mode: str = 'replace'):
        """Load cleaned data to database"""
        self.create_clean_schema()
        
        with sqlite3.connect(self.db_path) as conn:
            if mode == 'replace':
                df.to_sql('vehicles_clean', conn, if_exists='replace', index=False)
            elif mode == 'append':
                df.to_sql('vehicles_clean', conn, if_exists='append', index=False)
    
    def get_data_quality_stats(self) -> dict:
        """Get data quality statistics for the clean database"""
        with sqlite3.connect(self.db_path) as conn:
            stats = {}
            
            # Basic counts
            stats['total_records'] = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM vehicles_clean", conn
            ).iloc[0]['count']
            
            # Missing data percentages
            missing_query = """
                SELECT 
                    SUM(CASE WHEN model IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as model_missing,
                    SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as year_missing,
                    SUM(CASE WHEN mileage IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as mileage_missing,
                    SUM(CASE WHEN fuel_type IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as fuel_missing,
                    SUM(CASE WHEN engine_cc IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as engine_missing
                FROM vehicles_clean
            """
            stats['missing_percentages'] = pd.read_sql_query(missing_query, conn).to_dict('records')[0]
            
            # Price flags
            stats['price_issues'] = pd.read_sql_query(
                "SELECT COUNT(*) as count FROM vehicles_clean WHERE price_flag = 1", conn
            ).iloc[0]['count']
            
            # Brand distribution
            stats['brand_distribution'] = pd.read_sql_query(
                "SELECT brand, COUNT(*) as count FROM vehicles_clean GROUP BY brand ORDER BY count DESC LIMIT 10", 
                conn
            ).to_dict('records')
            
            return stats