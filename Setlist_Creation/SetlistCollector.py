from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional
from pathlib import Path
import pandas as pd
from datetime import date, datetime
import importlib
import logging

# Define Abstract Setlist Collector Class
class SetlistCollector(ABC):
    """
    Abstract base class for band data scraping.
    Provides a standardized interface for data collection and saving.
    """
    
    # Configurable allowed bands list
    ALLOWED_BANDS = ['Goose', 'Phish', 'UM', 'WSP']

    def __init__(self, band: str, base_dir: Optional[str] = None):
        """
        Initialize the band data scraper.
        
        Args:
            band: Name of the band (must be in ALLOWED_BANDS)
            base_dir: Base directory for data storage. Defaults to script directory's parent
        """
        if band not in self.ALLOWED_BANDS:
            raise ValueError(f"Band must be one of: {self.ALLOWED_BANDS}. Got: {band}")
        
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
    - Register scraper classes for each band.
    - Run scraping for all or a subset of registered bands.
    - Reports summary of successes and failures.
    """
    
    def __init__(self):
        """Initialize the scraper manager and scraper registry."""
        self.scrapers: Dict[str, SetlistCollector] = {}
        self.successful: Dict[str, float] = {}
        self.failed: Dict[str, str] = {}
    
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
            logging.error(f"Error registering scraper {scraper_class.__name__}: {e}")
    
    def scrape_all(self) -> None:
        """
        Scrape data for all registered bands.
        Prints a summary of successes and failures.
        """
        overall_start_time = datetime.now()
        self.successful = {}
        self.failed = {}
        for band, scraper in self.scrapers.items():
            logging.info(f"Scraping data for {band}")
            start_time = datetime.now()
            try:
                scraper.create_and_save_data()
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                minutes, seconds = divmod(execution_time, 60)
                logging.info(f"{band} Setlist Collection Time: {int(minutes)} minutes and {seconds:.2f} seconds")
                self.successful[band] = execution_time
            except Exception as e:
                logging.error(f"Error scraping data for {band}: {e}")
                self.failed[band] = str(e)
        overall_end_time = datetime.now()
        overall_execution_time = (overall_end_time - overall_start_time).total_seconds()
        minutes, seconds = divmod(overall_execution_time, 60)
        logging.info(f"Total Setlist Collection Time: {int(minutes)} minutes and {seconds:.2f} seconds")
        logging.info("--- Scrape Summary ---")
        for band, t in self.successful.items():
            logging.info(f"SUCCESS: {band} ({t:.2f} seconds)")
        for band, err in self.failed.items():
            logging.error(f"FAIL: {band} ({err})")