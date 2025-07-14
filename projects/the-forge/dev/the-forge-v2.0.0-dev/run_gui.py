#!/usr/bin/env python3
"""
Simple launcher for The Forge v2.0.0 GUI
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from PySide6.QtWidgets import QApplication
    from gui.main_window import MainWindow
    
    def main():
        """Launch the GUI application"""
        app = QApplication(sys.argv)
        app.setApplicationName("The Forge")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("EDP")
        
        window = MainWindow()
        window.show()
        
        print("🚀 The Forge v2.0.0 GUI is starting...")
        print("📋 Available tabs:")
        print("   - Schema Mapping: Map fields between schemas")
        print("   - Schema Conversion: Convert between XSD and JSON Schema")
        print("   - Documentation: Generate Excel documentation")
        print("   - Validation: Validate schema files")
        
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Error importing PySide6: {e}")
    print("💡 Please ensure PySide6 is installed: pip install PySide6")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting The Forge: {e}")
    sys.exit(1) 