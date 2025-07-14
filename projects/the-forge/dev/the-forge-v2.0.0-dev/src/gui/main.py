#!/usr/bin/env python3
"""
Main entry point for The Forge v2.0.0 GUI Application
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .main_window import MainWindow

def main():
    """Main entry point for the GUI application"""
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("The Forge")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("EDP")
    
    # Set application icon if available
    icon_path = Path(__file__).parent.parent.parent / "assets" / "ferreiro.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 