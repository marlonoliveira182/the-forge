@echo off
echo ========================================
echo The Forge v8.0.0 - Package for Distribution
echo ========================================

echo.
echo Creating distribution package...

REM Create distribution folder
if not exist "TheForge_v8_Distribution" mkdir "TheForge_v8_Distribution"

REM Copy executable
copy "dist\TheForge_v8.exe" "TheForge_v8_Distribution\"

REM Copy documentation
copy "INSTALACAO_EXE.md" "TheForge_v8_Distribution\"
copy "README_VENV.md" "TheForge_v8_Distribution\"

REM Copy requirements for reference
copy "requirements.txt" "TheForge_v8_Distribution\"

REM Create a simple README for the distribution
echo The Forge v8.0.0 > "TheForge_v8_Distribution\README.txt"
echo ======================== >> "TheForge_v8_Distribution\README.txt"
echo. >> "TheForge_v8_Distribution\README.txt"
echo Para executar: >> "TheForge_v8_Distribution\README.txt"
echo 1. Clique duas vezes em TheForge_v8.exe >> "TheForge_v8_Distribution\README.txt"
echo 2. Ou crie um atalho na area de trabalho >> "TheForge_v8_Distribution\README.txt"
echo. >> "TheForge_v8_Distribution\README.txt"
echo Para mais informacoes, leia INSTALACAO_EXE.md >> "TheForge_v8_Distribution\README.txt"

echo.
echo ========================================
echo Distribution package created successfully!
echo ========================================
echo.
echo Files in TheForge_v8_Distribution:
dir "TheForge_v8_Distribution"
echo.
echo You can now distribute the TheForge_v8_Distribution folder.
pause 