"""
Router for band-related endpoints.
"""
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Define model for band data
class Band(BaseModel):
    """
    Data model for band information.
    
    Attributes:
        id: The band identifier.
        name: The full band name.
        short_name: Short code for the band.
        display_name: Display name for the band.
    """
    id: str
    name: str
    short_name: str
    display_name: str

# Band data
BANDS = [
    Band(
        id="wsp",
        name="Widespread Panic",
        short_name="WSP",
        display_name="JoJo's Notebook"
    ),
    Band(
        id="goose",
        name="Goose",
        short_name="Goose",
        display_name="Rick's Notebook"
    ),
    Band(
        id="phish",
        name="Phish",
        short_name="Phish",
        display_name="Trey's Notebook"
    ),
    Band(
        id="um",
        name="Umphrey's McGee",
        short_name="UM",
        display_name="Joel's Notebook"
    )
]

@router.get("/", response_model=List[Band])
async def get_bands() -> List[Band]:
    """
    Get list of all bands.
    
    Returns:
        List[Band]: List of band objects
    """
    return BANDS

@router.get("/{band_id}", response_model=Band)
async def get_band(band_id: str) -> Band:
    """
    Get information for a specific band.
    
    Args:
        band_id: The band identifier
        
    Returns:
        Band: Band information
        
    Raises:
        HTTPException: If band not found
    """
    for band in BANDS:
        if band.id == band_id:
            return band
    raise HTTPException(status_code=404, detail=f"Band with id {band_id} not found")

@router.get("/{band_id}/next-show")
async def get_next_show(band_id: str) -> Dict[str, Any]:
    """
    Get information about the next show for a band.
    
    Args:
        band_id: The band identifier
        
    Returns:
        Dict[str, Any]: Next show information
        
    Raises:
        HTTPException: If band not found or next show info not available
    """
    # First check if band exists
    band = None
    for b in BANDS:
        if b.id == band_id:
            band = b
    
    if not band:
        raise HTTPException(status_code=404, detail=f"Band with id {band_id} not found")
    
    # Get next show info from data file
    from app.utils.data_loader import get_next_show_info
    
    try:
        show_info = get_next_show_info(band.short_name)
        if not show_info:
            return {"message": f"No upcoming shows found for {band.name}"}
        return show_info
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving next show info: {str(e)}"
        )
