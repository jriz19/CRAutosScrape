import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class DataValidator:
    def __init__(self):
        self.validation_rules = {
            'year': {'min': 1950, 'max': 2026},
            'price_usd': {'min': 1000, 'max': 500000},
            'price_colones': {'min': 500000, 'max': 250000000},
            'mileage': {'min': 0, 'max': 500000},
            'engine_cc': {'min': 500, 'max': 6000},
            'exchange_rate': {'min': 400, 'max': 600}
        }
    
    def validate_data(self, df: pd.DataFrame) -> Dict:
        """Validate data and return validation report"""
        report = {
            'total_records': len(df),
            'validation_errors': [],
            'warnings': [],
            'passed_validation': True
        }
        
        # Check required fields
        required_fields = ['url', 'vehicle_id', 'brand', 'price_usd', 'price_colones']
        for field in required_fields:
            if field not in df.columns:
                report['validation_errors'].append(f"Missing required field: {field}")
                report['passed_validation'] = False
            elif df[field].isnull().any():
                null_count = df[field].isnull().sum()
                report['warnings'].append(f"{field} has {null_count} null values")
        
        # Validate numeric ranges
        for field, rules in self.validation_rules.items():
            if field in df.columns:
                invalid_count = self._validate_numeric_range(df, field, rules['min'], rules['max'])
                if invalid_count > 0:
                    report['warnings'].append(f"{field} has {invalid_count} values outside valid range")
        
        # Check for duplicates
        if 'vehicle_id' in df.columns:
            duplicate_count = df['vehicle_id'].duplicated().sum()
            if duplicate_count > 0:
                report['warnings'].append(f"Found {duplicate_count} duplicate vehicle IDs")
        
        # Validate price consistency
        if 'price_usd' in df.columns and 'price_colones' in df.columns:
            inconsistent_prices = self._validate_price_consistency(df)
            if inconsistent_prices > 0:
                report['warnings'].append(f"{inconsistent_prices} records have inconsistent USD/Colones prices")
        
        return report
    
    def _validate_numeric_range(self, df: pd.DataFrame, field: str, min_val: float, max_val: float) -> int:
        """Count records outside valid numeric range"""
        if field not in df.columns:
            return 0
        
        valid_data = df[field].dropna()
        invalid_count = ((valid_data < min_val) | (valid_data > max_val)).sum()
        return invalid_count
    
    def _validate_price_consistency(self, df: pd.DataFrame) -> int:
        """Check price consistency between USD and Colones"""
        if 'price_usd' not in df.columns or 'price_colones' not in df.columns:
            return 0
        
        # Calculate exchange rate
        valid_prices = df[(df['price_usd'] > 0) & (df['price_colones'] > 0)]
        if len(valid_prices) == 0:
            return 0
        
        exchange_rates = valid_prices['price_colones'] / valid_prices['price_usd']
        
        # Count prices with suspicious exchange rates
        min_rate, max_rate = self.validation_rules['exchange_rate']['min'], self.validation_rules['exchange_rate']['max']
        inconsistent = ((exchange_rates < min_rate) | (exchange_rates > max_rate)).sum()
        
        return inconsistent
    
    def get_data_profile(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive data profile"""
        profile = {
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'missing_data': {},
            'data_types': df.dtypes.to_dict(),
            'numeric_summary': {},
            'categorical_summary': {}
        }
        
        # Missing data analysis
        for col in df.columns:
            null_count = df[col].isnull().sum()
            empty_strings = (df[col] == '').sum() if df[col].dtype == 'object' else 0
            profile['missing_data'][col] = {
                'null_count': int(null_count),
                'null_percentage': round(null_count / len(df) * 100, 2),
                'empty_strings': int(empty_strings),
                'total_missing': int(null_count + empty_strings)
            }
        
        # Numeric columns summary
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if not df[col].empty:
                profile['numeric_summary'][col] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'std': float(df[col].std())
                }
        
        # Categorical columns summary
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            unique_count = df[col].nunique()
            profile['categorical_summary'][col] = {
                'unique_count': int(unique_count),
                'top_values': df[col].value_counts().head(5).to_dict()
            }
        
        return profile