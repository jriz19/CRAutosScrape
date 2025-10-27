#!/usr/bin/env python3
"""
ETL Verification Script
Compare raw vs clean data to show improvements
"""

import sqlite3
import pandas as pd
from pathlib import Path

def compare_databases():
    """Compare raw and clean databases"""
    project_root = Path(__file__).parent.parent
    raw_db = project_root / "data" / "vehicles_raw.db"
    clean_db = project_root / "data" / "vehicles_clean.db"
    
    print("ETL Data Quality Comparison")
    print("=" * 50)
    
    # Raw data stats
    with sqlite3.connect(raw_db) as conn:
        raw_df = pd.read_sql_query("SELECT * FROM vehicles", conn)
    
    # Clean data stats  
    with sqlite3.connect(clean_db) as conn:
        clean_df = pd.read_sql_query("SELECT * FROM vehicles_clean", conn)
    
    print(f"Raw database records: {len(raw_df)}")
    print(f"Clean database records: {len(clean_df)}")
    print(f"Raw database columns: {len(raw_df.columns)}")
    print(f"Clean database columns: {len(clean_df.columns)}")
    
    print("\nColumns removed in cleaning:")
    removed_cols = set(raw_df.columns) - set(clean_df.columns)
    for col in removed_cols:
        if col not in ['id']:  # id might be different
            print(f"  - {col}")
    
    print("\nColumns added in cleaning:")
    added_cols = set(clean_df.columns) - set(raw_df.columns)
    for col in added_cols:
        print(f"  + {col}")
    
    print("\nData quality improvements:")
    
    # Check brand standardization
    if 'brand' in raw_df.columns and 'brand' in clean_df.columns:
        raw_brands = raw_df['brand'].nunique()
        clean_brands = clean_df['brand'].nunique()
        print(f"  Brand standardization: {raw_brands} -> {clean_brands} unique brands")
    
    # Check missing data handling
    common_cols = ['model', 'fuel_type', 'mileage', 'engine_cc']
    for col in common_cols:
        if col in raw_df.columns and col in clean_df.columns:
            raw_missing = (raw_df[col].isnull() | (raw_df[col] == '')).sum()
            clean_missing = clean_df[col].isnull().sum()
            raw_pct = raw_missing / len(raw_df) * 100
            clean_pct = clean_missing / len(clean_df) * 100
            print(f"  {col} missing: {raw_pct:.1f}% -> {clean_pct:.1f}%")
    
    print("\nNew derived features:")
    derived_features = ['vehicle_age', 'price_per_year', 'is_luxury', 'exchange_rate']
    for feature in derived_features:
        if feature in clean_df.columns:
            non_null = clean_df[feature].notna().sum()
            print(f"  {feature}: {non_null} records with values")
    
    print(f"\nClean database size: {clean_db.stat().st_size / 1024:.1f} KB")
    print(f"Raw database size: {raw_db.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    compare_databases()