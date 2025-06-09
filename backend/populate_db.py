import os
import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, Date, Index
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.exc import IntegrityError

DATABASE_URL = "mysql+pymysql://root:system@localhost/vehicleinsights"

Base = declarative_base()

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
    valuations = relationship("VehicleValuation", back_populates="vehicle", cascade="all, delete-orphan")
    history_records = relationship("VehicleHistory", back_populates="vehicle", cascade="all, delete-orphan")
    recalls = relationship("VehicleRecall", back_populates="vehicle", cascade="all, delete-orphan")
    specifications = relationship("VehicleSpecification", back_populates="vehicle", cascade="all, delete-orphan") 
    ai_summary = relationship("VehicleAISummary", back_populates="vehicle", uselist=False, cascade="all, delete-orphan")
    __table_args__ = (Index('ix_vehicle_make_model', 'make', 'model'),)

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
    pass_fail = Column(String(10))
    advisory_notes = Column(Text)
    cost = Column(Float)
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

NUM_VEHICLES = 100

makes_models = {
    "Ford": ["Focus", "Fiesta", "Kuga", "Puma", "Mustang"],
    "Volkswagen": ["Golf", "Polo", "Tiguan", "Passat", "ID.3"],
    "BMW": ["3 Series", "5 Series", "X3", "X5", "1 Series"],
    "Mercedes-Benz": ["C-Class", "E-Class", "A-Class", "GLC", "GLE"],
    "Audi": ["A3", "A4", "Q5", "Q3", "A6"],
    "Toyota": ["Corolla", "Yaris", "RAV4", "C-HR", "Land Cruiser"],
    "Honda": ["Civic", "CR-V", "Jazz", "HR-V"],
    "Nissan": ["Qashqai", "Juke", "Micra", "X-Trail"],
    "Kia": ["Sportage", "Ceed", "Niro", "Picanto"],
    "Hyundai": ["Tucson", "i30", "Kona", "Santa Fe"],
    "Land Rover": ["Range Rover Evoque", "Discovery Sport", "Defender", "Range Rover Sport"],
    "Jaguar": ["XE", "F-Pace", "E-Pace"],
    "Volvo": ["XC40", "XC60", "XC90", "S60"],
    "Peugeot": ["208", "3008", "2008", "508"],
    "Renault": ["Clio", "Captur", "Megane"]
}

# Realistic vehicle trim levels and variants
realistic_variants = [
    "Base", "SE", "SEL", "Titanium", "ST-Line", "Vignale", "RS",
    "S Line", "Sport", "Black Edition", "Premium", "Luxury", "R-Line",
    "AMG Line", "M Sport", "xDrive", "quattro", "4MATIC", "HSE", "Dynamic",
    "Inscription", "Polestar", "GT Line", "First Edition", "Limited Edition"
]

# UK fuel terminology - keeping "Petrol" not "Gasoline"
fuel_types = ["Petrol", "Diesel", "Hybrid", "Electric"]
transmissions = ["Manual", "Automatic", "CVT"]
body_types = ["Hatchback", "Saloon", "SUV", "Estate", "Coupe", "MPV", "Convertible"]
vehicle_statuses = ["Active", "Scrapped", "Exported", "Laid up (SORN)"] 
mot_tax_statuses = ["Valid", "Expired", "Due Soon"]
condition_grades = ["Excellent", "Good", "Fair", "Poor"]
valuation_sources = ["Dealer System", "Online Valuator", "Auction Data", "Insurance Database"]
history_event_types = ["MOT", "Service", "Repair", "Sale", "Import", "V5C Issued"]
recall_statuses = ["Outstanding", "Completed", "Not Applicable"]
drive_types = ["FWD", "RWD", "AWD", "4WD"]

