from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone 

# Import your modules
from utils.database import init_database
from api.routes import router as api_router 
from utils.llms import model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('vehicle_insights.log')
    ]
)
logger = logging.getLogger(__name__)

def get_utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Vehicle Insights API...")
    if not init_database():
        logger.error("Failed to initialize database")
        sys.exit(1)
    
    try:
        if model is None: 
            logger.warning("⚠️  Azure OpenAI model not initialized - AI features may not work")
        else:
            logger.info("✅ Azure OpenAI model validated successfully (basic check)")
    except Exception as e:
        logger.error(f"❌ LLM configuration error: {e}")
        
    
    logger.info("✅ Vehicle Insights API started successfully")
    yield
    logger.info("🛑 Shutting down Vehicle Insights API...")

app = FastAPI(
    title="Vehicle Insights API",
    description="""...""", 
    version="1.0.0",
    contact={
        "name": "Vehicle Insights API",
        "email": "support@vehicleinsights.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  
        "http://localhost:8080",  
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_SERVER_ERROR",
            "timestamp": get_utc_timestamp() 
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException): 
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": f"HTTP_{exc.status_code}", 
            "timestamp": get_utc_timestamp() 
        }
    )

app.include_router(api_router) 

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to Vehicle Insights API",
        "version": "1.0.0",
        "description": "AI-powered vehicle information and insights platform",
        "documentation": "/docs",
        "health_check": "/api/v1/health", 
        "timestamp": get_utc_timestamp(),
        "endpoints": {
            "search_by_vin": "/api/v1/vehicle/vin/{vin}",
            "search_by_vrm": "/api/v1/vehicle/vrm/{vrm}",
            "general_search": "/api/v1/vehicle/search?q={query}"
        }
    }

@app.get("/version", tags=["utility"])
async def get_version_info(): 
    """Get API version information"""
    return {
        "api_version": "1.0.0", 
        "build_date": get_utc_timestamp(), 
        "python_version": sys.version,
        "features": [
            "VIN lookup",
            "VRM lookup", 
            "AI insights generation",
            "Vehicle history analysis",
            "Recall information",
            "Valuation data",
            "Technical specifications"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )