"""
Router for prediction-related endpoints.
"""
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.utils.data_loader import load_prediction_data, get_last_updated_time

router = APIRouter()

class Song(BaseModel):
    """
    Data model for song prediction information.
    
    Attributes:
        name: The song name.
        times_played_last_year: Number of times played in the last year.
        last_time_played: Date when the song was last played.
        current_gap: Current gap since the song was last played.
        average_gap: Average gap between performances.
        median_gap: Median gap between performances.
        probability: Predicted probability the song will be played (optional).
        features: Dictionary of features that influenced the prediction (optional).
    """
    name: str
    times_played_last_year: Optional[int] = None
    last_time_played: Optional[str] = None
    current_gap: Optional[int] = None
    average_gap: Optional[float] = None
    median_gap: Optional[float] = None
    probability: Optional[float] = None
    features: Optional[Dict[str, Any]] = None

@router.get("/{band_id}/{prediction_type}", response_model=Dict[str, Any])
async def get_predictions(
    band_id: str,
    prediction_type: str = Query(..., description="Type of prediction (notebook or ckplus)"),
    limit: int = Query(50, description="Number of predictions to return")
) -> Dict[str, Any]:
    """
    Get predictions for a specific band.
    
    Args:
        band_id: The band identifier.
        prediction_type: Type of prediction (notebook or ckplus).
        limit: Number of predictions to return.
        
    Returns:
        Dict[str, Any]: Prediction data and metadata.
        
    Raises:
        HTTPException: If band not found or predictions not available.
    """
    # Map band_id to short_name
    band_mapping = {
        "wsp": "WSP",
        "goose": "Goose",
        "phish": "Phish",
        "um": "UM"
    }
    
    if band_id not in band_mapping:
        raise HTTPException(status_code=404, detail=f"Band with id {band_id} not found")
    
    band_short_name = band_mapping[band_id]
    
    # Validate prediction_type
    if prediction_type not in ["notebook", "ckplus"]:
        raise HTTPException(
            status_code=400,
            detail="Prediction type must be 'notebook' or 'ckplus'"
        )
    
    try:
        # Load prediction data
        predictions = load_prediction_data(band_short_name, prediction_type)
        if predictions.empty:
            return {
                "predictions": [],
                "meta": {
                    "band": band_short_name,
                    "type": prediction_type,
                    "last_updated": "Unknown"
                }
            }
        
        # Get last updated time
        last_updated = get_last_updated_time(band_short_name)
        
        # Convert to list of dictionaries
        prediction_list = predictions.head(limit).to_dict(orient="records")
        
        # Format the response
        return {
            "predictions": prediction_list,
            "meta": {
                "band": band_short_name,
                "type": prediction_type,
                "last_updated": last_updated
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving predictions: {str(e)}"
        )
