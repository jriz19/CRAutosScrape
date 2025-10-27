#!/usr/bin/env python3
"""
ETL Runner Script
Run this script to process raw vehicle data into clean, analysis-ready format
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from etl.pipelines.vehicle_etl_pipeline import VehicleETLPipeline

def main():
    """Run the ETL pipeline"""
    print("Starting Vehicle ETL Pipeline...")
    print("=" * 50)
    
    try:
        # Initialize and run pipeline
        pipeline = VehicleETLPipeline()
        stats = pipeline.run_full_pipeline()
        
        print("\n" + "=" * 50)
        print("ETL Pipeline Completed Successfully!")
        print(f"Total records processed: {stats['total_records']}")
        print(f"Records with price issues: {stats['price_issues']}")
        
        print("\nData Quality Summary:")
        for field, percentage in stats['missing_percentages'].items():
            print(f"  {field.replace('_', ' ').title()}: {percentage:.1f}% missing")
        
        print(f"\nClean database location: {project_root}/data/vehicles_clean.db")
        
    except Exception as e:
        print(f"ETL Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()