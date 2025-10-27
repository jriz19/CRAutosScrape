# Setup Guide

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CRAutosScrape
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings if needed
   ```

4. **Run the pipeline**

   **Scrape data:**
   ```bash
   python scrapers/run_scraper.py
   ```

   **Process data (ETL):**
   ```bash
   python etl/run_etl.py
   ```

   **Run ML analysis:**
   ```bash
   python analytics/notebooks/run_analysis.py
   ```

   **Launch dashboards:**
   ```bash
   # Technical dashboard (port 8501)
   streamlit run analytics/dashboard/streamlit_app.py

   # Business dashboard (port 8502)
   streamlit run analytics/dashboard/reseller_dashboard.py --server.port 8502
   ```

## Data Flow

1. **Scrapers** → Extract vehicle data from CRAutos.com → `raw_data/json/`
2. **ETL** → Clean and transform data → `data/vehicles_clean.db`
3. **Analytics** → ML models and analysis → `analytics/reports/`
4. **Dashboards** → Interactive visualizations and insights

## Project Structure

- `scrapers/` - Web scraping modules
- `etl/` - Data processing pipeline
- `analytics/` - ML models and analysis
- `config/` - Configuration files
- `sample_data_structure.json` - Expected data format

## Notes

- All actual data files are excluded from git (see `.gitignore`)
- The system requires scraped data to function
- ML models achieve ~90% accuracy in price prediction
- Dashboards provide both technical and business insights