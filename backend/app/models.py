from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Date, Index, Enum, JSON
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

Base = declarative_base()

class OwnershipChangeType(enum.Enum):
    PRIVATE_TO_PRIVATE = "private_to_private"
    PRIVATE_TO_TRADE = "private_to_trade"
    TRADE_TO_PRIVATE = "trade_to_private"
    TRADE_TO_TRADE = "trade_to_trade"
    LEASE_RETURN = "lease_return"
    FLEET_DISPOSAL = "fleet_disposal"
    AUCTION_SALE = "auction_sale"
    INSURANCE_WRITE_OFF = "insurance_write_off"

class VehicleStatusType(enum.Enum):
    ACTIVE = "active"
    STOLEN = "stolen"
    RECOVERED = "recovered"
    WRITTEN_OFF = "written_off"
    SCRAPPED = "scrapped"
    EXPORTED = "exported"
    SORN = "sorn"
    DESTROYED = "destroyed"

class InsuranceClaimType(enum.Enum):
    THEFT = "theft"
    ACCIDENT = "accident"
    FIRE = "fire"
    FLOOD = "flood"
    VANDALISM = "vandalism"
    WINDSCREEN = "windscreen"
    THIRD_PARTY = "third_party"
    TOTAL_LOSS = "total_loss"

class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vin = Column(String(17), unique=True, index=True)
    vrm = Column(String(15), unique=True, index=True)
    
    make = Column(String(50))
    model = Column(String(100))
    variant = Column(String(100))
    year = Column(Integer)
    registration_date = Column(Date)
    
    engine_size = Column(Float)
    fuel_type = Column(String(30))
    transmission = Column(String(30))
    body_type = Column(String(30))
    doors = Column(Integer)  
    seats = Column(Integer)  
    
    engine_power_hp = Column(Integer)
    engine_power_kw = Column(Integer)
    co2_emissions = Column(Float)
    fuel_consumption_urban = Column(Float)
    fuel_consumption_extra_urban = Column(Float)
    fuel_consumption_combined = Column(Float)
    
    vehicle_status = Column(String(30))
    mot_status = Column(String(30))
    mot_expiry_date = Column(Date)
    tax_status = Column(String(30))
    tax_due_date = Column(Date)
    
    insurance_group = Column(String(10))
    euro_status = Column(String(30))
    vehicle_class = Column(String(30))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    valuations = relationship("VehicleValuation", back_populates="vehicle")
    history_records = relationship("VehicleHistory", back_populates="vehicle")
    recalls = relationship("VehicleRecall", back_populates="vehicle")
    specifications = relationship("VehicleSpecification", back_populates="vehicle")
    ai_summary = relationship("VehicleAISummary", back_populates="vehicle", uselist=False)
    
    ownership_changes = relationship("VehicleOwnershipHistory", back_populates="vehicle")
    theft_records = relationship("VehicleTheftRecord", back_populates="vehicle")
    insurance_claims = relationship("VehicleInsuranceClaim", back_populates="vehicle")
    mileage_records = relationship("VehicleMileageRecord", back_populates="vehicle")
    finance_records = relationship("VehicleFinanceRecord", back_populates="vehicle")
    auction_records = relationship("VehicleAuctionRecord", back_populates="vehicle")
    
    __table_args__ = (
        Index('ix_vehicle_make_model', 'make', 'model'),
        Index('ix_vehicle_make_model_year', 'make', 'model', 'year'),
    )

class VehicleOwnershipHistory(Base):
    __tablename__ = 'vehicle_ownership_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    change_date = Column(Date, nullable=False)
    change_type = Column(Enum(OwnershipChangeType))
    previous_owner_type = Column(String(50))
    new_owner_type = Column(String(50))
    previous_owner_postcode = Column(String(10))
    new_owner_postcode = Column(String(10))
    mileage_at_change = Column(Integer)
    sale_price = Column(Float)
    source = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="ownership_changes")

    __table_args__ = (
        Index('ix_ownership_vehicle_date', 'vehicle_id', 'change_date'),
    )

class VehicleTheftRecord(Base):
    __tablename__ = 'vehicle_theft_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    theft_date = Column(Date)
    recovery_date = Column(Date, nullable=True)
    theft_location_postcode = Column(String(10))
    recovery_location_postcode = Column(String(10), nullable=True)
    theft_circumstances = Column(Text)
    recovery_condition = Column(String(50))
    police_reference = Column(String(50))
    insurance_claim_reference = Column(String(50))
    current_status = Column(Enum(VehicleStatusType))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="theft_records")

    __table_args__ = (
        Index('ix_theft_vehicle_date', 'vehicle_id', 'theft_date'),
    )

