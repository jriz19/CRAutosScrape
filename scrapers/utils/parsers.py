import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse

class VehicleParser:
    @staticmethod
    def extract_price_colones(text: str) -> Optional[int]:
        """Extract price in colones from text"""
        match = re.search(r'¢\s*([\d,\.]+)', text.replace(',', ''))
        if match:
            return int(match.group(1).replace('.', '').replace(',', ''))
        return None
    
    @staticmethod
    def extract_price_usd(text: str) -> Optional[int]:
        """Extract USD price from text"""
        match = re.search(r'\$\s*([\d,\.]+)', text.replace(',', ''))
        if match:
            return int(match.group(1).replace('.', '').replace(',', ''))
        return None
    
    @staticmethod
    def extract_year(text: str) -> Optional[int]:
        """Extract year from text"""
        match = re.search(r'\b(19|20)\d{2}\b', text)
        return int(match.group()) if match else None
    
    @staticmethod
    def extract_mileage(text: str) -> Optional[int]:
        """Extract mileage from text"""
        match = re.search(r'(\d+)[\s,]*k?m?s?\s*km', text.lower())
        if match:
            return int(match.group(1)) * 1000
        match = re.search(r'(\d+)[\s,]*mil', text.lower())
        if match:
            return int(match.group(1)) * 1000
        return None
    
    @staticmethod
    def extract_engine_cc(text: str) -> Optional[int]:
        """Extract engine displacement in CC"""
        match = re.search(r'(\d+)\s*c[c|m]', text.lower())
        if match:
            return int(match.group(1))
        match = re.search(r'(\d+)\s*l', text.lower())
        if match:
            return int(match.group(1)) * 1000
        return None
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract phone numbers from text"""
        patterns = [
            r'\b\d{4}-\d{4}\b',  # 8888-8888
            r'\b\d{8}\b',        # 88888888
            r'\+506\s*\d{8}',    # +506 88888888
        ]
        phones = []
        for pattern in patterns:
            phones.extend(re.findall(pattern, text))
        return list(set(phones))
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        return ' '.join(text.strip().split())

class LinkExtractor:
    @staticmethod
    def extract_vehicle_links(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract vehicle detail page links"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'cardetail.cfm' in href and 'c=' in href:
                full_url = urljoin(base_url, href)
                links.append(full_url)
        return list(set(links))
    
    @staticmethod
    def extract_pagination_links(soup: BeautifulSoup, base_url: str) -> Dict[str, Optional[str]]:
        """Extract pagination links"""
        pagination = {'next': None, 'prev': None, 'pages': []}
        
        # Look for pagination elements
        for element in soup.find_all(['a', 'button']):
            text = element.get_text(strip=True).lower()
            href = element.get('href', '')
            
            if any(word in text for word in ['siguiente', 'next', '>']):
                pagination['next'] = urljoin(base_url, href) if href else None
            elif any(word in text for word in ['anterior', 'prev', '<']):
                pagination['prev'] = urljoin(base_url, href) if href else None
            elif text.isdigit():
                pagination['pages'].append(urljoin(base_url, href) if href else None)
        
        # Also check for form-based pagination (common in ColdFusion sites)
        forms = soup.find_all('form')
        for form in forms:
            if 'page' in str(form).lower() or 'siguiente' in str(form).lower():
                pagination['has_form_pagination'] = True
        
        return pagination

class ImageExtractor:
    @staticmethod
    def extract_vehicle_images(soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract vehicle image URLs"""
        images = []
        
        # Look for images in common containers
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and any(keyword in src.lower() for keyword in ['vehicle', 'car', 'auto', 'foto']):
                full_url = urljoin(base_url, src)
                images.append(full_url)
        
        return list(set(images))