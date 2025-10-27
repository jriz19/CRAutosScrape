#!/usr/bin/env python3
"""
Vehicle Market Analysis Script
Scientific analysis of clean vehicle data for ML model development
"""

import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
import warnings
import json
warnings.filterwarnings('ignore')

# Statistical Analysis
from scipy import stats
from scipy.stats import pearsonr, spearmanr

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.feature_selection import mutual_info_regression

# Visualization (optional)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

def load_clean_data():
    """Load clean data from database"""
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / "data" / "vehicles_clean.db"
    
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query("SELECT * FROM vehicles_clean", conn)
    
    print(f"Loaded {len(df)} records from clean database")
    return df, project_root

def engineer_features(df):
    """Create advanced features for ML"""
    df_features = df.copy()
    
    # Create new features
    df_features['log_price'] = np.log(df_features['price_usd'])
    df_features['price_per_cc'] = df_features['price_usd'] / df_features['engine_cc']
    df_features['age_squared'] = df_features['vehicle_age'] ** 2
    df_features['mileage_per_year'] = df_features['mileage'] / (df_features['vehicle_age'] + 1)
    df_features['is_new'] = (df_features['vehicle_age'] <= 2).astype(int)
    df_features['is_vintage'] = (df_features['vehicle_age'] >= 20).astype(int)
    
    # Brand value encoding
    brand_value = df_features.groupby('brand')['price_usd'].mean().to_dict()
    df_features['brand_value_score'] = df_features['brand'].map(brand_value)
    
    # Model popularity
    model_popularity = df_features['model'].value_counts().to_dict()
    df_features['model_popularity'] = df_features['model'].map(model_popularity).fillna(1)
    
    print(f"Created {len(df_features.columns) - len(df.columns)} new features")
    return df_features

def prepare_ml_data(df):
    """Prepare data for machine learning"""
    ml_df = df.copy()
    
    # Select features
    numeric_features = ['year', 'engine_cc', 'vehicle_age', 'brand_value_score', 
                       'model_popularity', 'price_per_year', 'exchange_rate']
    categorical_features = ['fuel_type', 'transmission', 'is_luxury']
    
    # Filter available features
    numeric_features = [f for f in numeric_features if f in ml_df.columns]
    categorical_features = [f for f in categorical_features if f in ml_df.columns]
    
    # Handle missing values and infinite values
    for col in numeric_features:
        ml_df[col] = ml_df[col].fillna(ml_df[col].median())
        # Replace infinite values
        ml_df[col] = ml_df[col].replace([np.inf, -np.inf], ml_df[col].median())
    
    for col in categorical_features:
        ml_df[col] = ml_df[col].fillna('Unknown')
    
    # One-hot encode
    ml_df_encoded = pd.get_dummies(ml_df[numeric_features + categorical_features], 
                                  columns=categorical_features, drop_first=True)
    
    return ml_df_encoded, ml_df['price_usd']

