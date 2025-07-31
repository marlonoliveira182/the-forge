#!/usr/bin/env python3
"""
The Forge Web App Runner
A simple script to run the Streamlit application
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Change to the script directory
        os.chdir(script_dir)
        
        # Run streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"]
        
        print("🚀 Starting The Forge Web App...")
        print("📱 Open your browser to: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down The Forge Web App...")
    except Exception as e:
        print(f"❌ Error starting the app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 