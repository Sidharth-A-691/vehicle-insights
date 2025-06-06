
"""
Vehicle Insights API Server Runner

This script starts the FastAPI server with proper configuration.
Use this script to run your backend server in different environments.
"""

import uvicorn
import sys
import os
import argparse
from pathlib import Path

def setup_environment():
    """Setup environment and paths"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set default environment variables if not set
    os.environ.setdefault("PYTHONPATH", str(current_dir))

def run_development_server(host="127.0.0.1", port=8000):
    """Run development server with hot reload"""
    print("🔄 Starting Vehicle Insights API in DEVELOPMENT mode...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print("📚 API Documentation: http://{host}:{port}/docs")
    print("🔄 Hot reload enabled - server will restart on code changes")
    print("-" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=["./"],
        log_level="info",
        access_log=True
    )

def run_production_server(host="0.0.0.0", port=8000, workers=1):
    """Run production server"""
    print("🚀 Starting Vehicle Insights API in PRODUCTION mode...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"👥 Workers: {workers}")
    print("-" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        workers=workers,
        log_level="info",
        access_log=True,
        reload=False
    )

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy", 
        "langchain-openai",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment_variables():
    """Check if required environment variables are set"""
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set environment variables or create a .env file")
        print("   AI features may not work without proper configuration")
        return False
    
    return True

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Vehicle Insights API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # Development mode on 127.0.0.1:8000
  python run.py --prod                   # Production mode on 0.0.0.0:8000
  python run.py --host 0.0.0.0 --port 9000  # Custom host and port
  python run.py --prod --workers 4      # Production with 4 workers
        """
    )
    
    parser.add_argument(
        "--host", 
        default="127.0.0.1", 
        help="Host to bind to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--prod", 
        action="store_true", 
        help="Run in production mode"
    )
    
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (production mode only)"
    )
    
    parser.add_argument(
        "--skip-checks", 
        action="store_true", 
        help="Skip environment and dependency checks"
    )
    
    args = parser.parse_args()
    
    setup_environment()
    
    if not args.skip_checks:
        print("🔍 Checking requirements...")
        
        if not check_requirements():
            sys.exit(1)
        
        if not check_environment_variables():
            print("⚠️  Continuing with warnings...")
    
    if args.prod:
        if args.host == "127.0.0.1":
            args.host = "0.0.0.0"  
    
    try:
        if args.prod:
            run_production_server(args.host, args.port, args.workers)
        else:
            run_development_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()