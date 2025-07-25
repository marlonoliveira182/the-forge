@echo off
REM Ensure we are in the script directory
cd /d %~dp0

REM Check if venv exists
if not exist venv\Scripts\activate.bat (
    echo [ERROR] venv not found! Please create it with: python -m venv venv
    pause
    exit /b 1
)

REM Activate the venv
call venv\Scripts\activate.bat

REM Run the new PySide6 GUI
python forge_qt_app.py
REM To run the old Flet GUI, comment the line above and uncomment the line below
REM python forge_flet_app.py 