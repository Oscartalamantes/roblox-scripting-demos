@echo off
echo ===========================================
echo TRUE AUTOMATION DAEMON - ONE TIME SETUP
echo After this, just type in chat: make portal
echo ===========================================
echo.
echo Checking Python...
python --version
if %errorlevel% neq 0 (
  echo Python not found in PATH, trying py launcher...
  py --version
  if %errorlevel% neq 0 (
    echo ERROR: Python not found! Install Python 3.11 from python.org
    echo Make sure to check Add to PATH
    pause
    exit /b
  ) else (
    set PYTHON_CMD=py
    goto :run
  )
) else (
  set PYTHON_CMD=python
)
:run
echo.
echo Using %PYTHON_CMD%
echo Installing deps...
%PYTHON_CMD% -m pip install pyautogui --quiet
echo.
echo Starting daemon - DO NOT CLOSE THIS WINDOW
echo Leave open, then type in Meta AI chat: make portal
echo.
%PYTHON_CMD% "C:\Users\Etern\Documents\roblox-scripting-demos\TRUE_AUTO_DAEMON.py"
echo.
echo Daemon exited - error above
pause