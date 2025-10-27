import pandas as pd
import numpy as np
import re
from typing import Dict, Any

class DataCleaner:
    def __init__(self):
        self.brand_mapping = {
            'bmw': 'BMW',
            'mercedes': 'Mercedes-Benz',
            'mercedes benz': 'Mercedes-Benz',
            'volkswagen': 'Volkswagen',
            'vw': 'Volkswagen'
        }
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all cleaning transformations"""
        df = df.copy()
        
        # Remove completely empty columns
        df = self._remove_empty_columns(df)
        
        # Clean and standardize data
        df = self._clean_brands(df)
        df = self._clean_models(df)
        df = self._clean_fuel_types(df)
        df = self._clean_years(df)
        df = self._clean_mileage(df)
        df = self._clean_engine_cc(df)
        df = self._clean_colors(df)
        df = self._validate_prices(df)
        df = self._clean_phone_numbers(df)
        
        # Add derived features
        df = self._add_derived_features(df)
        
        return df
    
    def _remove_empty_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove columns that are 100% empty"""
        # Based on analysis: doors, style, location, province, features are 100% empty
        empty_cols = ['doors', 'style', 'location', 'province', 'features']
        return df.drop(columns=[col for col in empty_cols if col in df.columns])
    
    def _clean_brands(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize brand names"""
        if 'brand' in df.columns:
            df['brand'] = df['brand'].str.lower().str.strip()
            df['brand'] = df['brand'].replace(self.brand_mapping)
            df['brand'] = df['brand'].str.title()
        return df
    
    def _clean_models(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean model names"""
        if 'model' in df.columns:
            # Replace empty strings with None
            df['model'] = df['model'].replace('', None)
            # Clean model names
            df['model'] = df['model'].str.strip().str.upper()
            # Handle Mercedes models that include "Benz"
            df.loc[df['brand'] == 'Mercedes-Benz', 'model'] = df.loc[df['brand'] == 'Mercedes-Benz', 'model'].str.replace('BENZ ', '')
        return df
    
    def _clean_fuel_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize fuel types"""
        if 'fuel_type' in df.columns:
            df['fuel_type'] = df['fuel_type'].replace('', None)
            fuel_mapping = {
                'gasolina': 'Gasoline',
                'diesel': 'Diesel',
                'híbrido': 'Hybrid',
                'hibrido': 'Hybrid'
            }
            df['fuel_type'] = df['fuel_type'].str.lower().replace(fuel_mapping)
        return df
    
    def _clean_years(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate years"""
        if 'year' in df.columns:
            # Set invalid years to None (based on analysis: years < 1950 or > 2026)
            df.loc[(df['year'] < 1950) | (df['year'] > 2026), 'year'] = None
        return df
    
    def _clean_mileage(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean mileage data"""
        if 'mileage' in df.columns:
            # Handle extreme values (>500k might be data entry errors)
            df.loc[df['mileage'] > 500000, 'mileage'] = None
            # Convert 0 mileage to None for used cars (likely missing data)
            df.loc[df['mileage'] == 0, 'mileage'] = None
        return df
    
    def _clean_engine_cc(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean engine displacement"""
        if 'engine_cc' in df.columns:
            # Handle outliers (based on analysis: 18 outliers)
            df.loc[(df['engine_cc'] < 500) | (df['engine_cc'] > 6000), 'engine_cc'] = None
        return df
    
    def _clean_colors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize color names"""
        color_mapping = {
            'negro': 'Black',
            'blanco': 'White',
            'gris': 'Gray',
            'azul': 'Blue',
            'rojo': 'Red',
            'plateado': 'Silver',
            'café': 'Brown',
            'vino': 'Burgundy'
        }
        
        for col in ['color_exterior', 'color_interior']:
            if col in df.columns:
                df[col] = df[col].str.lower().str.strip()
                for spanish, english in color_mapping.items():
                    df[col] = df[col].str.replace(spanish, english.lower())
                df[col] = df[col].str.title()
        return df
    
    def _validate_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate price consistency"""
        if 'price_colones' in df.columns and 'price_usd' in df.columns:
            # Calculate exchange rate
            df['exchange_rate'] = df['price_colones'] / df['price_usd']
            # Flag suspicious exchange rates (not between 400-600)
            df['price_flag'] = (df['exchange_rate'] < 400) | (df['exchange_rate'] > 600)
        return df
    
    def _clean_phone_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize phone numbers"""
        if 'seller_phone' in df.columns:
            df['seller_phone'] = df['seller_phone'].str.replace(r'[^\d-]', '', regex=True)
        return df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add useful derived features"""
        # Vehicle age
        if 'year' in df.columns:
            current_year = pd.Timestamp.now().year
            df['vehicle_age'] = current_year - df['year']
        
        # Price per year (depreciation indicator)
        if 'price_usd' in df.columns and 'vehicle_age' in df.columns:
            df['price_per_year'] = df['price_usd'] / (df['vehicle_age'] + 1)
        
        # Luxury brand flag
        if 'brand' in df.columns:
            luxury_brands = ['BMW', 'Mercedes-Benz', 'Audi', 'Porsche', 'Lexus', 'Jaguar', 'Land Rover']
            df['is_luxury'] = df['brand'].isin(luxury_brands)
        
        return df