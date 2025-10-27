# Data Pipeline Project

A complete data pipeline from web scraping to analytics and ML predictions.

## Project Structure

```
├── scrapers/           # Web scraping modules
│   ├── spiders/       # Scrapy spiders
│   ├── utils/         # Scraping utilities
│   └── data_models/   # Data models
├── raw_data/          # Raw scraped data storage
│   ├── json/          # JSON files
│   ├── csv/           # CSV files
│   └── archive/       # Archived data
├── etl/               # ETL processes
│   ├── extractors/    # Data extraction
│   ├── transformers/  # Data transformation
│   ├── loaders/       # Data loading
│   ├── staging/       # Staging tables
│   └── pipelines/     # ETL pipelines
├── analytics/         # Analytics and ML
│   ├── models/        # Analytics models
│   ├── notebooks/     # Jupyter notebooks
│   ├── reports/       # Generated reports
│   ├── ml_models/     # Trained ML models
│   └── predictions/   # Prediction outputs
├── config/            # Configuration files
├── logs/              # Application logs
└── tests/             # Unit tests
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. Run pipeline:
   ```bash
   python main.py scrape --scraper example
   python main.py etl --pipeline example
   python main.py ml --model example --action train
   ```

## Usage

- **Scraping**: Extend `BaseScraper` for new scrapers
- **ETL**: Extend `BaseETL` for new pipelines  
- **ML**: Extend `BaseMLModel` for new models