import sqlite3
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import re

class VehicleDataAnalyzer:
    def __init__(self, db_path: str = "../scrapers/vehicles.db"):
        self.db_path = db_path
        self.analysis_results = {}
        
    def load_data(self):
        """Load vehicle data from database"""
        with sqlite3.connect(self.db_path) as conn:
            self.df = pd.read_sql_query("SELECT * FROM vehicles", conn)
        return self.df
    
    def analyze_data_quality(self):
        """Comprehensive data quality analysis"""
        df = self.df
        
        # Basic info
        basic_info = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
        }
        
        # Missing values analysis
        missing_analysis = {}
        for col in df.columns:
            null_count = df[col].isnull().sum()
            empty_strings = (df[col] == '').sum() if df[col].dtype == 'object' else 0
            missing_analysis[col] = {
                'null_count': int(null_count),
                'null_percentage': round(null_count / len(df) * 100, 2),
                'empty_strings': int(empty_strings),
                'total_missing': int(null_count + empty_strings)
            }
        
        # Data type analysis
        dtype_analysis = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        # Unique values analysis
        unique_analysis = {}
        for col in df.columns:
            if df[col].dtype == 'object':
                unique_count = df[col].nunique()
                unique_analysis[col] = {
                    'unique_count': int(unique_count),
                    'sample_values': df[col].dropna().unique()[:10].tolist()
                }
        
        # Numeric columns analysis
        numeric_analysis = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            numeric_analysis[col] = {
                'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                'max': float(df[col].max()) if not pd.isna(df[col].max()) else None,
                'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                'std': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                'outliers_count': int(self._count_outliers(df[col]))
            }
        
        self.analysis_results = {
            'basic_info': basic_info,
            'missing_analysis': missing_analysis,
            'dtype_analysis': dtype_analysis,
            'unique_analysis': unique_analysis,
            'numeric_analysis': numeric_analysis,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return self.analysis_results
    
    def _count_outliers(self, series):
        """Count outliers using IQR method"""
        if series.dtype not in [np.number] or series.isnull().all():
            return 0
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return ((series < lower_bound) | (series > upper_bound)).sum()
    
    def identify_data_issues(self):
        """Identify specific data quality issues"""
        df = self.df
        issues = {}
        
        # Price inconsistencies
        price_issues = []
        if 'price_colones' in df.columns and 'price_usd' in df.columns:
            # Check exchange rate consistency (should be around 500-600)
            valid_prices = df[(df['price_colones'] > 0) & (df['price_usd'] > 0)]
            if len(valid_prices) > 0:
                exchange_rates = valid_prices['price_colones'] / valid_prices['price_usd']
                median_rate = exchange_rates.median()
                outlier_rates = exchange_rates[(exchange_rates < 400) | (exchange_rates > 700)]
                price_issues.append(f"Median exchange rate: {median_rate:.2f}")
                price_issues.append(f"Outlier exchange rates: {len(outlier_rates)} records")
        
        # Year validation
        year_issues = []
        if 'year' in df.columns:
            current_year = datetime.now().year
            invalid_years = df[(df['year'] < 1950) | (df['year'] > current_year + 2)]
            year_issues.append(f"Invalid years: {len(invalid_years)} records")
        
        # Mileage validation
        mileage_issues = []
        if 'mileage' in df.columns:
            high_mileage = df[df['mileage'] > 500000]  # > 500k km
            zero_mileage = df[df['mileage'] == 0]
            mileage_issues.append(f"High mileage (>500k): {len(high_mileage)} records")
            mileage_issues.append(f"Zero mileage: {len(zero_mileage)} records")
        
        # Brand/Model consistency
        brand_issues = []
        if 'brand' in df.columns:
            brand_variations = df['brand'].value_counts()
            # Look for potential duplicates (case variations, etc.)
            brands_lower = df['brand'].str.lower().value_counts()
            if len(brand_variations) != len(brands_lower):
                brand_issues.append("Case inconsistencies in brand names detected")
        
        # Description quality
        desc_issues = []
        if 'description' in df.columns:
            generic_desc = df[df['description'].str.contains('Copyright|Todos los derechos', na=False)]
            desc_issues.append(f"Generic descriptions: {len(generic_desc)} records")
        
        issues = {
            'price_issues': price_issues,
            'year_issues': year_issues,
            'mileage_issues': mileage_issues,
            'brand_issues': brand_issues,
            'description_issues': desc_issues
        }
        
        return issues
    
    def generate_cleaning_recommendations(self):
        """Generate data cleaning recommendations"""
        recommendations = {
            'missing_data': [],
            'data_standardization': [],
            'outlier_handling': [],
            'data_validation': []
        }
        
        # Missing data recommendations
        missing = self.analysis_results['missing_analysis']
        for col, stats in missing.items():
            if stats['null_percentage'] > 50:
                recommendations['missing_data'].append(f"Consider dropping {col} (>{stats['null_percentage']}% missing)")
            elif stats['null_percentage'] > 20:
                recommendations['missing_data'].append(f"Impute {col} ({stats['null_percentage']}% missing)")
        
        # Standardization recommendations
        recommendations['data_standardization'].extend([
            "Standardize brand names (case, spelling)",
            "Clean and normalize fuel_type values",
            "Standardize transmission values",
            "Extract meaningful features from description",
            "Normalize phone number formats"
        ])
        
        # Outlier handling
        numeric = self.analysis_results['numeric_analysis']
        for col, stats in numeric.items():
            if stats['outliers_count'] > 0:
                recommendations['outlier_handling'].append(f"Review {stats['outliers_count']} outliers in {col}")
        
        # Validation rules
        recommendations['data_validation'].extend([
            "Validate year range (1950-2026)",
            "Check price consistency (colones vs USD)",
            "Validate mileage ranges",
            "Ensure vehicle_id uniqueness"
        ])
        
        return recommendations
    
    def save_analysis(self, output_dir: str = "docs"):
        """Save analysis results to files"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save as JSON
        json_path = Path(output_dir) / f"data_quality_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        
        # Save recommendations
        recommendations = self.generate_cleaning_recommendations()
        issues = self.identify_data_issues()
        
        full_report = {
            'analysis_results': self.analysis_results,
            'data_issues': issues,
            'cleaning_recommendations': recommendations
        }
        
        report_path = Path(output_dir) / f"eda_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(full_report, f, indent=2, default=str)
        
        return json_path, report_path

def main():
    analyzer = VehicleDataAnalyzer()
    
    print("Loading vehicle data...")
    df = analyzer.load_data()
    print(f"Loaded {len(df)} records")
    
    print("Analyzing data quality...")
    analysis = analyzer.analyze_data_quality()
    
    print("Identifying data issues...")
    issues = analyzer.identify_data_issues()
    
    print("Generating recommendations...")
    recommendations = analyzer.generate_cleaning_recommendations()
    
    print("Saving analysis results...")
    json_path, report_path = analyzer.save_analysis()
    
    print(f"Analysis complete!")
    print(f"Results saved to: {json_path}")
    print(f"Full report saved to: {report_path}")
    
    # Print summary
    print(f"\nSUMMARY:")
    print(f"Total records: {analysis['basic_info']['total_records']}")
    print(f"Columns with >20% missing: {sum(1 for col, stats in analysis['missing_analysis'].items() if stats['null_percentage'] > 20)}")
    print(f"Total outliers detected: {sum(stats['outliers_count'] for stats in analysis['numeric_analysis'].values())}")

if __name__ == "__main__":
    main()