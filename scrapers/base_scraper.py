from abc import ABC, abstractmethod
import requests
import json
from datetime import datetime
from pathlib import Path
from config.settings import settings

class BaseScraper(ABC):
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': settings.USER_AGENT})
    
    @abstractmethod
    def scrape(self) -> dict:
        pass
    
    def save_raw_data(self, data: dict, format: str = 'json'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.name}_{timestamp}.{format}"
        
        if format == 'json':
            filepath = settings.RAW_DATA_PATH / 'json' / filename
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        
        return filepath