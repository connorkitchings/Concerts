
from SetlistCollector import SetlistCollectorManager
from Phish import PhishSetlistCollector
from Goose import GooseSetlistCollector
from WSP import WSPSetlistCollector
from UM import UMSetlistCollector

def main():
    """Main function to run the band data scrapers."""
    
    manager = SetlistCollectorManager()
    
    band_modules = ['Goose','Phish', 'UM', 'WSP']  # Add more band module names as needed
    band_modules = ['UM']  # Add more band module names as needed
    
    for module_name in band_modules:
        try:
            # Dynamically get the scraper class
            class_name = f"{module_name}SetlistCollector"
            scraper_class = globals().get(class_name)

            # Validate and register scraper
            if scraper_class:
                manager.register_scraper(scraper_class)
            else:
                print(f"Invalid or missing class {class_name} in module {module_name}")

        except ImportError as e:
            print(f"Could not import {module_name} scraper: {e}")

    manager.scrape_all()

if __name__ == "__main__":
    main()