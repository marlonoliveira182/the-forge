# Run script with logging for The Forge Web App
import subprocess
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_app_with_logging():
    try:
        logger.info("Starting The Forge Web App with logging...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running app: {e}")
    except KeyboardInterrupt:
        logger.info("App stopped by user")

if __name__ == "__main__":
    run_app_with_logging() 