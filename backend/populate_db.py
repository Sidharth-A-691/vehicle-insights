import os
import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Date, Index, Enum as SQLAlchemyEnum, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError
import enum

DATABASE_URL = "mysql+pymysql://root:system@localhost/vehicleinsights"

Base = declarative_base()

# Enums from your new models.py
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

# MODELS DEFINITION (incorporating your new tables)
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
    vehicle_status = Column(String(30)) # This might be overridden by theft/write-off
    mot_status = Column(String(30))
    mot_expiry_date = Column(Date)
    tax_status = Column(String(30))
    tax_due_date = Column(Date)
    insurance_group = Column(String(10))
    euro_status = Column(String(30))
    vehicle_class = Column(String(30))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    valuations = relationship("VehicleValuation", back_populates="vehicle", cascade="all, delete-orphan")
    history_records = relationship("VehicleHistory", back_populates="vehicle", cascade="all, delete-orphan")
    recalls = relationship("VehicleRecall", back_populates="vehicle", cascade="all, delete-orphan")
    specifications = relationship("VehicleSpecification", back_populates="vehicle", cascade="all, delete-orphan")
    ai_summary = relationship("VehicleAISummary", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")

    ownership_changes = relationship("VehicleOwnershipHistory", back_populates="vehicle", cascade="all, delete-orphan")
    theft_records = relationship("VehicleTheftRecord", back_populates="vehicle", cascade="all, delete-orphan")
    insurance_claims = relationship("VehicleInsuranceClaim", back_populates="vehicle", cascade="all, delete-orphan")
    mileage_records = relationship("VehicleMileageRecord", back_populates="vehicle", cascade="all, delete-orphan")
    finance_records = relationship("VehicleFinanceRecord", back_populates="vehicle", cascade="all, delete-orphan")
    auction_records = relationship("VehicleAuctionRecord", back_populates="vehicle", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_vehicle_make_model', 'make', 'model'),
        Index('ix_vehicle_make_model_year', 'make', 'model', 'year'),
    )

class VehicleOwnershipHistory(Base):
    __tablename__ = 'vehicle_ownership_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    change_date = Column(Date, nullable=False)
    change_type = Column(SQLAlchemyEnum(OwnershipChangeType))
    previous_owner_type = Column(String(50))
    new_owner_type = Column(String(50))
    previous_owner_postcode = Column(String(10))
    new_owner_postcode = Column(String(10))
    mileage_at_change = Column(Integer)
    sale_price = Column(Float)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicle = relationship("Vehicle", back_populates="ownership_changes")
    __table_args__ = (Index('ix_ownership_vehicle_date', 'vehicle_id', 'change_date'),)

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
    current_status = Column(SQLAlchemyEnum(VehicleStatusType)) # e.g. STOLEN, RECOVERED
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicle = relationship("Vehicle", back_populates="theft_records")
    __table_args__ = (Index('ix_theft_vehicle_date', 'vehicle_id', 'theft_date'),)

class VehicleInsuranceClaim(Base):
    __tablename__ = 'vehicle_insurance_claims'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    claim_date = Column(Date)
    claim_type = Column(SQLAlchemyEnum(InsuranceClaimType))
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
    __table_args__ = (Index('ix_insurance_vehicle_date', 'vehicle_id', 'claim_date'),)

class VehicleMileageRecord(Base):
    __tablename__ = 'vehicle_mileage_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    reading_date = Column(Date)
    mileage = Column(Integer)
    source = Column(String(50))
    verified = Column(Boolean, default=False)
    discrepancy_flag = Column(Boolean, default=False)
    previous_mileage = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicle = relationship("Vehicle", back_populates="mileage_records")
    __table_args__ = (Index('ix_mileage_vehicle_date', 'vehicle_id', 'reading_date'),)

class VehicleFinanceRecord(Base):
    __tablename__ = 'vehicle_finance_records'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    finance_start_date = Column(Date)
    finance_end_date = Column(Date, nullable=True)
    finance_type = Column(String(30))
    finance_company = Column(String(100))
    settlement_figure = Column(Float, nullable=True)
    monthly_payment = Column(Float, nullable=True)
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
    hammer_price = Column(Float, nullable=True)
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
    __table_args__ = (Index('ix_valuation_vehicle_date', 'vehicle_id', 'valuation_date'),)

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
    pass_fail = Column(String(10), nullable=True)
    advisory_notes = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicle = relationship("Vehicle", back_populates="history_records")
    __table_args__ = (Index('ix_history_vehicle_event_date', 'vehicle_id', 'event_date'),)

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
    completion_date = Column(Date, nullable=True)
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

class VehicleClusterAnalytics(Base):
    __tablename__ = 'vehicle_cluster_analytics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    make = Column(String(50), index=True)
    model = Column(String(100), index=True)
    year_range_start = Column(Integer)
    year_range_end = Column(Integer)
    body_type = Column(String(30), nullable=True)
    total_vehicles_analyzed = Column(Integer)
    theft_rate_percentage = Column(Float, nullable=True)
    most_common_theft_location = Column(String(50), nullable=True)
    avg_days_to_recovery = Column(Float, nullable=True)
    theft_recovery_rate = Column(Float, nullable=True)
    claim_rate_percentage = Column(Float, nullable=True)
    most_common_claim_type = Column(String(50), nullable=True)
    avg_claim_amount = Column(Float, nullable=True)
    total_loss_rate = Column(Float, nullable=True)
    first_mot_pass_rate = Column(Float, nullable=True)
    most_common_mot_failure_reason = Column(String(100), nullable=True)
    avg_mot_failure_cost = Column(Float, nullable=True)
    avg_ownership_duration_months = Column(Float, nullable=True)
    most_common_ownership_change_type = Column(String(50), nullable=True)
    fleet_vehicle_percentage = Column(Float, nullable=True)
    avg_depreciation_rate_per_year = Column(Float, nullable=True)
    finance_percentage = Column(Float, nullable=True)
    avg_finance_term_months = Column(Float, nullable=True)
    recall_rate_percentage = Column(Float, nullable=True)
    most_common_recall_category = Column(String(100), nullable=True)
    avg_annual_mileage = Column(Integer, nullable=True)
    mileage_discrepancy_rate = Column(Float, nullable=True)
    auction_condition_distribution = Column(JSON, nullable=True)
    market_segment = Column(String(50), nullable=True)
    target_demographic = Column(String(100), nullable=True)
    theft_risk_score = Column(Integer, nullable=True)
    reliability_risk_score = Column(Integer, nullable=True)
    financial_risk_score = Column(Integer, nullable=True)
    overall_risk_score = Column(Integer, nullable=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    data_cutoff_date = Column(Date)
    confidence_level = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        Index('ix_cluster_make_model_range', 'make', 'model', 'year_range_start', 'year_range_end', unique=True),
    )

class VehicleClusterInsights(Base):
    __tablename__ = 'vehicle_cluster_insights'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_analytics_id = Column(Integer, ForeignKey('vehicle_cluster_analytics.id'), index=True)
    insight_category = Column(String(50))
    insight_type = Column(String(50))
    severity = Column(String(20))
    insight_title = Column(String(200))
    insight_description = Column(Text)
    supporting_statistic = Column(String(100), nullable=True)
    sample_size = Column(Integer, nullable=True)
    confidence_score = Column(Float, nullable=True)
    show_in_summary = Column(Boolean, default=True)
    priority_order = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index('ix_insights_cluster_category', 'cluster_analytics_id', 'insight_category'),)

class VehicleClusterMembership(Base):
    __tablename__ = 'vehicle_cluster_membership'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), index=True)
    cluster_analytics_id = Column(Integer, ForeignKey('vehicle_cluster_analytics.id'), index=True)
    inclusion_date = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index('ix_unique_membership', 'vehicle_id', 'cluster_analytics_id', unique=True),)


# Constants and Data Lists
NUM_VEHICLES = 100
makes_models = {
    "Ford": ["Focus", "Fiesta", "Kuga", "Puma", "Mustang"], "Volkswagen": ["Golf", "Polo", "Tiguan", "Passat", "ID.3"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "1 Series"], "Mercedes-Benz": ["C-Class", "E-Class", "A-Class", "GLC", "GLE"],
    "Audi": ["A3", "A4", "Q5", "Q3", "A6"], "Toyota": ["Corolla", "Yaris", "RAV4", "C-HR", "Land Cruiser"],
    "Honda": ["Civic", "CR-V", "Jazz", "HR-V"], "Nissan": ["Qashqai", "Juke", "Micra", "X-Trail"],
    "Kia": ["Sportage", "Ceed", "Niro", "Picanto"], "Hyundai": ["Tucson", "i30", "Kona", "Santa Fe"],
    "Land Rover": ["Range Rover Evoque", "Discovery Sport", "Defender", "Range Rover Sport"], "Jaguar": ["XE", "F-Pace", "E-Pace"],
    "Volvo": ["XC40", "XC60", "XC90", "S60"], "Peugeot": ["208", "3008", "2008", "508"], "Renault": ["Clio", "Captur", "Megane"]
}
realistic_variants = [
    "Base", "SE", "SEL", "Titanium", "ST-Line", "Vignale", "RS", "S Line", "Sport", "Black Edition", 
    "Premium", "Luxury", "R-Line", "AMG Line", "M Sport", "xDrive", "quattro", "4MATIC", "HSE", "Dynamic",
    "Inscription", "Polestar", "GT Line", "First Edition", "Limited Edition"
]
fuel_types = ["Petrol", "Diesel", "Hybrid", "Electric"]
transmissions = ["Manual", "Automatic", "CVT"]
body_types = ["Hatchback", "Saloon", "SUV", "Estate", "Coupe", "MPV", "Convertible"]
vehicle_statuses_options = [VehicleStatusType.ACTIVE, VehicleStatusType.SORN, VehicleStatusType.EXPORTED, VehicleStatusType.SCRAPPED]
mot_tax_statuses = ["Valid", "Expired", "Due Soon"] # For display logic, not direct DB field
condition_grades = ["Excellent", "Good", "Fair", "Poor"]
valuation_sources = ["Dealer System", "Online Valuator", "Auction Data", "Insurance Database"]
history_event_types = ["MOT", "Service", "Repair", "Sale", "Import", "V5C Issued", "Tyre Change", "Inspection"]
recall_statuses = ["Outstanding", "Completed", "Not Applicable"]
drive_types = ["FWD", "RWD", "AWD", "4WD"]
uk_cities = [
    "London", "Birmingham", "Manchester", "Leeds", "Liverpool", "Sheffield", "Bristol", "Newcastle", "Nottingham", "Cardiff"
]
mot_advisories = [
    "Nearside front tyre worn close to legal limit", "Offside rear brake disc slightly corroded", "Front windscreen stone chip - attention required",
    "Exhaust system slightly corroded but not affecting emissions", "Oil leak but not excessive", "Rear wiper blade perished"
]
service_descriptions = [
    "Annual service completed - oil and filter changed", "Major service including brake fluid replacement", "Minor service and safety inspection",
    "Oil change and basic health check", "Brake service - pads and discs replaced", "Clutch replacement completed"
]
recall_data_list = [
    {"title": "Engine Management Software Update", "description": "Software update required for engine control unit."},
    {"title": "Airbag Inflator Replacement", "description": "Driver airbag inflator may produce excessive force."},
    {"title": "Brake Servo Inspection", "description": "Brake servo unit may develop internal fault."},
    {"title": "Seat Belt Pre-tensioner Check", "description": "Front seat belt pre-tensioners may not deploy correctly."}
]
make_premium_multiplier = {
    "BMW": 1.4, "Mercedes-Benz": 1.3, "Audi": 1.3, "Jaguar": 1.5, "Land Rover": 1.2, "Volvo": 1.1,
    "Ford": 1.0, "Volkswagen": 1.1, "Toyota": 0.9, "Honda": 0.9, "Nissan": 1.0, "Kia": 0.9,
    "Hyundai": 0.9, "Peugeot": 1.0, "Renault": 1.0
}
owner_types = ["Private", "Trade", "Fleet", "Lease Company", "Rental"]
postcode_prefixes = ["AB1", "B2", "CF3", "DH4", "EH5", "FK6", "G7", "HD8", "IG9", "JE1", "KT2", "L3", "M4", "NE5", "OL6", "PE7", "RG8", "S9", "TF1", "UB2", "WF3", "YO4", "ZE5"]
theft_circumstances_list = ["Stolen from driveway overnight", "Keyless entry theft from street", "Taken during burglary", "Carjacking incident", "Stolen from public car park"]
recovery_conditions = ["Intact, no damage", "Minor body damage", "Wheels missing", "Interior vandalized", "Found burnt out", "Engine damage"]
insurance_companies = ["Aviva", "Direct Line", "Admiral", "AXA", "LV=", "Zurich", "NFU Mutual", "Hastings Direct"]
claim_descriptions = ["Minor rear-end collision, bumper damage", "Windscreen cracked by stone", "Vandalism - keyed along side panel", "Attempted theft, door lock damaged", "Flood damage to interior", "Third party hit parked car"]
mileage_sources = ["MOT Record", "Service Invoice", "Owner Submission", "Insurance Quote", "Valuation System", "Auction Listing"]
finance_types = ["Hire Purchase (HP)", "Personal Contract Purchase (PCP)", "Personal Loan", "Lease Agreement"]
finance_companies = ["Black Horse", "Santander Consumer Finance", "MotoNovo Finance", "Alphera Financial Services", "Close Brothers Motor Finance"]
auction_houses = ["British Car Auctions (BCA)", "Manheim Auctions", "Aston Barclay", "G3 Remarketing", "City Auction Group"]
auction_seller_types = ["Main Dealer PX", "Fleet Disposal", "Finance Repossession", "Private Entry", "Trade Seller"]

