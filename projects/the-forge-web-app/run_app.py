# Run script for The Forge Web App
import subprocess
import sys

def run_app():
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running app: {e}")
    except KeyboardInterrupt:
        print("App stopped by user")

if __name__ == "__main__":
    run_app() 