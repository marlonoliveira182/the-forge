#!/usr/bin/env python3
"""
Script to run the Streamlit app with comprehensive logging enabled.
This will help track down where the 'xml.etree.ElementTree.Element' object has no attribute 'error' error occurs.
"""

import os
import sys
import subprocess

def main():
    print("Starting The Forge app with debug logging enabled...")
    print("=" * 60)
    print("Logs will appear in the console below.")
    print("When you trigger the error, look for the detailed traceback.")
    print("=" * 60)
    
    # Set environment variable to enable debug logging
    env = os.environ.copy()
    env['STREAMLIT_LOG_LEVEL'] = 'debug'
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], env=env, check=True)
    except KeyboardInterrupt:
        print("\nApp stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"Error running app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 