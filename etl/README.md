# ETL Pipeline

This ETL pipeline processes raw vehicle data from web scraping into clean, analysis-ready format.

## Overview

The pipeline consists of three main stages:
1. **Extract**: Read raw data from `data/vehicles_raw.db`
2. **Transform**: Clean, validate, and enrich the data
3. **Load**: Store clean data in `data/vehicles_clean.db`

## Data Quality Issues Addressed

Based on the analysis reports, the pipeline handles:

### Missing Data
- **doors**: 100% missing → Column removed
- **style**: 100% missing → Column removed  
- **location**: 100% missing → Column removed
- **province**: 100% missing → Column removed
- **features**: 100% missing → Column removed
- **model**: 0.8% missing → Empty strings converted to NULL
- **mileage**: 1.67% missing → Extreme values (>500k) set to NULL
- **fuel_type**: 0.5% missing → Empty strings converted to NULL
- **engine_cc**: 0.5% missing → Outliers (<500cc or >6000cc) set to NULL

### Data Standardization
- **Brand names**: Standardized case and spelling (BMW, Mercedes-Benz, etc.)
- **Fuel types**: Spanish to English (Gasolina → Gasoline, Híbrido → Hybrid)
- **Colors**: Spanish to English with consistent formatting
- **Years**: Invalid years (<1950 or >2026) set to NULL
- **Phone numbers**: Standardized format

### Data Enrichment
- **Vehicle age**: Calculated from year
- **Price per year**: Depreciation indicator
- **Luxury brand flag**: Boolean for premium brands
- **Exchange rate**: USD/Colones ratio with validation
- **Price flags**: Suspicious exchange rates flagged

## Usage

### Run Full ETL Pipeline
```bash
# Using main.py
python main.py etl --pipeline vehicle --mode full

# Using direct script
python etl/run_etl.py

# Using ETL runner
cd etl && python run_etl.py
```

### Run Incremental ETL
```bash
# Process last 24 hours of data
python main.py etl --pipeline vehicle --mode incremental --hours 24
```

## Database Schema

### Raw Database (`data/vehicles_raw.db`)
- Contains scraped data with original structure
- Includes all fields from web scraping
- May contain data quality issues

### Clean Database (`data/vehicles_clean.db`)
- Optimized schema with cleaned data
- Indexed for better query performance
- Includes derived features for analysis
- Tracks data quality metrics

### Key Improvements in Clean DB
- Removed empty columns (doors, style, location, province, features)
- Added data quality flags (price_flag)
- Added derived features (vehicle_age, price_per_year, is_luxury)
- Proper data types and constraints
- Performance indexes on key fields

## Data Quality Monitoring

The pipeline generates comprehensive quality reports including:
- Missing data percentages
- Validation errors and warnings
- Price consistency checks
- Data distribution statistics
- Processing timestamps

## Files Structure

```
etl/
├── extractors/
│   └── raw_data_extractor.py     # Extract from raw database
├── transformers/
│   ├── data_cleaner.py           # Main cleaning logic
│   └── data_validator.py         # Data validation rules
├── loaders/
│   └── clean_data_loader.py      # Load to clean database
├── pipelines/
│   └── vehicle_etl_pipeline.py   # Main ETL orchestrator
├── docs/                         # Analysis reports
├── run_etl.py                    # Simple ETL runner
└── README.md                     # This file
```

## Configuration

Database paths and ETL settings are configured in:
- `config/database.py` - Database paths and connections
- `config/settings.py` - General application settings

## Logging

ETL processes generate detailed logs in the `logs/` directory with:
- Processing timestamps
- Record counts
- Data quality metrics
- Error messages and warnings

## Next Steps

After running the ETL pipeline, the clean database is ready for:
1. **Analytics**: Exploratory data analysis and reporting
2. **Machine Learning**: Feature engineering and model training
3. **Visualization**: Dashboard creation and insights
4. **API**: Serving clean data through web services