#!/usr/bin/env python3
"""
The Forge v2 - Main Entry Point

Schema conversion and mapping tool with both CLI and GUI interfaces.
Provides conversion between XSD and JSON Schema formats with Excel documentation.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.cli_interface import CLIInterface
from src.gui.gui_interface import GUIInterface


def main():
    """
    Main entry point for the-forge-v2.
    
    Provides both CLI and GUI interfaces:
    - CLI: Command-line interface for automation and scripting
    - GUI: Graphical interface for interactive use
    """
    
    # Check if GUI mode is requested
    if len(sys.argv) > 1 and sys.argv[1] in ['--gui', '-g', 'gui']:
        # Launch GUI
        gui = GUIInterface()
        gui.run()
    else:
        # Launch CLI
        cli = CLIInterface()
        exit_code = cli.run()
        sys.exit(exit_code)


if __name__ == "__main__":
    main() 