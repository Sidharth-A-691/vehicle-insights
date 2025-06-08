from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Date, Index
from sqlalchemy.orm import declarative_base 
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    """
    Main vehicle information table - Core vehicle details
    """
    __tablename__ = 'vehicles'
    
    # Primary identifiers
    id = Column(Integer, primary_key=True, autoincrement=True)
    vin = Column(String(17), unique=True, index=True)  # Vehicle Identification Number
    vrm = Column(String(15), unique=True, index=True)  # Vehicle Registration Mark/License Plate
    
    # Basic vehicle information
    make = Column(String(50))  # e.g., Toyota, Ford, BMW
    model = Column(String(100))  # e.g., Camry, Focus, 3 Series
    variant = Column(String(100))  # Specific variant/trim level
    year = Column(Integer)  # Model year
    registration_date = Column(Date)  # First registration date
    
    # Engine & Technical Details
    engine_size = Column(Float)  # Engine displacement in liters
    fuel_type = Column(String(30))  # Petrol, Diesel, Electric, Hybrid, etc.
    transmission = Column(String(30))  # Manual, Automatic, CVT, etc.
    body_type = Column(String(30))  # Sedan, Hatchback, SUV, etc.
    doors = Column(Integer)  
    seats = Column(Integer)  
    
    # Performance & Efficiency
    engine_power_hp = Column(Integer)  # Horsepower
    engine_power_kw = Column(Integer)  # Kilowatts
    co2_emissions = Column(Float)  # CO2 emissions g/km
    fuel_consumption_urban = Column(Float)  # Urban fuel consumption
    fuel_consumption_extra_urban = Column(Float)  # Extra urban fuel consumption
    fuel_consumption_combined = Column(Float)  # Combined fuel consumption
    
    # Legal & Status Information
    vehicle_status = Column(String(30))  # Active, Scrapped, Exported, etc.
    mot_status = Column(String(30))  # MOT test status
    mot_expiry_date = Column(Date)  # MOT expiry date
    tax_status = Column(String(30))  # Tax status
    tax_due_date = Column(Date)  # Tax due date
    
    # Insurance & Classification
    insurance_group = Column(String(10))  # Insurance group rating
    euro_status = Column(String(30))  # Euro emissions standard
    vehicle_class = Column(String(30))  # Classification for regulatory purposes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    valuations = relationship("VehicleValuation", back_populates="vehicle")
    history_records = relationship("VehicleHistory", back_populates="vehicle")
    recalls = relationship("VehicleRecall", back_populates="vehicle")
    specifications = relationship("VehicleSpecification", back_populates="vehicle")
    ai_summary = relationship("VehicleAISummary", back_populates="vehicle", uselist=False) # One-to-one for summary

    # Example of a multi-column index
    __table_args__ = (
        Index('ix_vehicle_make_model', 'make', 'model'),
    )

class VehicleValuation(Base):
    """
    Vehicle valuation and market data
    """
    __tablename__ = 'vehicle_valuations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True) # Added index
    
    valuation_date = Column(Date)
    retail_value = Column(Float)
    trade_value = Column(Float)
    private_value = Column(Float)
    auction_value = Column(Float)
    mileage_at_valuation = Column(Integer)
    condition_grade = Column(String(10))
    regional_adjustment = Column(Float)
    valuation_source = Column(String(50))
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="valuations")

    __table_args__ = (
        Index('ix_valuation_vehicle_date', 'vehicle_id', 'valuation_date'),
    )

class VehicleHistory(Base):
    """
    Vehicle history events and records
    """
    __tablename__ = 'vehicle_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True) 
    
    event_date = Column(Date)
    event_type = Column(String(50))
    event_description = Column(Text)
    mileage = Column(Integer)
    location = Column(String(100))
    source = Column(String(50))
    pass_fail = Column(String(10))
    advisory_notes = Column(Text)
    cost = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="history_records")

    __table_args__ = (
        Index('ix_history_vehicle_event_date', 'vehicle_id', 'event_date'),
    )

class VehicleRecall(Base):
    """
    Vehicle recall information
    """
    __tablename__ = 'vehicle_recalls'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True) 
    
    recall_number = Column(String(50))
    recall_date = Column(Date)
    recall_title = Column(String(200))
    recall_description = Column(Text)
    safety_issue = Column(Boolean)
    recall_status = Column(String(30))
    completion_date = Column(Date)
    issuing_authority = Column(String(100))
    manufacturer_campaign = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="recalls")

class VehicleSpecification(Base):
    """
    Detailed technical specifications
    """
    __tablename__ = 'vehicle_specifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True) 
    
    length_mm = Column(Integer)
    width_mm = Column(Integer)
    height_mm = Column(Integer)
    wheelbase_mm = Column(Integer)
    kerb_weight_kg = Column(Integer)
    gross_weight_kg = Column(Integer)
    max_towing_weight_kg = Column(Integer)
    fuel_tank_capacity = Column(Float)
    boot_capacity_litres = Column(Integer)
    top_speed_mph = Column(Integer)
    acceleration_0_60_mph = Column(Float)
    drive_type = Column(String(20))
    steering_type = Column(String(30))
    brake_type_front = Column(String(30))
    brake_type_rear = Column(String(30))
    airbags = Column(String(100))
    abs = Column(Boolean)
    esp = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="specifications")


class VehicleAISummary(Base):
    """
    Stores AI-generated user-friendly summaries to avoid regenerating.
    The full AI response (which is a JSON object) is stored in 'insights_json'.
    """
    __tablename__ = 'vehicle_ai_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, index=True) # One summary per vehicle
    
    search_key = Column(String(20), index=True)  # VIN or VRM, for potential direct lookups
    
    # Stores the entire AI-generated JSON response as a string
    insights_json = Column(Text) 
    
    # Simple flags for quick filtering, derived from insights_json or vehicle data
    has_issues = Column(Boolean, default=False)  # Any MOT fails, recalls, etc.
    needs_attention = Column(Boolean, default=False)  # Upcoming MOT, tax, etc.
    
    # Cache metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    llm_model_version = Column(String(50))  # Track which LLM version generated this
    data_hash = Column(String(64), index=True)  # Hash of source data to detect changes
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="ai_summary")

