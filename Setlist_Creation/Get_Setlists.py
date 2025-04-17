
"""
Get_Setlists.py

Main entry point for running band setlist scrapers. Supports dynamic imports, robust error handling, and optional CLI selection of bands.
"""
import importlib
import argparse
import logging
import os
from SetlistCollector import SetlistCollectorManager

# Set up logging configuration for the entire script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    # Ensure logs directory exists
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'Setlist_Creation')
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, 'setlist_scraper.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    parser = argparse.ArgumentParser(description="Run band setlist scrapers.")
    parser.add_argument('--bands', type=str, help="Comma-separated list of bands to scrape (default: all)")
    args = parser.parse_args()

    # List of all supported band modules
    all_band_modules = ['Goose', 'Phish', 'UM', 'WSP']
    if args.bands:
        band_modules = [b.strip() for b in args.bands.split(',') if b.strip() in all_band_modules]
        if not band_modules:
            logging.error(f"No valid bands specified. Supported: {all_band_modules}")
            return
    else:
        band_modules = all_band_modules

    manager = SetlistCollectorManager()
    for module_name in band_modules:
        try:
            module = importlib.import_module(module_name)
            class_name = f"{module_name}SetlistCollector"
            scraper_class = getattr(module, class_name, None)
            if scraper_class:
                manager.register_scraper(scraper_class)
                logging.info(f"Registered scraper: {class_name}")
            else:
                logging.error(f"Invalid or missing class {class_name} in module {module_name}")
        except ImportError as e:
            logging.error(f"Could not import {module_name} scraper: {e}")
        except Exception as e:
            logging.error(f"Error registering scraper for {module_name}: {e}")

    manager.scrape_all()

if __name__ == "__main__":
    main()