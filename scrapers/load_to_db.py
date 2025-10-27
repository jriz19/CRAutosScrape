#!/usr/bin/env python3
"""
Load scraped JSON data into SQLite database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    
    print("Loading scraped data to database...")
    
    # Initialize database
    db = DatabaseManager()
    
    # Load JSON files
    results = db.load_json_files_to_db("../raw_data/json")
    
    print(f"Loaded {results['loaded']} vehicles, {results['errors']} errors")
    
    # Show stats
    stats = db.get_vehicle_stats()
    print(f"\nDatabase Statistics:")
    print(f"Total vehicles: {stats['total_vehicles']}")
    print(f"Top brands: {stats['top_brands']}")
    print(f"Price range: ${stats['price_range']['min_usd']} - ${stats['price_range']['max_usd']} (avg: ${stats['price_range']['avg_usd']})")

if __name__ == "__main__":
    main()