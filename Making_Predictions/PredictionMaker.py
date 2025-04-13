from abc import ABC, abstractmethod
from typing import Tuple, Dict, Optional
from pathlib import Path
import pandas as pd
from datetime import date, datetime
import importlib

# Define Abstract Prediction Maker Class
class PredictionMaker(ABC):
    """
    Abstract base class for band prediction making.
    Provides a standardized interface for data loading, transformation, forecasting, and saving.
    """
    
    def __init__(self, band: str, base_dir: Optional[str] = None):
        """
        Initialize the band prediction maker.
        
        Args:
        band: Name of the band (must be in ['Goose','Phish','WSP'])
        base_dir: Base directory for data storage. Defaults to script directory's parent
        """
        if band not in ['Goose', 'Phish', 'WSP', 'UM']:
            raise ValueError(f"Band must be one of: Goose, Phish, UM, WSP. Got: {band}")
        
        self.band = band
        self.base_dir = base_dir or str(Path(__file__).parent.parent)
        self.data_dir = Path(self.base_dir) / "Data" / band / "From Web"
        self.pred_dir = Path(self.base_dir) / "Data" / band / "Predictions"
        
    @abstractmethod
    def load_data(self) -> Tuple[pd.DataFrame, ...]:
        """Load and return data for the band."""
        pass
    
    @abstractmethod
    def create_ckplus(self) -> pd.DataFrame:
        """Transform data and create ck_plus dataset for band."""
        pass
    
    @abstractmethod
    def create_notebook(self) -> pd.DataFrame:
        """Transform data and create x's notebook dataset for band."""
        pass

    @abstractmethod
    def create_and_save_predictions(self):
        """Create and save created prediction dataframes"""
        pass
    
# Manager Class
class PredictionMakerManager:
    """
    Manager class to handle multiple band setlist predictors.
    """
    
    def __init__(self):
        """Initialize the predictor manager."""
        self.predictors: Dict[str, PredictionMaker] = {}
    
    def register_predictor(self, predictor_class: type) -> None:
        """
        Register a band predictor module.

        Args:
            predictor_class (type): Class inheriting from PredictionMaker
        """
        if not issubclass(predictor_class, PredictionMaker):
            raise TypeError(f"Predictor must inherit from PredictionMaker. Got: {predictor_class}")

        try:
            predictor_instance = predictor_class()  # Ensure predictor_class does not require extra arguments
            self.predictors[predictor_instance.band] = predictor_instance
        except Exception as e:
            print(f"Error registering predictor {predictor_class.__name__}: {e}")
    
    def predict_all(self) -> None:
        """Predict setlists for all registered bands."""
        overall_start_time = datetime.now()
        for band, predictor in self.predictors.items():
            print(f"Predicting setlist for {band}")
            start_time = datetime.now()

            try:
                # Save collected data
                # Add all the relevant functions here
                predictor.create_and_save_predictions()  # Using each band's defined save method 
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                minutes, seconds = divmod(execution_time, 60)  # Convert seconds into minutes and seconds
                print(f"{band} Setlist Prediction Time: {int(minutes)} minutes and {seconds:.2f} seconds")

            except Exception as e:
                print(f"Error predicting data for {band}: {e}")
                
        overall_end_time = datetime.now()
        overall_execution_time = (overall_end_time - overall_start_time).total_seconds()
        minutes, seconds = divmod(overall_execution_time, 60)  # Convert seconds into minutes and seconds
        print(f"Total Setlist Prediction Time: {int(minutes)} minutes and {seconds:.2f} seconds")