# Realistic UK cities and service locations
uk_cities = [
    "London", "Birmingham", "Manchester", "Leeds", "Liverpool", "Sheffield", 
    "Bristol", "Newcastle", "Nottingham", "Cardiff", "Leicester", "Coventry",
    "Bradford", "Edinburgh", "Belfast", "Brighton", "Hull", "Plymouth",
    "Stoke-on-Trent", "Wolverhampton", "Derby", "Southampton", "Portsmouth",
    "Aberdeen", "Swansea", "Dundee", "York", "Peterborough", "Oldham"
]

# Realistic MOT advisory notes
mot_advisories = [
    "Nearside front tyre worn close to legal limit",
    "Offside rear brake disc slightly corroded",
    "Front windscreen stone chip - attention required",
    "Exhaust system slightly corroded but not affecting emissions",
    "Oil leak but not excessive",
    "Rear wiper blade perished",
    "Nearside headlamp alignment slightly off",
    "Brake fluid level low - topped up during test",
    "Battery terminals corroded",
    "Minor oil leak from engine - monitor closely",
    "Handbrake travel excessive but within limits",
    "Suspension arm bush worn but not affecting safety",
    "Door mirror glass cracked",
    "Number plate lamp not working - bulb replaced",
    "Tyre pressure monitoring system warning light on"
]

# Realistic service descriptions
service_descriptions = [
    "Annual service completed - oil and filter changed",
    "Major service including brake fluid replacement",
    "Minor service and safety inspection",
    "Oil change and basic health check",
    "Brake service - pads and discs replaced",
    "Clutch replacement completed",
    "Timing belt replacement due to age",
    "Battery replacement - old battery failed",
    "Tyre replacement - worn beyond legal limit",
    "Air conditioning service and re-gas",
    "Exhaust system repair completed",
    "Suspension component replacement",
    "Wheel alignment adjustment",
    "Windscreen replacement due to damage",
    "Electrical fault diagnosis and repair"
]

# Realistic recall titles and descriptions
recall_data = [
    {
        "title": "Engine Management Software Update",
        "description": "Software update required for engine control unit to prevent potential stalling in certain driving conditions. No safety risk identified but may affect vehicle performance."
    },
    {
        "title": "Airbag Inflator Replacement",
        "description": "Driver airbag inflator may produce excessive force during deployment. Replacement of airbag unit required as precautionary measure to ensure occupant safety."
    },
    {
        "title": "Brake Servo Inspection",
        "description": "Brake servo unit may develop internal fault leading to reduced braking assistance. Inspection and potential replacement required to maintain safe braking performance."
    },
    {
        "title": "Seat Belt Pre-tensioner Check",
        "description": "Front seat belt pre-tensioners may not deploy correctly in collision. Inspection of mechanism required with replacement if necessary to ensure occupant protection."
    },
    {
        "title": "Fuel System Component Replacement",
        "description": "Fuel pump component may fail prematurely causing engine to stall. Replacement of affected component required to prevent potential breakdown."
    },
    {
        "title": "Electronic Stability Control Update",
        "description": "ESC system software requires update to improve vehicle stability in adverse conditions. Software update available at authorized dealers."
    },
    {
        "title": "Door Lock Actuator Inspection",
        "description": "Central locking actuator may fail causing doors not to lock properly. Inspection and replacement of faulty actuators required for security."
    },
    {
        "title": "Headlamp Adjustment Check",
        "description": "Headlamp beam pattern may be incorrect due to manufacturing variance. Adjustment required to ensure proper road illumination and prevent dazzling oncoming traffic."
    }
]

# Insurance group premiums by make (for more realistic data)
make_premium_multiplier = {
    "BMW": 1.4, "Mercedes-Benz": 1.3, "Audi": 1.3, "Jaguar": 1.5, "Land Rover": 1.2,
    "Volvo": 1.1, "Ford": 1.0, "Volkswagen": 1.1, "Toyota": 0.9, "Honda": 0.9,
    "Nissan": 1.0, "Kia": 0.9, "Hyundai": 0.9, "Peugeot": 1.0, "Renault": 1.0
}

