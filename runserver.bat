@echo off
REM Navigate to the project folder
cd /d "C:\Users\msudh\OneDrive\Desktop\data visualizer"

REM Activate virtual environment if you have one
REM call venv\Scripts\activate

REM Start Django server in a separate window
start cmd /k "python manage.py runserver"

REM Wait a few seconds for the server to start
timeout /t 5 /nobreak >nul

REM Open default browser at localhost
start http://127.0.0.1:8000/

pause
