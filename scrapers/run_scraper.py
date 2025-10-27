#!/usr/bin/env python3
"""
Simple runner script for testing the CRautos scraper
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spiders import CrautosScraper

def main():
    print("Starting CRautos Scraper...")
    
    try:
        scraper = CrautosScraper()
        results = scraper.scrape()
        
        print("Scraping completed!")
        print(f"Results: {results}")
        
    except Exception as e:
        print(f"Error running scraper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()