def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

def generate_vrm():
    """Generates a realistic UK VRM."""
    if random.random() < 0.8:  
        # New format: AB12 CDE
        area_codes = ["AB", "BC", "CD", "DE", "EF", "FG", "GH", "HJ", "KL", "MN", 
                     "OP", "PQ", "QR", "RS", "ST", "TU", "UV", "VW", "WX", "XY"]
        area = random.choice(area_codes)
        # Age identifier: 01-24 for years 2001-2024
        age = f"{random.randint(1, 24):02d}"
        letters = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        return f"{area}{age}{letters}"
    else:  # Old format: A123 BCD
        letter1 = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        numbers = "".join(random.choices("123456789", k=random.randint(1,3)))
        letters2 = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=3))
        return f"{letter1}{numbers}{letters2}"

def generate_vin(prefix="SAMPLETESTVIN"):
    return prefix + "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=17-len(prefix)))

def get_realistic_annual_mileage():
    """Generate realistic annual mileage based on UK driving patterns."""
    return random.choices(
        [3000, 6000, 8000, 12000, 18000, 25000],  
        weights=[10, 20, 35, 25, 8, 2]  
    )[0]

def get_realistic_location():
    """Generate realistic UK service location."""
    city = random.choice(uk_cities)
    street_types = ["Road", "Street", "Avenue", "Lane", "Close", "Drive", "Way", "Gardens"]
    street_names = ["High", "Church", "Mill", "School", "Park", "Victoria", "Queen", "King", 
                   "Station", "Manor", "Oak", "Elm", "Rose", "Hill", "New", "Old"]
    
    street = f"{random.choice(street_names)} {random.choice(street_types)}"
    return f"{city}, {street}"

def calculate_insurance_group(make, engine_size, fuel_type, body_type, engine_power_hp):
    """Calculate more realistic insurance groups."""
    base_group = 10
    
    # Engine size factor
    if engine_size > 3.0:
        base_group += 15
    elif engine_size > 2.0:
        base_group += 8
    elif engine_size > 1.6:
        base_group += 4
    
    # Power factor
    if engine_power_hp > 300:
        base_group += 20
    elif engine_power_hp > 200:
        base_group += 10
    elif engine_power_hp > 150:
        base_group += 5
    
    # Make premium
    multiplier = make_premium_multiplier.get(make, 1.0)
    base_group = int(base_group * multiplier)
    
    # Body type adjustment
    if body_type in ["Coupe", "Convertible"]:
        base_group += 8
    elif body_type == "SUV":
        base_group += 3
    
    # Electric vehicles often get lower groups due to safety
    if fuel_type == "Electric":
        base_group = max(1, base_group - 5)
    
    # Clamp to valid range
    group_num = max(1, min(50, base_group))
    
    # Add realistic suffix
    suffix = random.choices(["E", "D", "A", ""], weights=[70, 15, 10, 5])[0]
    
    return f"{group_num}{suffix}"

def calculate_realistic_valuation(make, model, year, mileage, condition):
    """More realistic valuation calculation."""
    current_year = date.today().year
    age = current_year - year
    
    # Base values by make (rough UK market values)
    base_values = {
        "BMW": 35000, "Mercedes-Benz": 40000, "Audi": 32000, "Jaguar": 45000,
        "Land Rover": 50000, "Volvo": 28000, "Ford": 18000, "Volkswagen": 22000,
        "Toyota": 20000, "Honda": 18000, "Nissan": 16000, "Kia": 15000,
        "Hyundai": 14000, "Peugeot": 16000, "Renault": 15000
    }
    
    base_val = base_values.get(make, 18000)
    
    # Age depreciation (steeper in first few years)
    if age <= 1:
        depreciation = 0.15
    elif age <= 3:
        depreciation = 0.25 + (age - 1) * 0.12
    else:
        depreciation = 0.49 + (age - 3) * 0.08
    
    depreciation = min(0.9, depreciation)  
    
    # Mileage depreciation
    expected_mileage = age * 7500  
    mileage_diff = mileage - expected_mileage
    mileage_adjustment = max(-0.3, min(0.1, mileage_diff * -0.00002))  
    
    # Condition adjustment
    condition_multipliers = {"Excellent": 1.1, "Good": 1.0, "Fair": 0.85, "Poor": 0.65}
    condition_mult = condition_multipliers.get(condition, 1.0)
    
    final_value = base_val * (1 - depreciation) * (1 + mileage_adjustment) * condition_mult
    return max(1000, final_value)  

