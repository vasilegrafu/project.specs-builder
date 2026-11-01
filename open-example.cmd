@echo off
rem Opens the example specification in your browser. Close this window to stop it.
python -c "pass" >nul 2>nul
if errorlevel 1 goto nopython
call "%~dp0.claude\skills\specs-builder-2\examples\shop\specs\index.cmd"
exit /b

:nopython
echo.
echo   Windows cannot find Python. Run check-setup.cmd first.
echo.
pause
exit /b 1
