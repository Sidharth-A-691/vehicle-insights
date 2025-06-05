from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date

class VehicleBasicInfo(BaseModel):
    """Basic vehicle information schema"""
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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class VehicleValuation(BaseModel):
    """Vehicle valuation schema"""
    valuation_date: Optional[date] = None
    retail_value: Optional[float] = None
    trade_value: Optional[float] = None
    private_value: Optional[float] = None
    auction_value: Optional[float] = None
    mileage_at_valuation: Optional[int] = None
    condition_grade: Optional[str] = None
    valuation_source: Optional[str] = None
    confidence_score: Optional[float] = None

class VehicleHistoryRecord(BaseModel):
    """Vehicle history record schema"""
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
    """Vehicle recall schema"""
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
    """Vehicle specification schema"""
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

class ReliabilityAssessment(BaseModel):
    """Reliability assessment schema"""
    score: Union[int, str] = Field(..., description="Reliability score 1-10 or N/A")
    explanation: str = Field(..., description="Explanation of the reliability rating")

class ValueAssessment(BaseModel):
    """Value assessment schema"""
    current_market_position: str = Field(..., description="Current market position")
    factors_affecting_value: str = Field(..., description="Factors affecting vehicle value")

class CostInsights(BaseModel):
    """Cost insights schema"""
    typical_maintenance: str = Field(..., description="Typical maintenance costs")
    insurance_notes: str = Field(..., description="Insurance cost notes")
    fuel_efficiency: str = Field(..., description="Fuel efficiency information")

class AIInsights(BaseModel):
    """AI-generated insights schema"""
    summary: str = Field(..., description="User-friendly vehicle summary")
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
    """Detailed vehicle data schema"""
    basic: VehicleBasicInfo
    valuations: List[VehicleValuation] = Field(default_factory=list)
    history: List[VehicleHistoryRecord] = Field(default_factory=list)
    recalls: List[VehicleRecall] = Field(default_factory=list)
    specifications: Optional[VehicleSpecification] = None

class VehicleResponse(BaseModel):
    """Complete vehicle response schema"""
    vehicle_id: int
    search_term: str
    search_type: str
    ai_insights: AIInsights
    detailed_data: VehicleDetailedData
    last_updated: str

    class Config:
        from_attributes = True

class VehicleSearchResult(BaseModel):
    """Individual vehicle search result schema"""
    id: int
    vin: Optional[str] = None
    vrm: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_status: Optional[str] = None

class VehicleSearchResponse(BaseModel):
    """Vehicle search response schema"""
    query: str
    results: List[VehicleSearchResult]
    count: int

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    service: str
    timestamp: str

class RefreshInsightsResponse(BaseModel):
    """Refresh insights response schema"""
    message: str
    vehicle_id: int
    vrm: str
    next_request_will_regenerate: bool