# Helper Functions
def random_date_between(start, end):
    if start > end: start = end # Ensure start is not after end
    return start + timedelta(days=random.randint(0, int((end - start).days)))

def generate_vrm():
    if random.random() < 0.8:
        area_codes = ["AB", "BC", "CD", "DE", "EF", "FG", "GH", "HJ", "KL", "MN", "OP", "PQ", "QR", "RS", "ST", "TU", "UV", "VW", "WX", "XY"]
        area = random.choice(area_codes)
        age = f"{random.randint(1, 24):02d}"
        letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        return f"{area}{age}{letters}"
    else:
        letter1 = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        numbers = "".join(random.choices("123456789", k=random.randint(1,3)))
        letters2 = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        return f"{letter1}{numbers}{letters2}"

def generate_vin(prefix="SAMPLEVIN"):
    return prefix + "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=17-len(prefix)))

def get_realistic_annual_mileage():
    return random.choices([3000, 6000, 8000, 10000, 12000, 15000, 18000, 25000], weights=[5, 15, 25, 25, 15, 8, 5, 2])[0]

def get_realistic_location():
    city = random.choice(uk_cities)
    return f"{random.choice(['Main Street Garage', 'City Tyres', 'Quick Fit Auto', 'Approved MOT Centre'])}, {city}"

