from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, date, timezone
import json

from models import (
    Vehicle, VehicleAISummary 
)
from services.ai_service import VehicleAIService

logger = logging.getLogger(__name__)

class VehicleService:
    """Service class for vehicle-related operations"""
    
    def __init__(self):
        self.ai_service = VehicleAIService()
    
    def get_vehicle_by_vin(self, db: Session, vin: str) -> Optional[Vehicle]:
        """Get vehicle by VIN with all related data including AI summary."""
        return db.query(Vehicle).options(
            joinedload(Vehicle.valuations),
            joinedload(Vehicle.history_records),
            joinedload(Vehicle.recalls),
            joinedload(Vehicle.specifications), 
            joinedload(Vehicle.ai_summary)    
        ).filter(Vehicle.vin == vin.upper()).first()
    
    def get_vehicle_by_vrm(self, db: Session, vrm: str) -> Optional[Vehicle]:
        """Get vehicle by VRM with all related data including AI summary."""
        return db.query(Vehicle).options(
            joinedload(Vehicle.valuations),
            joinedload(Vehicle.history_records),
            joinedload(Vehicle.recalls),
            joinedload(Vehicle.specifications), 
            joinedload(Vehicle.ai_summary)    
        ).filter(Vehicle.vrm == vrm.upper()).first()
    
    def get_comprehensive_vehicle_data(self, db: Session, search_term: str, search_type: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive vehicle data including AI insights.
        """
        try:
            if search_type.lower() == 'vin':
                vehicle = self.get_vehicle_by_vin(db, search_term)
            else:
                vehicle = self.get_vehicle_by_vrm(db, search_term)
            
            if not vehicle:
                logger.info(f"Vehicle not found for {search_type}: {search_term}")
                return None
            
            vehicle_data_dict = self._vehicle_to_dict(vehicle)
            # ai_insights_dict will be the full JSON structure from AI service or cache
            ai_insights_dict = self._get_or_generate_ai_insights(db, vehicle, vehicle_data_dict)
            
            comprehensive_data = {
                "vehicle_id": vehicle.id,
                "search_term": search_term.upper(),
                "search_type": search_type,
                "ai_insights": ai_insights_dict,
                "detailed_data": vehicle_data_dict,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error in get_comprehensive_vehicle_data for {search_type} {search_term}: {str(e)}", exc_info=True)
            return None
    
    def _vehicle_to_dict(self, vehicle: Vehicle) -> Dict[str, Any]:
        """
        Convert vehicle SQLAlchemy object and its relationships to a dictionary.
        This forms the 'detailed_data' part of the API response.
        """
        basic_info = {
            "id": vehicle.id, "vin": vehicle.vin, "vrm": vehicle.vrm, "make": vehicle.make,
            "model": vehicle.model, "variant": vehicle.variant, "year": vehicle.year,
            "registration_date": vehicle.registration_date, "engine_size": vehicle.engine_size,
            "fuel_type": vehicle.fuel_type, "transmission": vehicle.transmission,
            "body_type": vehicle.body_type, "doors": vehicle.doors, "seats": vehicle.seats,
            "engine_power_hp": vehicle.engine_power_hp, "engine_power_kw": vehicle.engine_power_kw,
            "co2_emissions": vehicle.co2_emissions,
            "fuel_consumption_combined": vehicle.fuel_consumption_combined,
            "vehicle_status": vehicle.vehicle_status, "mot_status": vehicle.mot_status,
            "mot_expiry_date": vehicle.mot_expiry_date, "tax_status": vehicle.tax_status,
            "tax_due_date": vehicle.tax_due_date, "insurance_group": vehicle.insurance_group,
            "euro_status": vehicle.euro_status, "created_at": vehicle.created_at,
            "updated_at": vehicle.updated_at
        }
        
        valuations = [{
            "valuation_date": val.valuation_date, "retail_value": val.retail_value,
            "trade_value": val.trade_value, "private_value": val.private_value,
            "auction_value": val.auction_value, "mileage_at_valuation": val.mileage_at_valuation,
            "condition_grade": val.condition_grade, "valuation_source": val.valuation_source,
            "confidence_score": val.confidence_score
        } for val in vehicle.valuations] if vehicle.valuations else []
        
        history = [{
            "event_date": hist.event_date, "event_type": hist.event_type,
            "event_description": hist.event_description, "mileage": hist.mileage,
            "location": hist.location, "source": hist.source, "pass_fail": hist.pass_fail,
            "advisory_notes": hist.advisory_notes, "cost": hist.cost
        } for hist in vehicle.history_records] if vehicle.history_records else []
        
        recalls = [{
            "recall_number": recall.recall_number, "recall_date": recall.recall_date,
            "recall_title": recall.recall_title, "recall_description": recall.recall_description,
            "safety_issue": recall.safety_issue, "recall_status": recall.recall_status,
            "completion_date": recall.completion_date, "issuing_authority": recall.issuing_authority,
            "manufacturer_campaign": recall.manufacturer_campaign
        } for recall in vehicle.recalls] if vehicle.recalls else []
        
        specifications_dict = {}
        
        if vehicle.specifications and vehicle.specifications[0]: 
            spec = vehicle.specifications[0]
            specifications_dict = {
                "length_mm": spec.length_mm, "width_mm": spec.width_mm, "height_mm": spec.height_mm,
                "wheelbase_mm": spec.wheelbase_mm, "kerb_weight_kg": spec.kerb_weight_kg,
                "gross_weight_kg": spec.gross_weight_kg, "max_towing_weight_kg": spec.max_towing_weight_kg,
                "fuel_tank_capacity": spec.fuel_tank_capacity, "boot_capacity_litres": spec.boot_capacity_litres,
                "top_speed_mph": spec.top_speed_mph, "acceleration_0_60_mph": spec.acceleration_0_60_mph,
                "drive_type": spec.drive_type, "steering_type": spec.steering_type,
                "brake_type_front": spec.brake_type_front, "brake_type_rear": spec.brake_type_rear,
                "airbags": spec.airbags, "abs": spec.abs, "esp": spec.esp
            }
        
        return {
            "basic": basic_info,
            "valuations": valuations,
            "history": history,
            "recalls": recalls,
            "specifications": specifications_dict if specifications_dict else None
        }
    
    def _get_or_generate_ai_insights(self, db: Session, vehicle: Vehicle, vehicle_data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get cached AI insights (from insights_json) or generate new ones.
        The structure of the returned dictionary aims to match the AIInsights Pydantic schema.
        """
        try:
            cached_summary_model = vehicle.ai_summary # From eager loading

            should_regenerate = self.ai_service.should_regenerate_insights(cached_summary_model, vehicle_data_dict)
            
            if not should_regenerate and cached_summary_model and cached_summary_model.insights_json:
                logger.info(f"Using cached AI insights (from insights_json) for vehicle {vehicle.vrm or vehicle.vin}")
                try:
                    # Parse the stored JSON string to get the full insights dictionary
                    insights_from_cache = json.loads(cached_summary_model.insights_json)
                    # Augment with cache metadata
                    insights_from_cache["generated_at"] = cached_summary_model.generated_at.isoformat() + "Z"
                    insights_from_cache["model_version"] = cached_summary_model.llm_model_version
                    insights_from_cache["cached"] = True
                    insights_from_cache["error"] = insights_from_cache.get("error", False) # Preserve error flag if any
                    return insights_from_cache
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse cached insights_json for vehicle {vehicle.id}. Regenerating.", exc_info=True)
                    # Fall through to regenerate if JSON is corrupt
            
            logger.info(f"Generating new AI insights for vehicle {vehicle.vrm or vehicle.vin}")
            fresh_insights = self.ai_service.generate_vehicle_insights(vehicle_data_dict)
            
            if fresh_insights.get("error"):
                 logger.warning(f"AI service returned fallback/error insights for {vehicle.vrm or vehicle.vin}")
            else:
                # Cache the newly generated insights (which is a dict)
                self._cache_ai_insights(db, vehicle, fresh_insights, vehicle_data_dict)
            
            fresh_insights["cached"] = False # Mark as not from cache for this response
            return fresh_insights
            
        except Exception as e:
            logger.error(f"Error in _get_or_generate_ai_insights for vehicle {vehicle.id}: {str(e)}", exc_info=True)
            return self.ai_service._get_fallback_insights(vehicle_data_dict)
    
    def _cache_ai_insights(self, db: Session, vehicle: Vehicle, insights_dict: Dict[str, Any], vehicle_data_dict: Dict[str, Any]):
        """
        Cache AI insights in the VehicleAISummary table, storing the full insights_dict as JSON.
        """
        try:
            existing_summary = db.query(VehicleAISummary).filter(VehicleAISummary.vehicle_id == vehicle.id).first()
            
            # Derive flags from the full insights_dict and vehicle_data_dict
            has_issues = self._check_has_issues(vehicle_data_dict, insights_dict)
            needs_attention = self._check_needs_attention(vehicle_data_dict, insights_dict)
            
            current_time = datetime.now(timezone.utc)
            # Get generated_at from insights if available, otherwise use current time
            generated_at_str = insights_dict.get("generated_at") 
            generated_at_dt = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00")) if generated_at_str else current_time

            # Prepare the JSON string to be stored
            insights_json_to_store = json.dumps(insights_dict)

            if existing_summary:
                existing_summary.search_key = vehicle.vrm or vehicle.vin
                existing_summary.insights_json = insights_json_to_store 
                existing_summary.has_issues = has_issues
                existing_summary.needs_attention = needs_attention
                existing_summary.generated_at = generated_at_dt
                existing_summary.llm_model_version = insights_dict.get("model_version", "unknown")
                existing_summary.data_hash = self.ai_service.calculate_data_hash(vehicle_data_dict)
                existing_summary.updated_at = current_time
            else:
                new_summary = VehicleAISummary(
                    vehicle_id=vehicle.id,
                    search_key=vehicle.vrm or vehicle.vin,
                    insights_json=insights_json_to_store, 
                    has_issues=has_issues,
                    needs_attention=needs_attention,
                    generated_at=generated_at_dt,
                    llm_model_version=insights_dict.get("model_version", "unknown"),
                    data_hash=self.ai_service.calculate_data_hash(vehicle_data_dict),
                    created_at=current_time,
                    updated_at=current_time
                )
                db.add(new_summary)
            
            db.commit()
            logger.info(f"Cached AI insights (as JSON) for vehicle {vehicle.id} ({vehicle.vrm or vehicle.vin})")
            
        except Exception as e:
            logger.error(f"Error caching AI insights for vehicle {vehicle.id}: {str(e)}", exc_info=True)
            db.rollback()
    
    def _check_has_issues(self, vehicle_data_dict: Dict[str, Any], insights_dict: Dict[str, Any]) -> bool:
        """Check if vehicle has any significant issues based on data and AI insights."""
        history = vehicle_data_dict.get("history", [])
        for record in history:
            if record.get("event_type", "").upper() == "MOT" and record.get("pass_fail", "").upper() == "FAIL":
                return True
        
        recalls = vehicle_data_dict.get("recalls", [])
        for recall in recalls:
            if recall.get("recall_status", "").lower() in ["outstanding", "not completed", "open"]: 
                return True
        
        attention_items = insights_dict.get("attention_items", [])
        if any("critical" in item.lower() or "safety recall" in item.lower() for item in attention_items):
            return True
        
        reliability_assessment = insights_dict.get("reliability_assessment", {})
        if isinstance(reliability_assessment, dict) and reliability_assessment.get("score"):
            try:
                if int(reliability_assessment["score"]) <= 3: 
                    return True
            except (ValueError, TypeError): 
                pass
        return False
    
    def _check_needs_attention(self, vehicle_data_dict: Dict[str, Any], insights_dict: Dict[str, Any]) -> bool:
        """Check if vehicle needs immediate or upcoming attention (e.g., MOT/Tax due soon)."""
        basic = vehicle_data_dict.get("basic", {})
        today = datetime.now(timezone.utc).date()

        for date_key in ["mot_expiry_date", "tax_due_date"]:
            due_date_val = basic.get(date_key)
            if due_date_val:
                due_date_obj: Optional[date] = None
                if isinstance(due_date_val, date):
                    due_date_obj = due_date_val
                elif isinstance(due_date_val, str): 
                    try:
                        due_date_obj = datetime.strptime(due_date_val, "%Y-%m-%d").date()
                    except ValueError:
                        logger.warning(f"Invalid date string for {date_key}: {due_date_val}")
                
                if due_date_obj and (due_date_obj - today).days <= 30: # Within 30 days
                    return True
        
        # Check AI insights (insights_dict) for other attention items
        attention_items = insights_dict.get("attention_items", [])
        if attention_items and len(attention_items) > 0:
            return True 

        return False
    
    def search_vehicles(self, db: Session, query: str) -> List[Dict[str, Any]]:
        """Search vehicles by VIN, VRM, make, or model."""
        clean_query = f"%{query.strip().upper()}%" 
        vehicles = db.query(Vehicle).filter(
            or_(
                Vehicle.vin.ilike(clean_query), 
                Vehicle.vrm.ilike(clean_query),
                Vehicle.make.ilike(clean_query),
                Vehicle.model.ilike(clean_query)
            )
        ).limit(10).all()
        
        return [{
            "id": v.id, "vin": v.vin, "vrm": v.vrm, "make": v.make,
            "model": v.model, "year": v.year, "vehicle_status": v.vehicle_status
        } for v in vehicles]