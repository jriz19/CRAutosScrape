import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from datetime import datetime
from collections import defaultdict
import re

class PageStructureAnalyzer:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.analyzed_urls = set()
        self.structure = {
            'base_url': base_url,
            'domain': self.domain,
            'analysis_date': datetime.now().isoformat(),
            'pages': {},
            'navigation_patterns': {},
            'data_fields': {},
            'database_schema': {}
        }
    
    def analyze_page(self, url: str, depth: int = 0, max_depth: int = 3):
        if depth > max_depth or url in self.analyzed_urls:
            return
        
        self.analyzed_urls.add(url)
        print(f"Analyzing: {url} (depth: {depth})")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            page_info = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'forms': self._analyze_forms(soup),
                'links': self._analyze_links(soup, url),
                'vehicle_data': self._extract_vehicle_data(soup),
                'pagination': self._analyze_pagination(soup),
                'filters': self._analyze_filters(soup),
                'content_structure': self._analyze_content_structure(soup)
            }
            
            self.structure['pages'][url] = page_info
            
            # Analyze child pages
            if depth < max_depth:
                for link in page_info['links']['internal'][:5]:  # Limit to 5 links per page
                    time.sleep(1)  # Be respectful
                    self.analyze_page(link, depth + 1, max_depth)
                    
        except Exception as e:
            print(f"Error analyzing {url}: {e}")
    
    def _analyze_forms(self, soup):
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'inputs': []
            }
            
            for input_tag in form.find_all(['input', 'select', 'textarea']):
                input_data = {
                    'type': input_tag.get('type', input_tag.name),
                    'name': input_tag.get('name', ''),
                    'id': input_tag.get('id', ''),
                    'placeholder': input_tag.get('placeholder', ''),
                    'options': []
                }
                
                if input_tag.name == 'select':
                    input_data['options'] = [opt.get('value', opt.text) for opt in input_tag.find_all('option')]
                
                form_data['inputs'].append(input_data)
            
            forms.append(form_data)
        
        return forms
    
    def _analyze_links(self, soup, current_url):
        links = {'internal': [], 'external': [], 'vehicle_detail': []}
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            
            if self.domain in full_url:
                links['internal'].append(full_url)
                
                # Detect vehicle detail pages
                if any(pattern in href.lower() for pattern in ['detalle', 'detail', 'vehiculo', 'auto']):
                    links['vehicle_detail'].append(full_url)
            else:
                links['external'].append(full_url)
        
        return {k: list(set(v)) for k, v in links.items()}
    
    def _extract_vehicle_data(self, soup):
        vehicle_fields = {}
        
        # Common vehicle data patterns
        patterns = {
            'price': r'(\$|precio|price)',
            'year': r'(año|year|modelo)',
            'brand': r'(marca|brand|make)',
            'model': r'(modelo|model)',
            'mileage': r'(kilometraje|mileage|km)',
            'fuel': r'(combustible|fuel|gasolina)',
            'transmission': r'(transmision|transmission|automatica|manual)',
            'color': r'(color|colour)',
            'engine': r'(motor|engine|cilindros)',
            'location': r'(ubicacion|location|ciudad)'
        }
        
        # Extract from text content
        text_content = soup.get_text().lower()
        for field, pattern in patterns.items():
            matches = re.findall(f'{pattern}[:\s]*([^\\n\\r,]+)', text_content, re.IGNORECASE)
            if matches:
                vehicle_fields[field] = matches[:3]  # Keep first 3 matches
        
        # Extract from structured data (classes, ids)
        structured_data = {}
        for element in soup.find_all(['div', 'span', 'p'], class_=True):
            classes = ' '.join(element.get('class', []))
            if any(keyword in classes.lower() for keyword in ['price', 'year', 'brand', 'model']):
                structured_data[classes] = element.get_text(strip=True)
        
        return {
            'text_patterns': vehicle_fields,
            'structured_elements': structured_data
        }
    
    def _analyze_pagination(self, soup):
        pagination = {
            'next_page': None,
            'prev_page': None,
            'page_numbers': [],
            'total_pages': None
        }
        
        # Look for pagination elements
        for element in soup.find_all(['a', 'button'], text=re.compile(r'(siguiente|next|anterior|prev|\d+)', re.I)):
            text = element.get_text(strip=True).lower()
            href = element.get('href', '')
            
            if 'siguiente' in text or 'next' in text:
                pagination['next_page'] = urljoin(self.base_url, href)
            elif 'anterior' in text or 'prev' in text:
                pagination['prev_page'] = urljoin(self.base_url, href)
            elif text.isdigit():
                pagination['page_numbers'].append(int(text))
        
        return pagination
    
    def _analyze_filters(self, soup):
        filters = {}
        
        # Look for filter forms and selects
        for select in soup.find_all('select'):
            name = select.get('name', select.get('id', ''))
            if name:
                options = [opt.get('value', opt.text) for opt in select.find_all('option') if opt.get('value')]
                filters[name] = options
        
        return filters
    
    def _analyze_content_structure(self, soup):
        structure = {
            'vehicle_listings': [],
            'detail_sections': [],
            'navigation_menus': []
        }
        
        # Find vehicle listing containers
        for container in soup.find_all(['div', 'article'], class_=re.compile(r'(vehiculo|auto|car|listing)', re.I)):
            structure['vehicle_listings'].append({
                'class': container.get('class', []),
                'id': container.get('id', ''),
                'child_elements': len(container.find_all())
            })
        
        # Find navigation menus
        for nav in soup.find_all(['nav', 'ul'], class_=re.compile(r'(menu|nav)', re.I)):
            structure['navigation_menus'].append({
                'class': nav.get('class', []),
                'links_count': len(nav.find_all('a'))
            })
        
        return structure
    
    def generate_database_schema(self):
        # Generate SQLite schema based on analyzed data
        schema = {
            'vehicles': {
                'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                'url': 'TEXT UNIQUE',
                'title': 'TEXT',
                'price': 'REAL',
                'year': 'INTEGER',
                'brand': 'TEXT',
                'model': 'TEXT',
                'mileage': 'INTEGER',
                'fuel_type': 'TEXT',
                'transmission': 'TEXT',
                'color': 'TEXT',
                'engine': 'TEXT',
                'location': 'TEXT',
                'description': 'TEXT',
                'images': 'TEXT',  # JSON array of image URLs
                'scraped_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP',
                'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
            },
            'vehicle_images': {
                'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                'vehicle_id': 'INTEGER',
                'image_url': 'TEXT',
                'image_type': 'TEXT',  # main, gallery, etc.
                'FOREIGN KEY (vehicle_id)': 'REFERENCES vehicles(id)'
            },
            'scraping_log': {
                'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
                'url': 'TEXT',
                'status': 'TEXT',  # success, error, skipped
                'error_message': 'TEXT',
                'scraped_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP'
            }
        }
        
        self.structure['database_schema'] = schema
        return schema
    
    def save_analysis(self, filename: str = None):
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"page_structure_analysis_{timestamp}.json"
        
        # Generate database schema
        self.generate_database_schema()
        
        # Add navigation patterns summary
        self.structure['navigation_patterns'] = {
            'total_pages_analyzed': len(self.structure['pages']),
            'vehicle_detail_pages': sum(1 for page in self.structure['pages'].values() 
                                      if page['vehicle_data']['text_patterns']),
            'common_filters': self._get_common_filters(),
            'pagination_found': any(page['pagination']['next_page'] for page in self.structure['pages'].values())
        }
        
        filepath = f"raw_data/json/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.structure, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis saved to: {filepath}")
        return filepath
    
    def _get_common_filters(self):
        all_filters = {}
        for page in self.structure['pages'].values():
            for filter_name, options in page['filters'].items():
                if filter_name not in all_filters:
                    all_filters[filter_name] = set()
                all_filters[filter_name].update(options)
        
        return {k: list(v) for k, v in all_filters.items()}

if __name__ == "__main__":
    analyzer = PageStructureAnalyzer("https://crautos.com/autosusados/index.cfm")
    analyzer.analyze_page(analyzer.base_url, max_depth=2)
    analyzer.save_analysis()