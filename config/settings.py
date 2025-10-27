import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import ClassVar

class Settings(BaseSettings):
    # Project paths (ClassVar to exclude from pydantic fields)
    PROJECT_ROOT: ClassVar[Path] = Path(__file__).parent.parent
    RAW_DATA_PATH: ClassVar[Path] = PROJECT_ROOT / "raw_data"
    LOGS_PATH: ClassVar[Path] = PROJECT_ROOT / "logs"
    
    # Database
    DATABASE_URL: str = "sqlite:///vehicles.db"
    
    # Scraping settings
    SCRAPE_DELAY: int = 1
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # ETL settings
    BATCH_SIZE: int = 1000
    STAGING_SCHEMA: str = "staging"
    PROD_SCHEMA: str = "production"
    
    class Config:
        env_file = ".env"

settings = Settings()