engine = create_engine(DATABASE_URL, echo=False) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables_if_not_exist():
    Base.metadata.create_all(bind=engine)
    print("Tables checked/created.")

def populate_data():
    db = SessionLocal()
    created_vins = set()
    created_vrms = set()

    for i in range(NUM_VEHICLES):
        print(f"Generating vehicle {i+1}/{NUM_VEHICLES}...")

        # Generate unique identifiers
        vin = generate_vin()
        while vin in created_vins: 
            vin = generate_vin()
        created_vins.add(vin)

        vrm = generate_vrm()
        while vrm in created_vrms: 
            vrm = generate_vrm()
        created_vrms.add(vrm)

        # Basic vehicle info
        make = random.choice(list(makes_models.keys()))
        model_name = random.choice(makes_models[make])
        year = random.randint(2005, 2024)
        registration_date_val = random_date(date(year, 1, 1), date(min(year + 1, 2024), 12, 31))
        
        # Physical characteristics
        body = random.choice(body_types)
        doors_val = random.choice([2,3,4,5]) if body not in ["Coupe", "Convertible"] else random.choice([2,3])
        seats_val = random.choice([2,4,5,7]) if body != "Coupe" else random.choice([2,4])
        
        # Engine specifications
        fuel = random.choice(fuel_types)
        if fuel == "Electric":
            engine_s = 0.0
            hp_val = random.randint(100, 400)
        else:
            engine_s = round(random.uniform(1.0, 4.0), 1)
            hp_val = random.randint(70, 500)
        
        kw_val = int(hp_val * 0.7457)  # Convert HP to KW properly
        
        # Physical dimensions
        kerb_weight_val = random.randint(900, 2500)
        gross_weight_val = kerb_weight_val + random.randint(300, 800)
        
        # MOT/Tax status
        days_to_add_mot = random.randint(-90, 365) 
        mot_expiry = date.today() + timedelta(days=days_to_add_mot)
        mot_stat = "Valid"
        if days_to_add_mot < 0: 
            mot_stat = "Expired"
        elif days_to_add_mot <= 30: 
            mot_stat = "Due Soon"

        days_to_add_tax = random.randint(-90, 365)
        tax_due = date.today() + timedelta(days=days_to_add_tax)
        tax_stat = "Taxed" 
        if days_to_add_tax < 0: 
            tax_stat = "Untaxed"

        # Calculate realistic insurance group
        insurance_group_val = calculate_insurance_group(make, engine_s, fuel, body, hp_val)

        vehicle = Vehicle(
            vin=vin,
            vrm=vrm,
            make=make,
            model=model_name,
            variant=random.choice(realistic_variants),
            year=year,
            registration_date=registration_date_val,
            engine_size=engine_s,
            fuel_type=fuel,
            transmission=random.choice(transmissions),
            body_type=body,
            doors=doors_val,
            seats=seats_val,
            engine_power_hp=hp_val,
            engine_power_kw=kw_val,
            co2_emissions=round(random.uniform(0, 300),1) if fuel != "Electric" else 0.0,
            fuel_consumption_urban=round(random.uniform(3.0, 15.0),1) if fuel != "Electric" else 0.0,
            fuel_consumption_extra_urban=round(random.uniform(2.5, 10.0),1) if fuel != "Electric" else 0.0,
            fuel_consumption_combined=round(random.uniform(2.8, 12.0),1) if fuel != "Electric" else 0.0,
            vehicle_status=random.choice(vehicle_statuses) if random.random() > 0.1 else "Active",
            mot_status=mot_stat,
            mot_expiry_date=mot_expiry,
            tax_status=tax_stat,
            tax_due_date=tax_due,
            insurance_group=insurance_group_val,
            euro_status="Euro " + str(random.randint(4, 6)) + random.choice(["", "d", "d-TEMP"]),
            vehicle_class=random.choice(["M1", "N1", "L3e"])
        )
        db.add(vehicle)
        
        try:
            db.flush() 
        except IntegrityError:
            db.rollback()
            print(f"Skipping vehicle due to integrity error (likely duplicate VIN/VRM): {vin}/{vrm}")
            continue

        # Vehicle specifications
        spec = VehicleSpecification(
            vehicle_id=vehicle.id,
            length_mm=random.randint(3500, 5200),
            width_mm=random.randint(1600, 2100),
            height_mm=random.randint(1300, 1900),
            wheelbase_mm=random.randint(2300, 3100),
            kerb_weight_kg=kerb_weight_val,
            gross_weight_kg=gross_weight_val,
            max_towing_weight_kg=random.randint(500, 3500) if body == "SUV" or engine_s > 2.0 else random.randint(0, 1500),
            fuel_tank_capacity=round(random.uniform(30.0, 90.0),1) if fuel != "Electric" else 0.0,
            boot_capacity_litres=random.randint(150, 700),
            top_speed_mph=random.randint(90, 180) if fuel != "Electric" else random.randint(80,140),
            acceleration_0_60_mph=round(random.uniform(3.0, 18.0),1),
            drive_type=random.choice(drive_types),
            steering_type=random.choice(["Power", "Electric Power"]),
            brake_type_front=random.choice(["Discs", "Ventilated Discs"]),
            brake_type_rear=random.choice(["Discs", "Drums"]),
            airbags="Driver, Passenger" + (", Side" if random.random() > 0.3 else "") + (", Curtain" if random.random() > 0.5 else ""),
            abs=True if year > 1998 else random.choice([True, False]),
            esp=True if year > 2008 else random.choice([True, False])
        )
        db.add(spec)

        # Vehicle valuations with realistic pricing
        annual_mileage = get_realistic_annual_mileage()
        current_mileage = 500
        
        for _ in range(random.randint(0, 3)):
            val_date = random_date(registration_date_val + timedelta(days=180), date.today() - timedelta(days=30))
            years_since_reg = (val_date - registration_date_val).days / 365.0
            current_mileage += int(annual_mileage * years_since_reg * random.uniform(0.8, 1.2))
            current_mileage = max(500, current_mileage)
            
            condition = random.choice(condition_grades)
            base_val = calculate_realistic_valuation(make, model_name, year, current_mileage, condition)
            
            valuation = VehicleValuation(
                vehicle_id=vehicle.id,
                valuation_date=val_date,
                retail_value=round(base_val * random.uniform(1.05, 1.15), 2),
                trade_value=round(base_val * random.uniform(0.75, 0.85), 2),
                private_value=round(base_val * random.uniform(0.90, 1.05), 2),
                auction_value=round(base_val * random.uniform(0.70, 0.80), 2),
                mileage_at_valuation=current_mileage,
                condition_grade=condition,
                regional_adjustment=round(random.uniform(0.95, 1.05), 2),
                valuation_source=random.choice(valuation_sources),
                confidence_score=round(random.uniform(0.6, 0.95), 2)
            )
            db.add(valuation)

        # Vehicle history with more realistic MOT patterns
        vehicle_age = (date.today() - registration_date_val).days / 365.0
        last_event_date = registration_date_val
        current_mileage_hist = random.randint(10, 500)

        # Add first MOT at 3 years (if vehicle is old enough)
        if vehicle_age >= 3:
            first_mot_date = registration_date_val.replace(year=registration_date_val.year + 3)
            if first_mot_date <= date.today():
                current_mileage_hist += int(annual_mileage * 3 * random.uniform(0.8, 1.2))
                
                history_record = VehicleHistory(
                    vehicle_id=vehicle.id,
                    event_date=first_mot_date,
                    event_type="MOT",
                    event_description="First MOT Test",
                    mileage=current_mileage_hist,
                    location=get_realistic_location(),
                    source="DVSA Record",
                    pass_fail="PASS" if random.random() > 0.1 else "FAIL",
                    advisory_notes=random.choice(mot_advisories) if random.random() > 0.5 else None,
                    cost=None
                )
                db.add(history_record)
                last_event_date = first_mot_date

        # Add additional history events
        for _ in range(random.randint(1, 4)):
            days_to_add = random.randint(90, 730)
            event_date_val = last_event_date + timedelta(days=days_to_add)
            if event_date_val > date.today(): 
                event_date_val = date.today()
            if event_date_val <= last_event_date:
                continue

            # Calculate mileage increase
            years_passed = (event_date_val - last_event_date).days / 365.0
            mileage_increase = int(annual_mileage * years_passed * random.uniform(0.8, 1.2))
            current_mileage_hist += mileage_increase
            current_mileage_hist = max(10, current_mileage_hist)

            event_type_val = random.choice(history_event_types)
            pass_fail_val = None
            advisory = None
            cost_val = None

            if event_type_val == "MOT":
                pass_fail_val = "PASS" if random.random() > 0.25 else "FAIL"
                advisory = random.choice(mot_advisories) if random.random() > 0.4 else None
                event_description = "MOT Test"
            elif event_type_val in ["Service", "Repair"]:
                cost_val = round(random.uniform(50, 1000), 2)
                event_description = random.choice(service_descriptions)
            else:
                event_description = f"{event_type_val} Event"

            history_record = VehicleHistory(
                vehicle_id=vehicle.id,
                event_date=event_date_val,
                event_type=event_type_val,
                event_description=event_description,
                mileage=current_mileage_hist,
                location=get_realistic_location(),
                source=random.choice(["DVSA Record", "Garage Invoice", "Service Book", "Owner Input"]),
                pass_fail=pass_fail_val,
                advisory_notes=advisory,
                cost=cost_val
            )
            db.add(history_record)
            last_event_date = event_date_val

        # Vehicle recalls (40% chance)
        if random.random() < 0.4:
            for _ in range(random.randint(1, 2)):
                recall_date_val = random_date(registration_date_val, date.today() - timedelta(days=60))
                recall_item = random.choice(recall_data)
                is_safety = "safety" in recall_item["description"].lower()
                status = random.choice(recall_statuses)
                completion = None
                if status == "Completed":
                    completion = random_date(recall_date_val, date.today())

                recall = VehicleRecall(
                    vehicle_id=vehicle.id,
                    recall_number=f"R/{year}/{str(random.randint(100, 999)).zfill(3)}",
                    recall_date=recall_date_val,
                    recall_title=recall_item["title"],
                    recall_description=recall_item["description"],
                    safety_issue=is_safety,
                    recall_status=status,
                    completion_date=completion,
                    issuing_authority=random.choice(["DVSA", "Manufacturer"]),
                    manufacturer_campaign=f"CAMP-{''.join(random.choices('0123456789ABCDEF', k=6))}"
                )
                db.add(recall)

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error committing vehicle {vin}: {e}")

    db.close()
    print(f"Successfully populated database with vehicle records.")

if __name__ == "__main__":
    print(f"Connecting to database: {DATABASE_URL}")
    create_tables_if_not_exist() 
    print("Starting data population...")
    populate_data()
    print("Data population finished.")