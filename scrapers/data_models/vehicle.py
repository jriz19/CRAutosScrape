from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
import re

@dataclass
class Vehicle:
    url: str
    vehicle_id: str = ""
    brand: str = ""
    model: str = ""
    year: Optional[int] = None
    price_colones: Optional[int] = None
    price_usd: Optional[int] = None
    mileage: Optional[int] = None
    fuel_type: str = ""
    transmission: str = ""
    engine_cc: Optional[int] = None
    doors: Optional[int] = None
    style: str = ""
    color_exterior: str = ""
    color_interior: str = ""
    location: str = ""
    province: str = ""
    seller_phone: str = ""
    seller_whatsapp: str = ""
    description: str = ""
    features: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    scraped_at: datetime = field(default_factory=datetime.now)
    
    def extract_id_from_url(self):
        """Extract vehicle ID from URL"""
        match = re.search(r'c=(\d+)', self.url)
        if match:
            self.vehicle_id = match.group(1)
    
    def clean_price(self, price_text: str) -> Optional[int]:
        """Extract numeric price from text"""
        if not price_text:
            return None
        numbers = re.findall(r'[\d,]+', price_text.replace('.', '').replace(',', ''))
        return int(numbers[0]) if numbers else None
    
    def normalize_brand(self):
        """Normalize brand name"""
        self.brand = self.brand.strip().title()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'url': self.url,
            'vehicle_id': self.vehicle_id,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'price_colones': self.price_colones,
            'price_usd': self.price_usd,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'transmission': self.transmission,
            'engine_cc': self.engine_cc,
            'doors': self.doors,
            'style': self.style,
            'color_exterior': self.color_exterior,
            'color_interior': self.color_interior,
            'location': self.location,
            'province': self.province,
            'seller_phone': self.seller_phone,
            'seller_whatsapp': self.seller_whatsapp,
            'description': self.description,
            'features': ','.join(self.features),
            'images': ','.join(self.images),
            'scraped_at': self.scraped_at.isoformat()
        }