def generate_postcode():
    return f"{random.choice(postcode_prefixes)}{random.randint(0,9)} {random.randint(1,9)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"


def calculate_insurance_group(make, engine_size, fuel_type, body_type, engine_power_hp):
    base_group = 10
    if engine_size > 3.0: base_group += 15
    elif engine_size > 2.0: base_group += 8
    elif engine_size > 1.6: base_group += 4
    if engine_power_hp > 300: base_group += 20
    elif engine_power_hp > 200: base_group += 10
    elif engine_power_hp > 150: base_group += 5
    multiplier = make_premium_multiplier.get(make, 1.0)
    base_group = int(base_group * multiplier)
    if body_type in ["Coupe", "Convertible"]: base_group += 8
    elif body_type == "SUV": base_group += 3
    if fuel_type == "Electric": base_group = max(1, base_group - 5)
    group_num = max(1, min(50, base_group))
    suffix = random.choices(["E", "D", "A", ""], weights=[70, 15, 10, 5])[0]
    return f"{group_num}{suffix}"

def calculate_realistic_valuation(make, model, year, mileage, condition):
    current_year = date.today().year
    age = max(0, current_year - year)
    base_values = {"BMW": 35000, "Mercedes-Benz": 40000, "Audi": 32000, "Jaguar": 45000, "Land Rover": 50000, "Volvo": 28000, "Ford": 18000, "Volkswagen": 22000, "Toyota": 20000, "Honda": 18000, "Nissan": 16000, "Kia": 15000, "Hyundai": 14000, "Peugeot": 16000, "Renault": 15000}
    base_val = base_values.get(make, 18000)
    if age <= 1: depreciation = 0.15
    elif age <= 3: depreciation = 0.25 + (age - 1) * 0.12
    else: depreciation = 0.49 + (age - 3) * 0.08
    depreciation = min(0.9, depreciation)
    expected_mileage = age * 7500
    mileage_diff = mileage - expected_mileage
    mileage_adjustment = max(-0.3, min(0.1, mileage_diff * -0.00002))
    condition_multipliers = {"Excellent": 1.1, "Good": 1.0, "Fair": 0.85, "Poor": 0.65}
    condition_mult = condition_multipliers.get(condition, 1.0)
    final_value = base_val * (1 - depreciation) * (1 + mileage_adjustment) * condition_mult
    return max(1000, round(final_value / 100) * 100) # Round to nearest 100

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables_if_not_exist():
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created.")

