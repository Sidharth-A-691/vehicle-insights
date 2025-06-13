from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
import enum

class OwnershipChangeTypeSchema(enum.Enum):
    PRIVATE_TO_PRIVATE = "private_to_private"
    PRIVATE_TO_TRADE = "private_to_trade"
    TRADE_TO_PRIVATE = "trade_to_private"
    TRADE_TO_TRADE = "trade_to_trade"
    LEASE_RETURN = "lease_return"
    FLEET_DISPOSAL = "fleet_disposal"
    AUCTION_SALE = "auction_sale"
    INSURANCE_WRITE_OFF = "insurance_write_off"

class VehicleStatusTypeSchema(enum.Enum):
    ACTIVE = "active"
    STOLEN = "stolen"
    RECOVERED = "recovered"
    WRITTEN_OFF = "written_off"
    SCRAPPED = "scrapped"
    EXPORTED = "exported"
    SORN = "sorn"
    DESTROYED = "destroyed"

class InsuranceClaimTypeSchema(enum.Enum):
    THEFT = "theft"
    ACCIDENT = "accident"
    FIRE = "fire"
    FLOOD = "flood"
    VANDALISM = "vandalism"
    WINDSCREEN = "windscreen"
    THIRD_PARTY = "third_party"
    TOTAL_LOSS = "total_loss"

class VehicleBasicInfo(BaseModel):
    id: int
    vin: Optional[str] = None
    vrm: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    year: Optional[int] = None
    registration_date: Optional[date] = None
    engine_size: Optional[float] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    body_type: Optional[str] = None
    doors: Optional[int] = None
    seats: Optional[int] = None
    engine_power_hp: Optional[int] = None
    engine_power_kw: Optional[int] = None
    co2_emissions: Optional[float] = None
    fuel_consumption_combined: Optional[float] = None
    vehicle_status: Optional[str] = None
    mot_status: Optional[str] = None
    mot_expiry_date: Optional[date] = None
    tax_status: Optional[str] = None
    tax_due_date: Optional[date] = None
    insurance_group: Optional[str] = None
    euro_status: Optional[str] = None
    vehicle_class: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class VehicleValuation(BaseModel):
    valuation_date: Optional[date] = None
    retail_value: Optional[float] = None
    trade_value: Optional[float] = None
    private_value: Optional[float] = None
    auction_value: Optional[float] = None
    mileage_at_valuation: Optional[int] = None
    condition_grade: Optional[str] = None
    regional_adjustment: Optional[float] = None
    valuation_source: Optional[str] = None
    confidence_score: Optional[float] = None

class VehicleHistoryRecord(BaseModel):
    event_date: Optional[date] = None
    event_type: Optional[str] = None
    event_description: Optional[str] = None
    mileage: Optional[int] = None
    location: Optional[str] = None
    source: Optional[str] = None
    pass_fail: Optional[str] = None
    advisory_notes: Optional[str] = None
    cost: Optional[float] = None

class VehicleRecall(BaseModel):
    recall_number: Optional[str] = None
    recall_date: Optional[date] = None
    recall_title: Optional[str] = None
    recall_description: Optional[str] = None
    safety_issue: Optional[bool] = None
    recall_status: Optional[str] = None
    completion_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    manufacturer_campaign: Optional[str] = None

class VehicleSpecification(BaseModel):
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    wheelbase_mm: Optional[int] = None
    kerb_weight_kg: Optional[int] = None
    gross_weight_kg: Optional[int] = None
    max_towing_weight_kg: Optional[int] = None
    fuel_tank_capacity: Optional[float] = None
    boot_capacity_litres: Optional[int] = None
    top_speed_mph: Optional[int] = None
    acceleration_0_60_mph: Optional[float] = None
    drive_type: Optional[str] = None
    steering_type: Optional[str] = None
    brake_type_front: Optional[str] = None
    brake_type_rear: Optional[str] = None
    airbags: Optional[str] = None
    abs: Optional[bool] = None
    esp: Optional[bool] = None

class VehicleOwnershipHistoryItem(BaseModel):
    change_date: date
    change_type: Optional[OwnershipChangeTypeSchema] = None
    previous_owner_type: Optional[str] = None
    new_owner_type: Optional[str] = None
    previous_owner_postcode: Optional[str] = None
    new_owner_postcode: Optional[str] = None
    mileage_at_change: Optional[int] = None
    sale_price: Optional[float] = None
    source: Optional[str] = None

class VehicleTheftRecordItem(BaseModel):
    theft_date: Optional[date] = None
    recovery_date: Optional[date] = None
    theft_location_postcode: Optional[str] = None
    recovery_location_postcode: Optional[str] = None
    theft_circumstances: Optional[str] = None
    recovery_condition: Optional[str] = None
    police_reference: Optional[str] = None
    insurance_claim_reference: Optional[str] = None
    current_status: Optional[VehicleStatusTypeSchema] = None

