from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import logging

from models import Vehicle, VehicleAISummary
from utils.database import get_db
from services.vehicle_service import VehicleService
from utils.schemas import VehicleResponse, VehicleSearchResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["vehicles"])

# Initialize service
vehicle_service = VehicleService()

@router.get("/vehicle/vin/{vin}", response_model=VehicleResponse)
async def get_vehicle_by_vin(
    vin: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive vehicle information and AI insights by VIN
    
    Args:
        vin: Vehicle Identification Number (17 characters)
        db: Database session
        
    Returns:
        Complete vehicle data with AI-generated insights
    """
    try:
        # Validate VIN format (basic validation)
        if not vin or len(vin.strip()) != 17:
            raise HTTPException(
                status_code=400, 
                detail="VIN must be exactly 17 characters long"
            )
        
        # Clean the VIN
        clean_vin = vin.strip().upper()
        
        logger.info(f"Searching for vehicle with VIN: {clean_vin}")
        
        # Get comprehensive vehicle data
        vehicle_data = vehicle_service.get_comprehensive_vehicle_data(
            db=db, 
            search_term=clean_vin, 
            search_type="vin"
        )
        
        if not vehicle_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Vehicle with VIN {clean_vin} not found"
            )
        
        logger.info(f"Successfully retrieved vehicle data for VIN: {clean_vin}")
        return vehicle_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vehicle by VIN {vin}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while retrieving vehicle data"
        )

@router.get("/vehicle/vrm/{vrm}", response_model=VehicleResponse)
async def get_vehicle_by_vrm(
    vrm: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive vehicle information and AI insights by VRM (License Plate)
    
    Args:
        vrm: Vehicle Registration Mark (License Plate)
        db: Database session
        
    Returns:
        Complete vehicle data with AI-generated insights
    """
    try:
        # Validate VRM format (basic validation)
        if not vrm or len(vrm.strip()) < 2 or len(vrm.strip()) > 15:
            raise HTTPException(
                status_code=400, 
                detail="VRM must be between 2 and 15 characters long"
            )
        
        # Clean the VRM (remove spaces and convert to uppercase)
        clean_vrm = vrm.strip().replace(" ", "").upper()
        
        logger.info(f"Searching for vehicle with VRM: {clean_vrm}")
        
        # Get comprehensive vehicle data
        vehicle_data = vehicle_service.get_comprehensive_vehicle_data(
            db=db, 
            search_term=clean_vrm, 
            search_type="vrm"
        )
        
        if not vehicle_data:
            raise HTTPException(
                status_code=404, 
                detail=f"Vehicle with VRM {clean_vrm} not found"
            )
        
        logger.info(f"Successfully retrieved vehicle data for VRM: {clean_vrm}")
        return vehicle_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vehicle by VRM {vrm}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while retrieving vehicle data"
        )

@router.get("/vehicle/search", response_model=VehicleSearchResponse)
async def search_vehicles(
    q: str = Query(..., min_length=2, description="Search query (VIN, VRM, make, or model)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Search for vehicles by VIN, VRM, make, or model
    
    Args:
        q: Search query string
        db: Database session
        
    Returns:
        List of matching vehicles with basic information
    """
    try:
        logger.info(f"Searching vehicles with query: {q}")
        
        # Perform search
        results = vehicle_service.search_vehicles(db=db, query=q.strip())
        
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching vehicles: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while searching vehicles"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vehicle-insights-api",
        "timestamp": "2024-06-05T00:00:00Z"
    }

@router.get("/vehicle/{vehicle_id}/refresh-insights")
async def refresh_vehicle_insights(
    vehicle_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Force refresh of AI insights for a specific vehicle
    
    Args:
        vehicle_id: Vehicle ID
        db: Database session
        
    Returns:
        Confirmation of refresh operation
    """
    try:
        # Get vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        # Delete existing cached insights to force regeneration
        db.query(VehicleAISummary).filter(
            VehicleAISummary.vehicle_id == vehicle_id
        ).delete()
        db.commit()
        
        logger.info(f"Refreshed insights cache for vehicle ID: {vehicle_id}")
        
        return {
            "message": "Vehicle insights cache cleared successfully",
            "vehicle_id": vehicle_id,
            "vrm": vehicle.vrm,
            "next_request_will_regenerate": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing insights for vehicle {vehicle_id}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Internal server error while refreshing insights"
        )