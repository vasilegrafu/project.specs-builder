@echo off
rem Opens this specification: starts its application and the browser on it. Close this window to stop it.
python "%~dp0app\serve.py" --open %*
if errorlevel 1 pause
