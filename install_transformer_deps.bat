@echo off
REM Installation script for Transformer-based Sehat Nabha application
REM This script installs all required Python packages

echo ========================================
echo Sehat Nabha - Transformer Model Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/5] Updating pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto error

echo.
echo [2/5] Installing core dependencies...
python -m pip install numpy pandas scikit-learn pyyaml
if errorlevel 1 goto error

echo.
echo [3/5] Installing Flask and CORS...
python -m pip install flask==3.0.0 flask-cors==4.0.0 gunicorn
if errorlevel 1 goto error

echo.
echo [4/5] Installing Transformer Libraries...
echo This may take a few minutes...
python -m pip install torch>=2.0.0 transformers>=4.30.0
if errorlevel 1 goto error

echo.
echo [5/5] Installing Additional ML Libraries...
python -m pip install sentence-transformers==2.2.2 faiss-cpu==1.12.0 Cython
if errorlevel 1 goto error

echo.
echo ========================================
echo ✓ All dependencies installed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Start the Python API server:
echo    python api_server.py
echo.
echo 2. In another terminal, start the React frontend:
echo    npm run dev
echo.
echo 3. Open browser and navigate to http://localhost:3000
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo ✗ Installation failed!
echo ========================================
echo.
echo Please check the error messages above and try again.
echo If you continue to have issues, please ensure:
echo 1. Python 3.8+ is installed
echo 2. You have internet connection
echo 3. You have enough disk space (~3GB for transformer models)
echo.
pause
exit /b 1
