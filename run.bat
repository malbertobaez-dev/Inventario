@echo off
echo ====================================
echo   Inventario Slow Movement Dashboard
echo ====================================
echo.

:: Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

:: Run the app
streamlit run app/main.py --server.port 8501
