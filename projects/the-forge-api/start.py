#!/usr/bin/env python3
"""
Startup script for The Forge API
Provides easy local development and testing
"""

import uvicorn
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Start The Forge API")
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run tests after starting server"
    )
    
    args = parser.parse_args()
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("Error: main.py not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    # Create temp directory if it doesn't exist
    Path("temp").mkdir(exist_ok=True)
    
    print(f"Starting The Forge API on {args.host}:{args.port}")
    print("API Documentation will be available at:")
    print(f"  - Swagger UI: http://{args.host}:{args.port}/docs")
    print(f"  - ReDoc: http://{args.host}:{args.port}/redoc")
    print(f"  - Health Check: http://{args.host}:{args.port}/api/health")
    
    if args.test:
        print("\nRunning tests...")
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "test_api.py", f"http://{args.host}:{args.port}"
            ], capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except Exception as e:
            print(f"Test error: {e}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 