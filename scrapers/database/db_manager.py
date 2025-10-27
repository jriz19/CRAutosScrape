import sqlite3
import json
from pathlib import Path
from typing import List, Dict
import logging

class DatabaseManager:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use centralized data directory
            project_root = Path(__file__).parent.parent.parent
            self.db_path = project_root / "data" / "vehicles_raw.db"
        else:
            self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize database with vehicle schema"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Create vehicles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    vehicle_id TEXT,
                    brand TEXT,
                    model TEXT,
                    year INTEGER,
                    price_colones INTEGER,
                    price_usd INTEGER,
                    mileage INTEGER,
                    fuel_type TEXT,
                    transmission TEXT,
                    engine_cc INTEGER,
                    doors INTEGER,
                    style TEXT,
                    color_exterior TEXT,
                    color_interior TEXT,
                    location TEXT,
                    province TEXT,
                    seller_phone TEXT,
                    seller_whatsapp TEXT,
                    description TEXT,
                    features TEXT,
                    images TEXT,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create scraping log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraping_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    status TEXT,
                    error_message TEXT,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    def insert_vehicle(self, vehicle_data: Dict) -> bool:
        """Insert vehicle data into database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Insert or update vehicle
                cursor.execute('''
                    INSERT OR REPLACE INTO vehicles (
                        url, vehicle_id, brand, model, year, price_colones, price_usd,
                        mileage, fuel_type, transmission, engine_cc, doors, style,
                        color_exterior, color_interior, location, province,
                        seller_phone, seller_whatsapp, description, features, images,
                        scraped_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vehicle_data.get('url'),
                    vehicle_data.get('vehicle_id'),
                    vehicle_data.get('brand'),
                    vehicle_data.get('model'),
                    vehicle_data.get('year'),
                    vehicle_data.get('price_colones'),
                    vehicle_data.get('price_usd'),
                    vehicle_data.get('mileage'),
                    vehicle_data.get('fuel_type'),
                    vehicle_data.get('transmission'),
                    vehicle_data.get('engine_cc'),
                    vehicle_data.get('doors'),
                    vehicle_data.get('style'),
                    vehicle_data.get('color_exterior'),
                    vehicle_data.get('color_interior'),
                    vehicle_data.get('location'),
                    vehicle_data.get('province'),
                    vehicle_data.get('seller_phone'),
                    vehicle_data.get('seller_whatsapp'),
                    vehicle_data.get('description'),
                    vehicle_data.get('features'),
                    vehicle_data.get('images'),
                    vehicle_data.get('scraped_at')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error inserting vehicle: {e}")
            return False
    
    def load_json_files_to_db(self, json_dir: str = "raw_data/json"):
        """Load all JSON files from directory into database"""
        json_path = Path(json_dir)
        loaded = 0
        errors = 0
        
        for json_file in json_path.glob("crautos_*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    vehicle_data = json.load(f)
                
                if self.insert_vehicle(vehicle_data):
                    loaded += 1
                    self.logger.info(f"Loaded {vehicle_data.get('brand')} {vehicle_data.get('model')}")
                else:
                    errors += 1
                    
            except Exception as e:
                self.logger.error(f"Error loading {json_file}: {e}")
                errors += 1
        
        return {'loaded': loaded, 'errors': errors}
    
    def get_vehicle_stats(self) -> Dict:
        """Get basic statistics from database"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Total vehicles
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            total = cursor.fetchone()[0]
            
            # By brand
            cursor.execute("SELECT brand, COUNT(*) FROM vehicles GROUP BY brand ORDER BY COUNT(*) DESC LIMIT 5")
            top_brands = cursor.fetchall()
            
            # Price range
            cursor.execute("SELECT MIN(price_usd), MAX(price_usd), AVG(price_usd) FROM vehicles WHERE price_usd > 0")
            price_stats = cursor.fetchone()
            
            return {
                'total_vehicles': total,
                'top_brands': top_brands,
                'price_range': {
                    'min_usd': price_stats[0],
                    'max_usd': price_stats[1],
                    'avg_usd': round(price_stats[2], 2) if price_stats[2] else 0
                }
            }