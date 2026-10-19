@echo off
echo Starting OscarAI Official App...
cd /d %~dp0..
python -m pip install fastapi uvicorn jinja2 --quiet
python app.py
pause
