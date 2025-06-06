from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
from utils.config import settings

from models import Base  

DATABASE_URL = settings.DATABASE_URL
    
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """
    Dependency function to get database session
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    # Base is now imported from models
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

def drop_tables():
    """Drop all database tables (use with caution!)"""
    # Base is now imported from models
    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")

def init_database():
    """Initialize database with tables"""
    try:
        create_tables()
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False