class VehicleInsuranceClaimItem(BaseModel):
    claim_date: Optional[date] = None
    claim_type: Optional[InsuranceClaimTypeSchema] = None
    claim_amount: Optional[float] = None
    settlement_amount: Optional[float] = None
    incident_location_postcode: Optional[str] = None
    fault_claim: Optional[bool] = None
    total_loss: Optional[bool] = None
    mileage_at_incident: Optional[int] = None
    description: Optional[str] = None
    insurer: Optional[str] = None
    claim_reference: Optional[str] = None

class VehicleMileageRecordItem(BaseModel):
    reading_date: Optional[date] = None
    mileage: Optional[int] = None
    source: Optional[str] = None
    verified: Optional[bool] = None
    discrepancy_flag: Optional[bool] = None
    previous_mileage: Optional[int] = None

class VehicleFinanceRecordItem(BaseModel):
    finance_start_date: Optional[date] = None
    finance_end_date: Optional[date] = None
    finance_type: Optional[str] = None
    finance_company: Optional[str] = None
    settlement_figure: Optional[float] = None
    monthly_payment: Optional[float] = None
    outstanding_finance: Optional[bool] = None
    settlement_date: Optional[date] = None

class VehicleAuctionRecordItem(BaseModel):
    auction_date: Optional[date] = None
    auction_house: Optional[str] = None
    lot_number: Optional[str] = None
    guide_price_low: Optional[float] = None
    guide_price_high: Optional[float] = None
    hammer_price: Optional[float] = None
    sold: Optional[bool] = None
    seller_type: Optional[str] = None
    condition_grade: Optional[str] = None
    mileage_at_auction: Optional[int] = None

class ReliabilityAssessment(BaseModel):
    score: Union[int, str] = Field(..., description="Reliability score 1-10 or N/A")
    explanation: str = Field(..., description="Explanation of the reliability rating")

class ValueAssessment(BaseModel):
    current_market_position: str = Field(..., description="Current market position")
    factors_affecting_value: str = Field(..., description="Factors affecting vehicle value")
    score: str = Field(..., description="Value assessment score 1-10 or N/A")
    roi: str = Field(..., description="Return on Investment of this vehicle based on all the valuation data provided") 

class CostInsights(BaseModel):
    typical_maintenance: str = Field(..., description="Typical maintenance costs")
    insurance_notes: str = Field(..., description="Insurance cost notes")
    fuel_efficiency: str = Field(..., description="Fuel efficiency information")

class AIInsights(BaseModel):
    summary: str = Field(..., description="User-friendly vehicle summary")
    overall_score: str = Field(..., description="An overall score based on all the data")
    overall_score_explaination:  str = Field(..., description="Explaination for the score given")
    key_insights: List[str] = Field(default_factory=list, description="Key insights about the vehicle")
    owner_advice: str = Field(..., description="Personalized advice for the owner")
    reliability_assessment: Optional[ReliabilityAssessment] = None
    value_assessment: Optional[ValueAssessment] = None
    attention_items: List[str] = Field(default_factory=list, description="Items needing attention")
    cost_insights: Optional[CostInsights] = None
    technical_highlights: List[str] = Field(default_factory=list, description="Technical highlights")
    generated_at: Optional[str] = None
    model_version: Optional[str] = None
    cached: Optional[bool] = None
    error: Optional[bool] = None

class VehicleDetailedData(BaseModel):
    basic: VehicleBasicInfo
    valuations: List[VehicleValuation] = Field(default_factory=list)
    history: List[VehicleHistoryRecord] = Field(default_factory=list)
    recalls: List[VehicleRecall] = Field(default_factory=list)
    specifications: Optional[VehicleSpecification] = None
    ownership_history: List[VehicleOwnershipHistoryItem] = Field(default_factory=list)
    theft_records: List[VehicleTheftRecordItem] = Field(default_factory=list)
    insurance_claims: List[VehicleInsuranceClaimItem] = Field(default_factory=list)
    mileage_records: List[VehicleMileageRecordItem] = Field(default_factory=list)
    finance_records: List[VehicleFinanceRecordItem] = Field(default_factory=list)
    auction_records: List[VehicleAuctionRecordItem] = Field(default_factory=list)

class VehicleResponse(BaseModel):
    vehicle_id: int
    search_term: str
    search_type: str
    ai_insights: AIInsights
    detailed_data: VehicleDetailedData
    last_updated: str

    class Config:
        from_attributes = True

class VehicleSearchResult(BaseModel):
    id: int
    vin: Optional[str] = None
    vrm: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_status: Optional[str] = None

class VehicleSearchResponse(BaseModel):
    query: str
    results: List[VehicleSearchResult]
    count: int

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str

class RefreshInsightsResponse(BaseModel):
    message: str
    vehicle_id: int
    vrm: Optional[str] # VRM can be None
    next_request_will_regenerate: bool