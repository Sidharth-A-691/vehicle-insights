from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, date, timezone
import json

from models import (
    Vehicle, VehicleAISummary, OwnershipChangeType, VehicleStatusType, InsuranceClaimType
)
from services.ai_service import VehicleAIService

logger = logging.getLogger(__name__)

class VehicleService:
    def __init__(self):
        self.ai_service = VehicleAIService()
    
    def _get_vehicle_query(self, db: Session):
        return db.query(Vehicle).options(
            joinedload(Vehicle.valuations),
            joinedload(Vehicle.history_records),
            joinedload(Vehicle.recalls),
            joinedload(Vehicle.specifications), 
            joinedload(Vehicle.ai_summary),
            joinedload(Vehicle.ownership_changes),
            joinedload(Vehicle.theft_records),
            joinedload(Vehicle.insurance_claims),
            joinedload(Vehicle.mileage_records),
            joinedload(Vehicle.finance_records),
            joinedload(Vehicle.auction_records)
        )

    def get_vehicle_by_vin(self, db: Session, vin: str) -> Optional[Vehicle]:
        return self._get_vehicle_query(db).filter(Vehicle.vin == vin.upper()).first()
    
    def get_vehicle_by_vrm(self, db: Session, vrm: str) -> Optional[Vehicle]:
        return self._get_vehicle_query(db).filter(Vehicle.vrm == vrm.upper()).first()
    
    def get_comprehensive_vehicle_data(self, db: Session, search_term: str, search_type: str) -> Optional[Dict[str, Any]]:
        try:
            if search_type.lower() == 'vin':
                vehicle = self.get_vehicle_by_vin(db, search_term)
            else:
                vehicle = self.get_vehicle_by_vrm(db, search_term)
            
            if not vehicle:
                logger.info(f"Vehicle not found for {search_type}: {search_term}")
                return None
            
            vehicle_data_dict = self._vehicle_to_dict(vehicle)
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
            "euro_status": vehicle.euro_status, "vehicle_class": vehicle.vehicle_class,
            "created_at": vehicle.created_at, "updated_at": vehicle.updated_at
        }
        
        valuations = [{
            "valuation_date": val.valuation_date, "retail_value": val.retail_value,
            "trade_value": val.trade_value, "private_value": val.private_value,
            "auction_value": val.auction_value, "mileage_at_valuation": val.mileage_at_valuation,
            "condition_grade": val.condition_grade, "valuation_source": val.valuation_source,
            "confidence_score": val.confidence_score, "regional_adjustment": val.regional_adjustment
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

        ownership_history = [{
            "change_date": oh.change_date, 
            "change_type": oh.change_type.value if oh.change_type else None,
            "previous_owner_type": oh.previous_owner_type, "new_owner_type": oh.new_owner_type,
            "previous_owner_postcode": oh.previous_owner_postcode, "new_owner_postcode": oh.new_owner_postcode,
            "mileage_at_change": oh.mileage_at_change, "sale_price": oh.sale_price, "source": oh.source
        } for oh in vehicle.ownership_changes] if vehicle.ownership_changes else []

        theft_records = [{
            "theft_date": tr.theft_date, "recovery_date": tr.recovery_date,
            "theft_location_postcode": tr.theft_location_postcode,
            "recovery_location_postcode": tr.recovery_location_postcode,
            "theft_circumstances": tr.theft_circumstances, "recovery_condition": tr.recovery_condition,
            "police_reference": tr.police_reference, "insurance_claim_reference": tr.insurance_claim_reference,
            "current_status": tr.current_status.value if tr.current_status else None
        } for tr in vehicle.theft_records] if vehicle.theft_records else []

        insurance_claims = [{
            "claim_date": ic.claim_date, "claim_type": ic.claim_type.value if ic.claim_type else None,
            "claim_amount": ic.claim_amount, "settlement_amount": ic.settlement_amount,
            "incident_location_postcode": ic.incident_location_postcode, "fault_claim": ic.fault_claim,
            "total_loss": ic.total_loss, "mileage_at_incident": ic.mileage_at_incident,
            "description": ic.description, "insurer": ic.insurer, "claim_reference": ic.claim_reference
        } for ic in vehicle.insurance_claims] if vehicle.insurance_claims else []

        mileage_records = [{
            "reading_date": mr.reading_date, "mileage": mr.mileage, "source": mr.source,
            "verified": mr.verified, "discrepancy_flag": mr.discrepancy_flag,
            "previous_mileage": mr.previous_mileage
        } for mr in vehicle.mileage_records] if vehicle.mileage_records else []
        
        finance_records = [{
            "finance_start_date": fr.finance_start_date, "finance_end_date": fr.finance_end_date,
            "finance_type": fr.finance_type, "finance_company": fr.finance_company,
            "settlement_figure": fr.settlement_figure, "monthly_payment": fr.monthly_payment,
            "outstanding_finance": fr.outstanding_finance, "settlement_date": fr.settlement_date
        } for fr in vehicle.finance_records] if vehicle.finance_records else []

        auction_records = [{
            "auction_date": ar.auction_date, "auction_house": ar.auction_house, "lot_number": ar.lot_number,
            "guide_price_low": ar.guide_price_low, "guide_price_high": ar.guide_price_high,
            "hammer_price": ar.hammer_price, "sold": ar.sold, "seller_type": ar.seller_type,
            "condition_grade": ar.condition_grade, "mileage_at_auction": ar.mileage_at_auction
        } for ar in vehicle.auction_records] if vehicle.auction_records else []
        
        return {
            "basic": basic_info,
            "valuations": valuations,
            "history": history,
            "recalls": recalls,
            "specifications": specifications_dict if specifications_dict else None,
            "ownership_history": ownership_history,
            "theft_records": theft_records,
            "insurance_claims": insurance_claims,
            "mileage_records": mileage_records,
            "finance_records": finance_records,
            "auction_records": auction_records
        }
    
    def _get_or_generate_ai_insights(self, db: Session, vehicle: Vehicle, vehicle_data_dict: Dict[str, Any]) -> Dict[str, Any]:
        try:
            cached_summary_model = vehicle.ai_summary

            should_regenerate = self.ai_service.should_regenerate_insights(cached_summary_model, vehicle_data_dict)
            
            if not should_regenerate and cached_summary_model and cached_summary_model.insights_json:
                logger.info(f"Using cached AI insights (from insights_json) for vehicle {vehicle.vrm or vehicle.vin}")
                try:
                    insights_from_cache = json.loads(cached_summary_model.insights_json)
                    insights_from_cache["generated_at"] = cached_summary_model.generated_at.isoformat() + "Z"
                    insights_from_cache["model_version"] = cached_summary_model.llm_model_version
                    insights_from_cache["cached"] = True
                    insights_from_cache["error"] = insights_from_cache.get("error", False)
                    return insights_from_cache
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse cached insights_json for vehicle {vehicle.id}. Regenerating.", exc_info=True)
            
            logger.info(f"Generating new AI insights for vehicle {vehicle.vrm or vehicle.vin}")
            fresh_insights = self.ai_service.generate_vehicle_insights(vehicle_data_dict)
            
            if fresh_insights.get("error"):
                 logger.warning(f"AI service returned fallback/error insights for {vehicle.vrm or vehicle.vin}")
            else:
                self._cache_ai_insights(db, vehicle, fresh_insights, vehicle_data_dict)
            
            fresh_insights["cached"] = False
            return fresh_insights
            
        except Exception as e:
            logger.error(f"Error in _get_or_generate_ai_insights for vehicle {vehicle.id}: {str(e)}", exc_info=True)
            return self.ai_service._get_fallback_insights(vehicle_data_dict)
    
    def _cache_ai_insights(self, db: Session, vehicle: Vehicle, insights_dict: Dict[str, Any], vehicle_data_dict: Dict[str, Any]):
        try:
            existing_summary = db.query(VehicleAISummary).filter(VehicleAISummary.vehicle_id == vehicle.id).first()
            
            has_issues = self._check_has_issues(vehicle_data_dict, insights_dict)
            needs_attention = self._check_needs_attention(vehicle_data_dict, insights_dict)
            
            current_time = datetime.now(timezone.utc)
            generated_at_str = insights_dict.get("generated_at") 
            generated_at_dt = datetime.fromisoformat(generated_at_str.replace("Z", "+00:00")) if generated_at_str else current_time

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
        history = vehicle_data_dict.get("history", [])
        for record in history:
            if record.get("event_type", "").upper() == "MOT" and record.get("pass_fail", "").upper() == "FAIL":
                return True
        
        recalls = vehicle_data_dict.get("recalls", [])
        for recall in recalls:
            if recall.get("recall_status", "").lower() in ["outstanding", "not completed", "open"]: 
                return True

        theft_records = vehicle_data_dict.get("theft_records", [])
        for theft in theft_records:
            if theft.get("current_status") == VehicleStatusType.STOLEN.value:
                return True
        
        insurance_claims = vehicle_data_dict.get("insurance_claims", [])
        for claim in insurance_claims:
            if claim.get("total_loss"):
                return True
        
        finance_records = vehicle_data_dict.get("finance_records", [])
        for finance in finance_records:
            if finance.get("outstanding_finance"):
                return True

        attention_items = insights_dict.get("attention_items", [])
        if any("critical" in item.lower() or "safety recall" in item.lower() or "stolen" in item.lower() or "outstanding finance" in item.lower() for item in attention_items):
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
                
                if due_date_obj and (due_date_obj - today).days <= 30:
                    return True
        
        finance_records = vehicle_data_dict.get("finance_records", [])
        for finance in finance_records:
            if finance.get("outstanding_finance"):
                return True
            if finance.get("finance_end_date"):
                end_date_obj: Optional[date] = None
                if isinstance(finance["finance_end_date"], date):
                    end_date_obj = finance["finance_end_date"]
                elif isinstance(finance["finance_end_date"], str):
                    try:
                        end_date_obj = datetime.strptime(finance["finance_end_date"], "%Y-%m-%d").date()
                    except ValueError:
                        pass
                if end_date_obj and (end_date_obj - today).days <= 60: # Finance ending in 60 days
                    return True
        
        attention_items = insights_dict.get("attention_items", [])
        if attention_items and len(attention_items) > 0:
            if any("MOT due" in item or "Tax due" in item or "finance ending" in item or "outstanding recall" in item for item in attention_items):
                return True

        return False
    
    def search_vehicles(self, db: Session, query: str) -> List[Dict[str, Any]]:
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