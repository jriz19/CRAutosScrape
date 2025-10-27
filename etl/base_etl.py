from abc import ABC, abstractmethod
import pandas as pd
from sqlalchemy import create_engine
from config.settings import settings

class BaseETL(ABC):
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
    
    @abstractmethod
    def extract(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    
    def load_to_staging(self, df: pd.DataFrame, table_name: str):
        df.to_sql(
            table_name, 
            self.engine, 
            schema=settings.STAGING_SCHEMA,
            if_exists='replace',
            index=False
        )
    
    def load_to_production(self, df: pd.DataFrame, table_name: str):
        df.to_sql(
            table_name, 
            self.engine, 
            schema=settings.PROD_SCHEMA,
            if_exists='append',
            index=False
        )
    
    def run_pipeline(self, table_name: str):
        raw_data = self.extract()
        cleaned_data = self.transform(raw_data)
        self.load_to_staging(cleaned_data, f"staging_{table_name}")
        self.load_to_production(cleaned_data, table_name)