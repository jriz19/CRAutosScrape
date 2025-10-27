# Vehicle Market Intelligence Dashboard

Interactive Streamlit dashboard for Costa Rica vehicle market analysis and price prediction.

## Features

### 📊 Market Overview
- **KPI Cards**: Total inventory, average price, luxury segment, market leader
- **Price Distribution**: Histogram and box plots by brand
- **Market Share**: Interactive pie chart of top brands
- **Price vs Age**: Scatter plot with trend analysis
- **Feature Importance**: ML model feature rankings

### 🎯 Price Prediction Tool
- **Interactive Form**: Input vehicle specifications
- **Real-time Prediction**: Instant price estimates
- **Confidence Intervals**: Prediction uncertainty ranges
- **Market Position**: Percentile ranking
- **Similar Vehicles**: Comparable listings

### 📈 Brand Analysis
- **Performance Table**: Volume, pricing, and age metrics
- **Volume vs Price**: Scatter plot analysis
- **Market Positioning**: Brand comparison matrix

### 🤖 ML Insights
- **Model Performance**: Accuracy metrics and alternatives
- **Feature Importance**: Top predictive variables
- **Data Quality**: Improvement recommendations

## Quick Start

### Launch Dashboard
```bash
# Method 1: Direct Streamlit
streamlit run analytics/dashboard/streamlit_app.py

# Method 2: Using runner script
python analytics/dashboard/run_dashboard.py

# Method 3: From project root
cd analytics/dashboard && streamlit run streamlit_app.py
```

### Access Dashboard
- **URL**: http://localhost:8501
- **Auto-opens**: In default web browser
- **Mobile**: Responsive design works on mobile devices

## Dashboard Components

### Sidebar Navigation
- **Page Selection**: Market Overview, Price Prediction, Brand Analysis, ML Insights
- **Dynamic Filters**: Price range, brand selection
- **Record Counter**: Shows filtered vs total records

### Interactive Features
- **Real-time Filtering**: Instant chart updates
- **Hover Details**: Rich tooltips on charts
- **Responsive Layout**: Adapts to screen size
- **Export Options**: Download charts and data

## Technical Architecture

### Data Pipeline
```
Raw Database → ETL Pipeline → Clean Database → Dashboard
```

### Key Dependencies
- **Streamlit**: Web framework
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **SQLite**: Database connection
- **NumPy**: Numerical computations

### Performance Optimizations
- **Caching**: `@st.cache_data` for data loading
- **Lazy Loading**: Charts render on demand
- **Efficient Queries**: Optimized database access
- **Memory Management**: Minimal data duplication

## ML Integration

### Prediction Model
- **Algorithm**: Gradient Boosting (89.7% accuracy)
- **Features**: price_per_year, brand_value_score, engine_cc, year, vehicle_age
- **Error Rate**: $4,357 mean absolute error
- **Confidence**: 85-115% prediction intervals

### Feature Engineering
- **Brand Value Score**: Average price by brand
- **Vehicle Age**: Current year - manufacture year
- **Price Per Year**: Depreciation indicator
- **Luxury Flag**: Premium brand classification

## Business Intelligence

### Market Insights
- **Total Vehicles**: 600 active listings
- **Price Range**: $5,200 - $205,000
- **Market Leader**: Toyota (14.7% share)
- **Luxury Premium**: 80.7% price premium
- **Median Age**: 6 years

### Key Findings
- **Automatic Preference**: 26.7% of vehicles
- **Gasoline Dominance**: Primary fuel type
- **Age Impact**: Strong negative correlation with price
- **Brand Premium**: Significant price variations by brand

## Data Quality

### Current Status
- **Complete Records**: 600 vehicles processed
- **Missing Mileage**: 71% (high priority fix)
- **Model Names**: 0.8% missing
- **Engine Data**: 2.8% missing

### Improvement Roadmap
1. **High Priority**: Collect mileage data, standardize model names
2. **Medium Priority**: Engine specifications, vehicle condition, location data
3. **Enhancements**: Service history, accident records, market timing

## Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py
```

### Production Deployment
- **Streamlit Cloud**: Free hosting with GitHub integration
- **Heroku**: Container-based deployment
- **AWS/GCP**: Cloud platform hosting
- **Docker**: Containerized deployment

### Environment Variables
```bash
# Optional configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_THEME_BASE=light
```

## Customization

### Adding New Charts
1. Create chart function in `streamlit_app.py`
2. Add to appropriate page section
3. Update navigation if needed

### New ML Models
1. Train model using `analytics/notebooks/run_analysis.py`
2. Save model artifacts
3. Update prediction function

### Styling
- **CSS**: Custom styles in `.streamlit/config.toml`
- **Themes**: Light/dark mode support
- **Colors**: Brand-consistent color palette

## Troubleshooting

### Common Issues
- **Port Conflict**: Change port with `--server.port 8502`
- **Memory Issues**: Reduce data size or add pagination
- **Slow Loading**: Check database connection and caching

### Performance Tips
- **Filter Data**: Use sidebar filters to reduce dataset size
- **Cache Results**: Leverage Streamlit caching decorators
- **Optimize Queries**: Use efficient SQL queries

## Future Enhancements

### Planned Features
- **Real-time Updates**: Live data refresh
- **Advanced Filters**: More granular filtering options
- **Export Tools**: PDF reports and data downloads
- **User Authentication**: Multi-user access control
- **API Integration**: External data sources

### ML Improvements
- **Ensemble Models**: Combine multiple algorithms
- **Feature Selection**: Automated feature engineering
- **Model Monitoring**: Performance tracking over time
- **A/B Testing**: Model comparison framework