def populate_data():
    db = SessionLocal()
    created_vins = set()
    created_vrms = set()
    all_vehicle_ids = []


    for i in range(NUM_VEHICLES):
        print(f"Generating vehicle {i+1}/{NUM_VEHICLES}...")
        vin = generate_vin()
        while vin in created_vins: vin = generate_vin()
        created_vins.add(vin)
        vrm = generate_vrm()
        while vrm in created_vrms: vrm = generate_vrm()
        created_vrms.add(vrm)

        make = random.choice(list(makes_models.keys()))
        model_name = random.choice(makes_models[make])
        year_val = random.randint(2005, 2023) # Max year 2023 for some history
        registration_date_val = random_date_between(date(year_val, 1, 1), date(min(year_val + 1, 2023), 12, 31))
        
        body = random.choice(body_types)
        doors_val = random.choice([2,3,4,5]) if body not in ["Coupe", "Convertible"] else random.choice([2,3])
        seats_val = random.choice([2,4,5,7]) if body != "Coupe" else random.choice([2,4])
        
        fuel = random.choice(fuel_types)
        engine_s = 0.0 if fuel == "Electric" else round(random.uniform(1.0, 4.0), 1)
        hp_val = random.randint(100, 400) if fuel == "Electric" else random.randint(70, 500)
        kw_val = int(hp_val * 0.7457)
        
        kerb_weight_val = random.randint(900, 2500)
        gross_weight_val = kerb_weight_val + random.randint(300, 800)
        
        days_to_add_mot = random.randint(-90, 365)
        mot_expiry = date.today() + timedelta(days=days_to_add_mot)
        mot_stat = "Valid" if days_to_add_mot > 30 else ("Due Soon" if days_to_add_mot >=0 else "Expired")

        days_to_add_tax = random.randint(-90, 365)
        tax_due = date.today() + timedelta(days=days_to_add_tax)
        tax_stat = "Taxed" if days_to_add_tax >=0 else "Untaxed"

        insurance_group_val = calculate_insurance_group(make, engine_s, fuel, body, hp_val)

        initial_vehicle_status = random.choice(list(VehicleStatusType)) if random.random() < 0.1 else VehicleStatusType.ACTIVE

        vehicle = Vehicle(
            vin=vin, vrm=vrm, make=make, model=model_name, variant=random.choice(realistic_variants), year=year_val,
            registration_date=registration_date_val, engine_size=engine_s, fuel_type=fuel, transmission=random.choice(transmissions),
            body_type=body, doors=doors_val, seats=seats_val, engine_power_hp=hp_val, engine_power_kw=kw_val,
            co2_emissions=round(random.uniform(0, 300),1) if fuel != "Electric" else 0.0,
            fuel_consumption_combined=round(random.uniform(2.8, 12.0),1) if fuel != "Electric" else 0.0,
            vehicle_status=initial_vehicle_status.value, mot_status=mot_stat, mot_expiry_date=mot_expiry,
            tax_status=tax_stat, tax_due_date=tax_due, insurance_group=insurance_group_val,
            euro_status="Euro " + str(random.randint(4, 6)) + random.choice(["", "d", "d-TEMP"]),
            vehicle_class=random.choice(["M1", "N1", "L3e"])
        )
        db.add(vehicle)
        try:
            db.flush()
            all_vehicle_ids.append(vehicle.id)
        except IntegrityError:
            db.rollback()
            print(f"Skipping vehicle {vin}/{vrm} due to integrity error.")
            continue

        spec = VehicleSpecification(
            vehicle_id=vehicle.id, length_mm=random.randint(3500, 5200), width_mm=random.randint(1600, 2100),
            height_mm=random.randint(1300, 1900), wheelbase_mm=random.randint(2300, 3100), kerb_weight_kg=kerb_weight_val,
            gross_weight_kg=gross_weight_val, max_towing_weight_kg=random.randint(0, 3500), fuel_tank_capacity=round(random.uniform(30.0, 90.0),1) if fuel != "Electric" else 0.0,
            boot_capacity_litres=random.randint(150, 700), top_speed_mph=random.randint(80, 180), acceleration_0_60_mph=round(random.uniform(3.0, 18.0),1),
            drive_type=random.choice(drive_types), steering_type=random.choice(["Power", "Electric Power"]), brake_type_front=random.choice(["Discs", "Ventilated Discs"]),
            brake_type_rear=random.choice(["Discs", "Drums"]), airbags="Driver, Passenger" + (", Side" if random.random() > 0.3 else "") + (", Curtain" if random.random() > 0.5 else ""),
            abs=True if year_val > 1998 else random.choice([True, False]), esp=True if year_val > 2008 else random.choice([True, False])
        )
        db.add(spec)

        current_mileage = random.randint(100, 2000) # Initial mileage
        last_date_with_mileage = registration_date_val
        annual_mileage = get_realistic_annual_mileage()

        # Valuations
        for _ in range(random.randint(0, 3)):
            val_date = random_date_between(last_date_with_mileage + timedelta(days=180), date.today() - timedelta(days=30))
            if val_date < registration_date_val: continue
            
            time_since_last = (val_date - last_date_with_mileage).days / 365.25
            current_mileage += int(annual_mileage * time_since_last * random.uniform(0.7, 1.3))
            current_mileage = max(100, current_mileage)
            last_date_with_mileage = val_date
            
            condition = random.choice(condition_grades)
            base_val = calculate_realistic_valuation(make, model_name, year_val, current_mileage, condition)
            db.add(VehicleValuation(
                vehicle_id=vehicle.id, valuation_date=val_date, retail_value=round(base_val * 1.1,0), trade_value=round(base_val * 0.8,0),
                private_value=round(base_val * 0.95,0), auction_value=round(base_val * 0.75,0), mileage_at_valuation=current_mileage,
                condition_grade=condition, regional_adjustment=round(random.uniform(0.95, 1.05), 2), valuation_source=random.choice(valuation_sources),
                confidence_score=round(random.uniform(0.6, 0.95), 2)
            ))

        # History (MOTs, Services)
        # Ensure MOT history has plausible mileage progression
        mot_mileage = random.randint(100,1000) if (date.today() - registration_date_val).days / 365.25 < 1 else current_mileage
        
        num_history_events = random.randint(1, max(1, int((date.today() - registration_date_val).days / 365.25) + 1)) # up to 1 per year + 1
        last_history_event_date = registration_date_val
        
        for _ in range(num_history_events):
            days_to_add = random.randint(180, 500) # Event every 6-18 months
            event_date_val = last_history_event_date + timedelta(days=days_to_add)
            if event_date_val > date.today(): break # Don't go past today

            time_since_last_hist = (event_date_val - last_history_event_date).days / 365.25
            mot_mileage += int(annual_mileage * time_since_last_hist * random.uniform(0.7, 1.3))
            mot_mileage = max(10, mot_mileage)

            event_type_val = random.choice(history_event_types)
            desc = f"{event_type_val} performed."
            pf = None
            advisory = None
            cost_hist = None

            if event_type_val == "MOT":
                pf = "PASS" if random.random() > 0.2 else "FAIL"
                if random.random() > 0.4: advisory = random.choice(mot_advisories)
                desc = "MOT Test"
            elif event_type_val in ["Service", "Repair"]:
                cost_hist = round(random.uniform(50, 800), 2)
                desc = random.choice(service_descriptions)
            
            db.add(VehicleHistory(
                vehicle_id=vehicle.id, event_date=event_date_val, event_type=event_type_val, event_description=desc,
                mileage=mot_mileage, location=get_realistic_location(), source=random.choice(["DVSA", "Garage", "Main Dealer"]),
                pass_fail=pf, advisory_notes=advisory, cost=cost_hist
            ))
            last_history_event_date = event_date_val
            current_mileage = max(current_mileage, mot_mileage) # Update overall current_mileage
            last_date_with_mileage = max(last_date_with_mileage, event_date_val)


        # Recalls
        if random.random() < 0.4:
            for _ in range(random.randint(1, 2)):
                recall_item = random.choice(recall_data_list)
                db.add(VehicleRecall(
                    vehicle_id=vehicle.id, recall_number=f"R/{year_val}/{random.randint(100,999)}",
                    recall_date=random_date_between(registration_date_val, date.today() - timedelta(days=30)),
                    recall_title=recall_item["title"], recall_description=recall_item["description"],
                    safety_issue=random.choice([True, False]), recall_status=random.choice(recall_statuses),
                    completion_date=random_date_between(registration_date_val + timedelta(days=30), date.today()) if random.random() > 0.3 else None,
                    issuing_authority=random.choice(["DVSA", make]), manufacturer_campaign=f"CAMP-{random.randint(1000,9999)}"
                ))
        
        # Ownership History
        num_owners = random.choices([1,2,3,4,5],[60,20,10,5,5])[0]
        last_owner_change_date = registration_date_val
        prev_owner_type = "Manufacturer/Dealer" # First owner often dealer
        for own_idx in range(num_owners):
            if own_idx == 0 and num_owners == 1: # Single owner car
                change_type_val = OwnershipChangeType.TRADE_TO_PRIVATE
                new_owner_type_val = "Private"
            else:
                change_type_val = random.choice(list(OwnershipChangeType))
                new_owner_type_val = random.choice(owner_types)
                while new_owner_type_val == prev_owner_type and change_type_val not in [OwnershipChangeType.TRADE_TO_TRADE, OwnershipChangeType.PRIVATE_TO_PRIVATE]: # Avoid same type unless specific
                    new_owner_type_val = random.choice(owner_types)


            change_d = random_date_between(last_owner_change_date + timedelta(days=(7 if own_idx == 0 else 365)), date.today() - timedelta(days=30))
            if change_d < last_owner_change_date : continue

            time_since_last_own = (change_d - last_date_with_mileage).days / 365.25
            current_mileage += int(annual_mileage * time_since_last_own * random.uniform(0.7, 1.3))
            current_mileage = max(100, current_mileage)
            last_date_with_mileage = change_d
            
            db.add(VehicleOwnershipHistory(
                vehicle_id=vehicle.id, change_date=change_d, change_type=change_type_val,
                previous_owner_type=prev_owner_type, new_owner_type=new_owner_type_val,
                previous_owner_postcode=generate_postcode(), new_owner_postcode=generate_postcode(),
                mileage_at_change=current_mileage, sale_price=round(calculate_realistic_valuation(make,model_name,year_val,current_mileage,random.choice(condition_grades)) * random.uniform(0.8,1.2),0) if random.random() > 0.3 else None,
                source=random.choice(["DVLA", "Dealer Sale", "Private Sale", "Auction"])
            ))
            last_owner_change_date = change_d
            prev_owner_type = new_owner_type_val

        # Theft Record (10% chance)
        if random.random() < 0.1 and vehicle.vehicle_status == VehicleStatusType.ACTIVE.value : # Only if currently active
            theft_d = random_date_between(registration_date_val + timedelta(days=90), date.today() - timedelta(days=60))
            is_recovered = random.random() > 0.4
            recovery_d = None
            theft_status = VehicleStatusType.STOLEN
            if is_recovered:
                recovery_d = random_date_between(theft_d + timedelta(days=1), date.today() - timedelta(days=1))
                theft_status = VehicleStatusType.RECOVERED
            
            db.add(VehicleTheftRecord(
                vehicle_id=vehicle.id, theft_date=theft_d, recovery_date=recovery_d,
                theft_location_postcode=generate_postcode(), recovery_location_postcode=generate_postcode() if is_recovered else None,
                theft_circumstances=random.choice(theft_circumstances_list),
                recovery_condition=random.choice(recovery_conditions) if is_recovered else None,
                police_reference=f"POL-{random.randint(10000,99999)}", insurance_claim_reference=f"INS-{random.randint(10000,99999)}" if random.random() > 0.5 else None,
                current_status=theft_status
            ))
            if not is_recovered:
                vehicle.vehicle_status = VehicleStatusType.STOLEN.value
            elif theft_status == VehicleStatusType.RECOVERED : # if recovered, set vehicle status back to active for further events
                 vehicle.vehicle_status = VehicleStatusType.ACTIVE.value


        # Insurance Claims (20% chance of 1-2 claims)
        if random.random() < 0.2:
            for _ in range(random.randint(1,2)):
                claim_d = random_date_between(registration_date_val + timedelta(days=30), date.today() - timedelta(days=15))
                claim_type_val = random.choice(list(InsuranceClaimType))
                
                time_since_last_claim = (claim_d - last_date_with_mileage).days / 365.25
                current_mileage += int(annual_mileage * time_since_last_claim * random.uniform(0.7, 1.3))
                current_mileage = max(100, current_mileage)
                last_date_with_mileage = claim_d

                total_loss_val = False
                if claim_type_val not in [InsuranceClaimType.WINDSCREEN, InsuranceClaimType.VANDALISM] and random.random() < 0.1: # 10% chance of total loss for major claims
                    total_loss_val = True
                
                claim_amt = round(random.uniform(100, 15000),2)
                settle_amt = round(claim_amt * random.uniform(0.7, 1.0),2) if not total_loss_val else round(calculate_realistic_valuation(make, model_name, year_val, current_mileage, "Poor") * 0.9, 0)


                db.add(VehicleInsuranceClaim(
                    vehicle_id=vehicle.id, claim_date=claim_d, claim_type=claim_type_val,
                    claim_amount=claim_amt, settlement_amount=settle_amt,
                    incident_location_postcode=generate_postcode(), fault_claim=random.choice([True,False]),
                    total_loss=total_loss_val, mileage_at_incident=current_mileage,
                    description=random.choice(claim_descriptions), insurer=random.choice(insurance_companies),
                    claim_reference=f"CLM-{random.randint(100000,999999)}"
                ))
                if total_loss_val:
                    vehicle.vehicle_status = VehicleStatusType.WRITTEN_OFF.value # Update vehicle status

        # Mileage Records (independent log, can overlap with MOT/Service)
        last_mileage_rec_date = registration_date_val
        prev_mileage_val = 0
        for _ in range(random.randint(2,5)): # 2-5 distinct mileage readings
            reading_d = random_date_between(last_mileage_rec_date + timedelta(days=random.randint(90,730)), date.today() - timedelta(days=10))
            if reading_d < registration_date_val: continue

            time_since_last_read = (reading_d - last_date_with_mileage).days / 365.25
            current_mileage += int(annual_mileage * time_since_last_read * random.uniform(0.7, 1.3))
            current_mileage = max(10, current_mileage)

            discrepancy = False
            if prev_mileage_val > 0 and current_mileage < prev_mileage_val * 0.95 : # If new mileage is less than 95% of previous
                discrepancy = True

            db.add(VehicleMileageRecord(
                vehicle_id=vehicle.id, reading_date=reading_d, mileage=current_mileage,
                source=random.choice(mileage_sources), verified=random.choice([True,False]),
                discrepancy_flag=discrepancy, previous_mileage=prev_mileage_val if prev_mileage_val > 0 else None
            ))
            prev_mileage_val = current_mileage
            last_mileage_rec_date = reading_d
            last_date_with_mileage = max(last_date_with_mileage, reading_d)


        # Finance Record (30% chance)
        if random.random() < 0.3:
            finance_start_d = random_date_between(registration_date_val, date.today() - timedelta(days=365 * 2)) # Min 2 years ago if active
            term_years = random.choice([2,3,4,5])
            finance_end_d = finance_start_d + timedelta(days=term_years * 365)
            outstanding = date.today() < finance_end_d
            settle_d = None
            if not outstanding and random.random() < 0.7: # if ended, 70% chance it ended on time
                settle_d = finance_end_d
            elif outstanding and random.random() < 0.1: # if outstanding, 10% chance it was settled early
                settle_d = random_date_between(finance_start_d + timedelta(days=365), date.today()-timedelta(days=30))
                outstanding = False # No longer outstanding if settled early
            
            db.add(VehicleFinanceRecord(
                vehicle_id=vehicle.id, finance_start_date=finance_start_d, finance_end_date=finance_end_d,
                finance_type=random.choice(finance_types), finance_company=random.choice(finance_companies),
                settlement_figure=round(random.uniform(1000,20000),2) if outstanding else 0.0,
                monthly_payment=round(random.uniform(150,800),2), outstanding_finance=outstanding,
                settlement_date=settle_d
            ))

        # Auction Record (15% chance)
        if random.random() < 0.15:
            auction_d = random_date_between(registration_date_val + timedelta(days=180), date.today() - timedelta(days=30))
            
            time_since_last_auc = (auction_d - last_date_with_mileage).days / 365.25
            current_mileage += int(annual_mileage * time_since_last_auc * random.uniform(0.7, 1.3))
            current_mileage = max(100, current_mileage)
            last_date_with_mileage = auction_d
            
            auc_condition = random.choice(condition_grades)
            guide_low = calculate_realistic_valuation(make,model_name,year_val,current_mileage,auc_condition) * 0.7
            guide_high = guide_low * 1.3
            is_sold = random.random() > 0.2 # 80% sold
            hammer = None
            if is_sold:
                hammer = round(random.uniform(guide_low * 0.9, guide_high * 1.1),0)

            db.add(VehicleAuctionRecord(
                vehicle_id=vehicle.id, auction_date=auction_d, auction_house=random.choice(auction_houses),
                lot_number=f"LOT{random.randint(100,9999)}", guide_price_low=round(guide_low,0), guide_price_high=round(guide_high,0),
                hammer_price=hammer, sold=is_sold, seller_type=random.choice(auction_seller_types),
                condition_grade=auc_condition, mileage_at_auction=current_mileage
            ))
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error committing vehicle {vin} and its related records: {e}")

    # Populate Simplified Cluster Analytics and Insights
    print("Populating simplified cluster analytics...")
    sample_clusters = [
        {"make": "Ford", "model": "Focus", "year_start": 2018, "year_end": 2020, "body_type": "Hatchback"},
        {"make": "BMW", "model": "3 Series", "year_start": 2019, "year_end": 2021, "body_type": "Saloon"},
        {"make": "Volkswagen", "model": "Golf", "year_start": 2017, "year_end": 2019, "body_type": "Hatchback"},
        {"make": "Nissan", "model": "Qashqai", "year_start": 2020, "year_end": 2022, "body_type": "SUV"}
    ]
    
    cluster_analytics_ids = []
    for sc in sample_clusters:
        try:
            analytics = VehicleClusterAnalytics(
                make=sc["make"], model=sc["model"], year_range_start=sc["year_start"], year_range_end=sc["year_end"], body_type=sc["body_type"],
                total_vehicles_analyzed=random.randint(50, 500),
                theft_rate_percentage=round(random.uniform(0.5, 5.0), 2),
                most_common_theft_location=random.choice(["Street", "Driveway", "Car Park"]),
                avg_days_to_recovery=round(random.uniform(5, 30),1),
                theft_recovery_rate=round(random.uniform(40,80),1),
                claim_rate_percentage=round(random.uniform(10, 30), 2),
                most_common_claim_type=random.choice(list(InsuranceClaimType)).value,
                avg_claim_amount=round(random.uniform(500, 3000), 2),
                total_loss_rate=round(random.uniform(1,10),1),
                first_mot_pass_rate=round(random.uniform(70, 95), 1),
                most_common_mot_failure_reason=random.choice(["Brakes", "Tyres", "Suspension", "Lights"]),
                avg_ownership_duration_months=round(random.uniform(24, 60),1),
                avg_annual_mileage=random.choice([8000,10000,12000]),
                auction_condition_distribution={"Excellent":random.randint(5,15),"Good":random.randint(30,50),"Fair":random.randint(20,40),"Poor":random.randint(5,15)}, # %
                theft_risk_score=random.randint(1,10), reliability_risk_score=random.randint(1,10), financial_risk_score=random.randint(1,10),
                overall_risk_score=random.randint(1,10),
                data_cutoff_date=date.today() - timedelta(days=random.randint(30,90)),
                confidence_level = round(random.uniform(0.7, 0.95),2)
            )
            db.add(analytics)
            db.flush() # Get ID for insights
            cluster_analytics_ids.append(analytics.id)

            # Add some dummy insights for this cluster
            db.add(VehicleClusterInsights(cluster_analytics_id=analytics.id, insight_category="reliability", insight_type="positive", severity="medium", insight_title=f"Good MOT Pass Rate for {sc['make']} {sc['model']}", insight_description=f"Models from {sc['year_start']}-{sc['year_end']} generally show a strong first-time MOT pass rate, indicating good build quality.", supporting_statistic=f"{analytics.first_mot_pass_rate}% pass rate"))
            db.add(VehicleClusterInsights(cluster_analytics_id=analytics.id, insight_category="theft", insight_type="warning", severity="high", insight_title=f"Moderate Theft Risk for {sc['make']} {sc['model']}", insight_description=f"These models have a theft rate of {analytics.theft_rate_percentage}%. Consider extra security.", supporting_statistic=f"{analytics.theft_rate_percentage}% theft rate"))
            db.commit()
        except IntegrityError:
            db.rollback()
            print(f"Cluster analytics for {sc['make']} {sc['model']} {sc['year_start']}-{sc['year_end']} likely already exists. Skipping.")
        except Exception as e:
            db.rollback()
            print(f"Error creating cluster analytics/insights: {e}")


    # Populate VehicleClusterMembership
    if all_vehicle_ids and cluster_analytics_ids:
        print("Populating vehicle cluster memberships...")
        for veh_id in random.sample(all_vehicle_ids, min(len(all_vehicle_ids), NUM_VEHICLES // 2)): # Half the vehicles get assigned
            chosen_cluster_id = random.choice(cluster_analytics_ids)
            try:
                membership = VehicleClusterMembership(vehicle_id=veh_id, cluster_analytics_id=chosen_cluster_id)
                db.add(membership)
                db.commit()
            except IntegrityError: # Already a member of this cluster
                db.rollback()
            except Exception as e:
                db.rollback()
                print(f"Error creating cluster membership for vehicle {veh_id} and cluster {chosen_cluster_id}: {e}")


    db.close()
    print(f"Successfully populated database with vehicle records and related data.")

if __name__ == "__main__":
    print(f"Connecting to database: {DATABASE_URL}")
    create_tables_if_not_exist()
    print("Starting data population...")
    populate_data()
    print("Data population finished.")