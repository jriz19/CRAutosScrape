import time
import logging
from typing import List, Optional, Generator
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_scraper import BaseScraper
from data_models import Vehicle
from utils import VehicleParser, LinkExtractor, ImageExtractor

class CrautosScraper(BaseScraper):
    def __init__(self):
        super().__init__("crautos")
        self.base_url = "https://crautos.com"
        self.listing_url = "https://crautos.com/autosusados/index.cfm"
        self.parser = VehicleParser()
        self.link_extractor = LinkExtractor()
        self.image_extractor = ImageExtractor()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def scrape(self) -> dict:
        """Main scrape method - returns summary statistics"""
        self.logger.info("Starting CRautos scraping...")
        
        vehicles_scraped = 0
        errors = 0
        
        try:
            # Get vehicle links from listing pages
            vehicle_links = self._get_all_vehicle_links()
            self.logger.info(f"Found {len(vehicle_links)} vehicle links")
            
            # Scrape each vehicle
            for link in vehicle_links:
                try:
                    vehicle = self._scrape_vehicle_detail(link)
                    if vehicle:
                        self.save_raw_data(vehicle.to_dict())
                        vehicles_scraped += 1
                        self.logger.info(f"Scraped vehicle {vehicle.vehicle_id}: {vehicle.brand} {vehicle.model}")
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {link}: {e}")
                    errors += 1
                    
        except Exception as e:
            self.logger.error(f"Critical error in scraping: {e}")
            errors += 1
        
        return {
            'vehicles_scraped': vehicles_scraped,
            'errors': errors,
            'status': 'completed'
        }
    
    def _get_all_vehicle_links(self) -> List[str]:
        """Get all vehicle detail page links from all listing pages"""
        all_links = []
        page = 1
        max_pages = 50  # Safety limit
        
        while page <= max_pages:
            try:
                # Get page content
                if page == 1:
                    response = self.session.get(self.listing_url)
                else:
                    # Try different pagination approaches
                    page_url = f"{self.listing_url}?p={page}"
                    response = self.session.get(page_url)
                    
                    # If that fails, try with different parameter
                    if response.status_code != 200:
                        page_url = f"{self.listing_url}?page={page}"
                        response = self.session.get(page_url)
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract vehicle links from current page
                links = self.link_extractor.extract_vehicle_links(soup, self.base_url)
                
                if not links:
                    self.logger.info(f"No vehicles found on page {page}. Stopping.")
                    break
                
                # Check if we're getting the same links (indicates no more pages)
                new_links = [link for link in links if link not in all_links]
                if not new_links and page > 1:
                    self.logger.info(f"No new vehicles on page {page}. Stopping.")
                    break
                
                all_links.extend(new_links)
                self.logger.info(f"Found {len(new_links)} new vehicles on page {page} (total: {len(all_links)})")
                
                page += 1
                time.sleep(1)  # Rate limit between pages
                
            except Exception as e:
                self.logger.error(f"Error getting vehicle links from page {page}: {e}")
                break
        
        return list(set(all_links))
    
    def _scrape_vehicle_detail(self, url: str) -> Optional[Vehicle]:
        """Scrape individual vehicle detail page"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Create vehicle object
            vehicle = Vehicle(url=url)
            vehicle.extract_id_from_url()
            
            # Extract basic info from title
            title = soup.title.string if soup.title else ""
            self._parse_title(vehicle, title)
            
            # Extract price information
            self._parse_prices(vehicle, soup)
            
            # Extract technical details
            self._parse_technical_details(vehicle, soup)
            
            # Extract contact information
            self._parse_contact_info(vehicle, soup)
            
            # Extract images
            vehicle.images = self.image_extractor.extract_vehicle_images(soup, self.base_url)
            
            # Extract description
            self._parse_description(vehicle, soup)
            
            return vehicle
            
        except Exception as e:
            self.logger.error(f"Error scraping vehicle detail {url}: {e}")
            return None
    
    def _parse_title(self, vehicle: Vehicle, title: str):
        """Parse vehicle info from page title"""
        # Title format: "crautos.com Brand MODEL Year ¢ price ($ usd_price)*"
        parts = title.split()
        
        for i, part in enumerate(parts):
            if part.isdigit() and len(part) == 4:  # Year
                vehicle.year = int(part)
                if i > 1:
                    vehicle.brand = parts[1] if len(parts) > 1 else ""
                    vehicle.model = ' '.join(parts[2:i]) if i > 2 else ""
                break
        
        vehicle.normalize_brand()
    
    def _parse_prices(self, vehicle: Vehicle, soup: BeautifulSoup):
        """Parse price information"""
        text_content = soup.get_text()
        
        vehicle.price_colones = self.parser.extract_price_colones(text_content)
        vehicle.price_usd = self.parser.extract_price_usd(text_content)
    
    def _parse_technical_details(self, vehicle: Vehicle, soup: BeautifulSoup):
        """Parse technical specifications"""
        text_content = soup.get_text().lower()
        
        # Extract mileage
        vehicle.mileage = self.parser.extract_mileage(text_content)
        
        # Extract engine CC
        vehicle.engine_cc = self.parser.extract_engine_cc(text_content)
        
        # Extract fuel type
        if 'diesel' in text_content:
            vehicle.fuel_type = 'Diesel'
        elif 'gasolina' in text_content or 'gasoline' in text_content:
            vehicle.fuel_type = 'Gasolina'
        elif 'híbrido' in text_content or 'hybrid' in text_content:
            vehicle.fuel_type = 'Híbrido'
        
        # Extract transmission
        if 'manual' in text_content:
            vehicle.transmission = 'Manual'
        elif 'automática' in text_content or 'automatic' in text_content:
            vehicle.transmission = 'Automática'
        
        # Extract colors (look for specific patterns)
        color_patterns = [
            r'color\s+exterior[:\s]+([^,\n]+)',
            r'color\s+interior[:\s]+([^,\n]+)'
        ]
        
        for i, pattern in enumerate(color_patterns):
            import re
            match = re.search(pattern, text_content)
            if match:
                color = match.group(1).strip().title()
                if i == 0:
                    vehicle.color_exterior = color
                else:
                    vehicle.color_interior = color
    
    def _parse_contact_info(self, vehicle: Vehicle, soup: BeautifulSoup):
        """Parse contact information"""
        text_content = soup.get_text()
        
        # Extract phone numbers
        phones = self.parser.extract_phone_numbers(text_content)
        if phones:
            vehicle.seller_phone = phones[0]
        
        # Extract WhatsApp links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'whatsapp.com' in href or 'wa.me' in href:
                vehicle.seller_whatsapp = href
                break
    
    def _parse_description(self, vehicle: Vehicle, soup: BeautifulSoup):
        """Parse vehicle description and features"""
        # Look for description in common containers
        description_selectors = [
            'div.description',
            'div.details',
            'p',
            'div'
        ]
        
        descriptions = []
        for selector in description_selectors:
            elements = soup.select(selector)
            for element in elements[:3]:  # Limit to avoid too much text
                text = element.get_text(strip=True)
                if len(text) > 50 and len(text) < 1000:  # Reasonable description length
                    descriptions.append(text)
        
        vehicle.description = ' '.join(descriptions[:2])  # Combine first 2 descriptions
        vehicle.description = self.parser.clean_text(vehicle.description)