class VehicleInsuranceClaim(Base):
    __tablename__ = 'vehicle_insurance_claims'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    claim_date = Column(Date)
    claim_type = Column(Enum(InsuranceClaimType))
    claim_amount = Column(Float)
    settlement_amount = Column(Float)
    incident_location_postcode = Column(String(10))
    fault_claim = Column(Boolean)
    total_loss = Column(Boolean)
    mileage_at_incident = Column(Integer)
    description = Column(Text)
    insurer = Column(String(100))
    claim_reference = Column(String(50))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="insurance_claims")

    __table_args__ = (
        Index('ix_insurance_vehicle_date', 'vehicle_id', 'claim_date'),
    )

class VehicleMileageRecord(Base):
    __tablename__ = 'vehicle_mileage_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    reading_date = Column(Date)
    mileage = Column(Integer)
    source = Column(String(50))
    verified = Column(Boolean, default=False)
    discrepancy_flag = Column(Boolean, default=False)
    previous_mileage = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="mileage_records")

    __table_args__ = (
        Index('ix_mileage_vehicle_date', 'vehicle_id', 'reading_date'),
    )

class VehicleFinanceRecord(Base):
    __tablename__ = 'vehicle_finance_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    finance_start_date = Column(Date)
    finance_end_date = Column(Date)
    finance_type = Column(String(30))
    finance_company = Column(String(100))
    settlement_figure = Column(Float)
    monthly_payment = Column(Float)
    outstanding_finance = Column(Boolean, default=False)
    settlement_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="finance_records")

class VehicleAuctionRecord(Base):
    __tablename__ = 'vehicle_auction_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    auction_date = Column(Date)
    auction_house = Column(String(100))
    lot_number = Column(String(20))
    guide_price_low = Column(Float)
    guide_price_high = Column(Float)
    hammer_price = Column(Float)
    sold = Column(Boolean)
    seller_type = Column(String(50))
    condition_grade = Column(String(10))
    mileage_at_auction = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    vehicle = relationship("Vehicle", back_populates="auction_records")

class VehicleValuation(Base):
    __tablename__ = 'vehicle_valuations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
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
    __tablename__ = 'vehicle_ai_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), unique=True, index=True)
    
    search_key = Column(String(20), index=True)
    insights_json = Column(Text)
    has_issues = Column(Boolean, default=False)
    needs_attention = Column(Boolean, default=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    llm_model_version = Column(String(50))
    data_hash = Column(String(64), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vehicle = relationship("Vehicle", back_populates="ai_summary")

class VehicleClusterAnalysis(Base):
    __tablename__ = 'vehicle_cluster_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    search_query = Column(String(200), index=True)  # e.g., "volkswagen polo", "white sedan"
    search_hash = Column(String(64), unique=True, index=True)  # Hash of normalized search query
    
    total_vehicles_analyzed = Column(Integer)
    clusters_found = Column(Integer)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Store the clustering parameters used
    clustering_algorithm = Column(String(50), default='DBSCAN')
    algorithm_parameters = Column(JSON)  # Store DBSCAN eps, min_samples etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patterns = relationship("VehiclePattern", back_populates="analysis")
    vehicle_clusters = relationship("VehicleClusterMembership", back_populates="analysis")

class VehiclePattern(Base):
    __tablename__ = 'vehicle_patterns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('vehicle_cluster_analysis.id'), index=True)
    
    cluster_id = Column(Integer)  # -1 for outliers in DBSCAN
    pattern_type = Column(String(50))  # 'theft', 'insurance_claim', 'ownership_change', 'high_mileage', etc.
    pattern_description = Column(Text)
    
    # Pattern characteristics
    vehicles_in_pattern = Column(Integer)
    pattern_strength = Column(Float)  # 0-1 score indicating how strong the pattern is
    statistical_significance = Column(Float)  # p-value or confidence score
    
    # Common characteristics of vehicles in this pattern
    common_characteristics = Column(JSON)  # Store dict of common features
    
    # Pattern-specific metrics
    pattern_metrics = Column(JSON)  # Store specific metrics like theft_rate, avg_claim_amount, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis = relationship("VehicleClusterAnalysis", back_populates="patterns")

class VehicleClusterMembership(Base):
    __tablename__ = 'vehicle_cluster_membership'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('vehicle_cluster_analysis.id'), index=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    
    cluster_id = Column(Integer)  # -1 for outliers
    distance_to_centroid = Column(Float)  # How close to cluster center
    
    # Store the vehicle's feature vector used in clustering
    feature_vector = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis = relationship("VehicleClusterAnalysis", back_populates="vehicle_clusters")
    vehicle = relationship("Vehicle")
    
    __table_args__ = (
        Index('ix_cluster_analysis_vehicle', 'analysis_id', 'vehicle_id'),
        Index('ix_cluster_analysis_cluster', 'analysis_id', 'cluster_id'),
    )