def evaluate_models(X, y):
    """Evaluate multiple ML models"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Linear Regression': (LinearRegression(), True),
        'Ridge Regression': (Ridge(alpha=1.0), True),
        'Lasso Regression': (Lasso(alpha=1.0), True),
        'Random Forest': (RandomForestRegressor(n_estimators=100, random_state=42), False),
        'Gradient Boosting': (GradientBoostingRegressor(n_estimators=100, random_state=42), False)
    }
    
    results = []
    best_model = None
    best_score = -np.inf
    
    for name, (model, use_scaling) in models.items():
        # Choose data
        X_tr = X_train_scaled if use_scaling else X_train
        X_te = X_test_scaled if use_scaling else X_test
        
        # Fit and predict
        model.fit(X_tr, y_train)
        y_pred = model.predict(X_te)
        
        # Metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_tr, y_train, cv=5, scoring='r2')
        
        results.append({
            'model': name,
            'test_r2': r2,
            'test_mae': mae,
            'test_rmse': rmse,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std()
        })
        
        if r2 > best_score:
            best_score = r2
            best_model = (name, model, X_te, y_test, y_pred)
    
    return results, best_model

def analyze_feature_importance(X, y):
    """Analyze feature importance"""
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X, y)
    
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    # Mutual information
    mi_scores = mutual_info_regression(X, y, random_state=42)
    mi_df = pd.DataFrame({
        'feature': X.columns,
        'mutual_info': mi_scores
    }).sort_values('mutual_info', ascending=False)
    
    return feature_importance, mi_df

def market_analysis(df):
    """Perform market structure analysis"""
    analysis = {
        'total_vehicles': len(df),
        'price_range': {
            'min': float(df['price_usd'].min()),
            'max': float(df['price_usd'].max()),
            'median': float(df['price_usd'].median()),
            'mean': float(df['price_usd'].mean())
        },
        'market_leader': df['brand'].value_counts().index[0],
        'market_share': float(df['brand'].value_counts().iloc[0] / len(df) * 100),
        'luxury_percentage': float(df['is_luxury'].sum() / len(df) * 100),
        'automatic_percentage': float((df['transmission'] == 'Automática').sum() / len(df) * 100),
        'median_age': float(df['vehicle_age'].median()),
        'top_brands': df['brand'].value_counts().head(5).to_dict()
    }
    
    # Luxury premium
    luxury_median = df[df['is_luxury'] == True]['price_usd'].median()
    regular_median = df[df['is_luxury'] == False]['price_usd'].median()
    analysis['luxury_premium'] = float((luxury_median / regular_median - 1) * 100)
    
    return analysis

def generate_recommendations(results, feature_importance, market_analysis, best_model_info):
    """Generate comprehensive recommendations"""
    best_model_name, _, _, _, _ = best_model_info
    best_result = next(r for r in results if r['model'] == best_model_name)
    
    recommendations = {
        "ml_models": {
            "primary": best_model_name,
            "performance": best_result['test_r2'],
            "mae": best_result['test_mae'],
            "alternative": sorted(results, key=lambda x: x['test_r2'], reverse=True)[1]['model']
        },
        
        "key_features": {
            "most_important": feature_importance.head(5)['feature'].tolist(),
            "top_mutual_info": feature_importance.head(3)['feature'].tolist()
        },
        
        "market_insights": market_analysis,
        
        "dashboard_components": {
            "kpi_cards": ["Total Inventory", "Average Price", "Luxury Percentage", "Market Leader"],
            "visualizations": ["Price Distribution", "Brand Market Share", "Price vs Age", "Feature Importance"],
            "prediction_tool": ["Input Form", "Price Prediction", "Confidence Interval", "Similar Vehicles"],
            "analytics": ["Market Trends", "Brand Performance", "Depreciation Analysis", "Inventory Insights"]
        },
        
        "data_improvements": {
            "high_priority": ["Collect mileage data (71% missing)", "Standardize model names"],
            "medium_priority": ["Engine specifications", "Vehicle condition", "Location data"],
            "enhancements": ["Service history", "Accident records", "Market timing"]
        }
    }
    
    return recommendations

def main():
    """Run complete analysis"""
    print("Starting Vehicle Market Analysis...")
    print("=" * 50)
    
    # Load data
    df, project_root = load_clean_data()
    
    # Feature engineering
    df_features = engineer_features(df)
    
    # Prepare ML data
    X, y = prepare_ml_data(df_features)
    print(f"Prepared {X.shape[1]} features for ML")
    
    # Evaluate models
    print("\nEvaluating ML models...")
    results, best_model_info = evaluate_models(X, y)
    
    # Feature importance
    print("Analyzing feature importance...")
    feature_importance, mi_df = analyze_feature_importance(X, y)
    
    # Market analysis
    print("Performing market analysis...")
    market_stats = market_analysis(df_features)
    
    # Generate recommendations
    print("Generating recommendations...")
    recommendations = generate_recommendations(results, feature_importance, market_stats, best_model_info)
    
    # Display results
    print("\n" + "=" * 50)
    print("ANALYSIS RESULTS")
    print("=" * 50)
    
    print(f"\nBest Model: {recommendations['ml_models']['primary']}")
    print(f"   Accuracy (R²): {recommendations['ml_models']['performance']:.4f}")
    print(f"   Mean Error: ${recommendations['ml_models']['mae']:,.0f}")
    
    print(f"\nMarket Overview:")
    print(f"   Total Vehicles: {market_stats['total_vehicles']:,}")
    print(f"   Price Range: ${market_stats['price_range']['min']:,.0f} - ${market_stats['price_range']['max']:,.0f}")
    print(f"   Market Leader: {market_stats['market_leader']} ({market_stats['market_share']:.1f}%)")
    print(f"   Luxury Premium: {market_stats['luxury_premium']:.1f}%")
    
    print(f"\nTop Predictive Features:")
    for i, feature in enumerate(recommendations['key_features']['most_important'], 1):
        print(f"   {i}. {feature}")
    
    # Save results
    reports_dir = project_root / "analytics" / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Save recommendations
    with open(reports_dir / "ml_recommendations.json", 'w') as f:
        json.dump(recommendations, f, indent=2, default=str)
    
    # Save model results
    results_df = pd.DataFrame(results)
    results_df.to_csv(reports_dir / "model_comparison.csv", index=False)
    
    # Save feature importance
    feature_importance.to_csv(reports_dir / "feature_importance.csv", index=False)
    
    print(f"\nResults saved to: {reports_dir}")
    print("\nAnalysis Complete! Ready for Streamlit Dashboard Development.")
    
    return recommendations

if __name__ == "__main__":
    recommendations = main()