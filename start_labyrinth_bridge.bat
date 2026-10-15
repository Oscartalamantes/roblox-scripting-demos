@echo off 
cd /d "%~dp0" 
start "Labyrinth Bridge API v2" cmd /k python -u file_bridge_api.py 
pause 
