@echo off
rem Checks this computer for specs-builder-2. It changes nothing.
cd /d "%~dp0"
python -c "pass" >nul 2>nul
if errorlevel 1 goto nopython
python check_setup.py
pause
exit /b

:nopython
echo.
echo   MISSING  Python
echo            Windows cannot find Python. Install it: see step 2 of GETTING-STARTED.md
echo            If you have just installed it, tick "Add python.exe to PATH" and install again.
echo.
pause
exit /b 1
