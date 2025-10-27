# 🚗 Car Market Intelligence Platform

AI-powered automotive market analytics platform built in 4 hours using Amazon Q Developer. Complete data pipeline from web scraping to ML-driven insights for Costa Rica's car market.

## 🎯 Problem Solved

My brother-in-law was car shopping and frustrated by the lack of market intelligence - no way to know fair prices, find good deals, or make data-driven decisions. I built this platform to solve that problem at scale.

## ⚡ Built with AI in 4 Hours

This entire system was developed in a single afternoon using AI assistance:
- **Human role**: Problem definition, business logic, strategic direction
- **AI role**: Code implementation, technical architecture, optimization
- **Result**: Production-ready platform with 89.7% ML accuracy

## 🏗️ Architecture

```
Web Scraping → ETL Pipeline → ML Models → Interactive Dashboards
     ↓              ↓            ↓              ↓
Raw Vehicle Data → Clean Data → Price Predictions → Business Insights
```

## 🚀 Features

- **Web Scraper**: Extracts vehicle data from CRAutos.com
- **ETL Pipeline**: Cleans and transforms raw data
- **ML Engine**: 5 algorithms compared, Gradient Boosting wins (89.7% R²)
- **Dual Dashboards**: Technical analytics + Business intelligence
- **Smart Deal Detection**: ML-powered underpriced vehicle identification
- **Real-time Insights**: Market trends, brand analysis, price predictions

## 📊 Key Insights Discovered

- Toyota leads with 14.7% market share
- Luxury segment commands 80.7% price premium
- Top price predictors: age (35%), brand value (25%), engine size (15%)
- 80% missing mileage data identified as critical improvement area

## 🛠️ Tech Stack

- **Python**: Core language
- **Scrapy**: Web scraping framework
- **SQLite**: Data storage
- **Scikit-learn**: Machine learning
- **Streamlit**: Interactive dashboards
- **Pandas**: Data processing

## 🚀 Quick Start

1. **Clone & Install**
   ```bash
   git clone https://github.com/jriz19/CRAutosScrape.git
   cd CRAutosScrape
   pip install -r requirements.txt
   ```

2. **Run Pipeline**
   ```bash
   # Scrape data
   python scrapers/run_scraper.py
   
   # Process data
   python etl/run_etl.py
   
   # Run ML analysis
   python analytics/notebooks/run_analysis.py
   
   # Launch dashboards
   streamlit run analytics/dashboard/streamlit_app.py
   ```

## 📈 Results

The platform identifies deals like a 2018 BMW X3 listed at $29,900 (predicted value: $32,000+) and provides:
- Market price benchmarking
- Brand depreciation analysis
- Regional pricing insights
- Direct seller contact integration

## 🤖 AI Development Workflow

This project demonstrates the power of AI-assisted development:
- **Context Management**: Rich project context fed to AI
- **Iterative Development**: Real data feedback loops
- **Rapid Prototyping**: Hours instead of weeks
- **Quality Output**: Production-ready code with proper architecture

## 📁 Project Structure

```
├── scrapers/          # Web scraping modules
├── etl/              # Data processing pipeline
├── analytics/        # ML models and dashboards
├── config/           # Configuration files
└── SETUP.md         # Detailed setup guide
```

## 🔮 Future Improvements

- Fix mileage extraction (80% missing data) - valuable feature for price prediction
- Implement mobile-responsive UI

## 📄 License

Feel free to use and modify

---

**Built with ❤️ and AI assistance in Costa Rica**
