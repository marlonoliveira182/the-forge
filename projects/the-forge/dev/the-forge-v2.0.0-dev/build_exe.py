#!/usr/bin/env python3
"""
Build script for The Forge v2.0.0 - Creates standalone executable
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """Build the standalone executable using PyInstaller"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window for GUI
        "--name=TheForge",  # Executable name
        "--icon=assets/ferreiro.ico",  # Application icon
        "--add-data=assets;assets",  # Include assets
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui", 
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=xmlschema",
        "--hidden-import=jsonschema",
        "--hidden-import=openpyxl",
        "--hidden-import=pandas",
        "--hidden-import=lxml",
        "--hidden-import=pydantic",
        "--clean",  # Clean cache
        "--noconfirm",  # Overwrite without asking
        str(src_dir / "gui" / "main.py")  # Main entry point
    ]
    
    print("Building The Forge v2.0.0 executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, cwd=project_root, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(f"Executable location: {project_root / 'dist' / 'TheForge.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def build_cli_executable():
    """Build CLI version of the executable"""
    
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--name=TheForgeCLI",
        "--icon=assets/ferreiro.ico",
        "--add-data=assets;assets",
        "--hidden-import=xmlschema",
        "--hidden-import=jsonschema", 
        "--hidden-import=openpyxl",
        "--hidden-import=pandas",
        "--hidden-import=lxml",
        "--hidden-import=pydantic",
        "--clean",
        "--noconfirm",
        str(src_dir / "cli" / "main.py")
    ]
    
    print("Building The Forge CLI executable...")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True, capture_output=True, text=True)
        print("CLI build completed successfully!")
        print(f"CLI executable location: {project_root / 'dist' / 'TheForgeCLI.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"CLI build failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        success = build_cli_executable()
    else:
        success = build_executable()
    
    if success:
        print("\n✅ Build completed successfully!")
        print("The executable is ready for distribution.")
    else:
        print("\n❌ Build failed!")
        sys.exit(1) 