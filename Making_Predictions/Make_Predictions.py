
from PredictionMaker import PredictionMakerManager
#from Phish import PhishSetlistCollector
from Goose import GoosePredictionMaker
#from WSP import WSPSetlistCollector

def main():
    """Main function to run the band data scrapers."""
    
    manager = PredictionMakerManager()
    
    #band_modules = ['Goose','Phish', 'WSP']  # Add more band module names as needed
    band_modules = ['Goose']
    
    for module_name in band_modules:
        try:
            # Dynamically get the scraper class
            class_name = f"{module_name}PredictionMaker"
            predictor_class = globals().get(class_name)

            # Validate and register scraper
            if predictor_class:
                manager.register_predictor(predictor_class)
            else:
                print(f"Invalid or missing class {class_name} in module {module_name}")

        except ImportError as e:
            print(f"Could not import {module_name} predictor: {e}")

    manager.predict_all()

if __name__ == "__main__":
    main()