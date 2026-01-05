@echo off
echo ============================================================
echo   NEPPA: NHS Expert Policy Assistant
echo ============================================================
echo.
echo Starting services...
echo.
echo FastAPI will run on: http://localhost:8000
echo Streamlit will run on: http://localhost:8501
echo.
echo Press Ctrl+C to stop both services.
echo.

start "NEPPA FastAPI" cmd /k "venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
start "NEPPA Streamlit" cmd /k "venv\Scripts\python.exe -m streamlit run src/app.py --server.port 8501"

echo.
echo Services started! Check the windows that opened.
echo FastAPI: http://localhost:8000
echo Streamlit: http://localhost:8501
echo.
pause

