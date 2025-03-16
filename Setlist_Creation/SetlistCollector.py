from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional
from pathlib import Path
import pandas as pd
from datetime import date, datetime
import importlib

# Define Abstract Setlist Collector Class
class SetlistCollector(ABC):
    """
    Abstract base class for band data scraping.
    Provides a standardized interface for data collection and saving.
    """
    
    def __init__(self, band: str, base_dir: Optional[str] = None):
        """
        Initialize the band data scraper.
        
        Args:
        band: Name of the band (must be in ['Goose','Phish','WSP'])
        base_dir: Base directory for data storage. Defaults to script directory's parent
        """
        if band not in ['Goose', 'Phish', 'UM', 'WSP']:
            raise ValueError(f"Band must be one of: Goose, Phish, UM, WSP. Got: {band}")
        
        self.band = band
        self.base_dir = base_dir or str(Path(__file__).parent.parent)
        self.data_dir = Path(self.base_dir) / "Data" / band / "From Web"
        
    @abstractmethod
    def load_song_data(self) -> pd.DataFrame:
        """Load and return song data for the band."""
        pass

    @abstractmethod
    def load_show_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and return show (and venue data if it exists) for the band."""
        pass

    @abstractmethod
    def load_setlist_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and return setlist (and transition data if it exists) for the band."""
        pass

    @abstractmethod
    def create_and_save_data(self):
        """Save data after scraping."""
        pass
    
# Manager Class
class SetlistCollectorManager:
    """
    Manager class to handle multiple band data scrapers.
    """
    
    def __init__(self):
        """Initialize the scraper manager."""
        self.scrapers: Dict[str, SetlistCollector] = {}
    
    def register_scraper(self, scraper_class: type) -> None:
        """
        Register a band scraper module.

        Args:
            scraper_class (type): Class inheriting from SetlistCollector
        """
        if not issubclass(scraper_class, SetlistCollector):
            raise TypeError(f"Scraper must inherit from SetlistCollector. Got: {scraper_class}")

        try:
            scraper_instance = scraper_class()  # Ensure scraper_class does not require extra arguments
            self.scrapers[scraper_instance.band] = scraper_instance
        except Exception as e:
            print(f"Error registering scraper {scraper_class.__name__}: {e}")
    
    def scrape_all(self) -> None:
        """Scrape data for all registered bands."""
        overall_start_time = datetime.now()
        for band, scraper in self.scrapers.items():
            print(f"\nScraping data for {band}")
            start_time = datetime.now()

            try:
                # Save collected data
                scraper.create_and_save_data()  # Using each band's defined save method 
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                minutes, seconds = divmod(execution_time, 60)  # Convert seconds into minutes and seconds
                print(f"{band} Setlist Collection Time: {int(minutes)} minutes and {seconds:.2f} seconds")

            except Exception as e:
                print(f"Error scraping data for {band}: {e}")
                
        overall_end_time = datetime.now()
        overall_execution_time = (overall_end_time - overall_start_time).total_seconds()
        minutes, seconds = divmod(overall_execution_time, 60)  # Convert seconds into minutes and seconds
        print(f"Total Setlist Collection Time: {int(minutes)} minutes and {seconds:.2f} seconds")