@echo off
REM Setup script for Windows

echo ======================================
echo E-commerce BI System - Setup Script
echo ======================================
echo.

REM Check if Docker is running
echo [1/5] Checking Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)
echo   ✓ Docker is running

REM Create .env file
echo.
echo [2/5] Creating environment file...
if not exist .env (
    copy .env.example .env >nul
    echo   ✓ Created .env file
    echo   ⚠ IMPORTANT: Edit .env with your MongoDB connection details!
) else (
    echo   ✓ .env file already exists
)

REM Start PostgreSQL
echo.
echo [3/5] Starting PostgreSQL Data Warehouse...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start PostgreSQL
    pause
    exit /b 1
)
echo   ✓ PostgreSQL started

REM Wait for PostgreSQL to be ready
echo.
echo [4/5] Waiting for PostgreSQL to be ready...
timeout /t 5 /nobreak >nul
docker exec ecommerce_dw pg_isready -U bi_admin -d ecommerce_dw >nul 2>&1
if %errorlevel% neq 0 (
    echo   Waiting a bit longer...
    timeout /t 5 /nobreak >nul
)
echo   ✓ PostgreSQL is ready

REM Create Python virtual environment
echo.
echo [5/5] Setting up Python environment...
if not exist venv (
    python -m venv venv
    echo   ✓ Created virtual environment
    echo   Installing dependencies...
    call venv\Scripts\activate.bat
    pip install --quiet -r requirements.txt
    if %errorlevel% neq 0 (
        echo   ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
    echo   ✓ Dependencies installed
) else (
    echo   ✓ Virtual environment already exists
)

echo.
echo ======================================
echo Setup Complete! ✓
echo ======================================
echo.
echo Next steps:
echo 1. Edit .env file with your MongoDB connection
echo 2. Activate virtual environment: venv\Scripts\activate
echo 3. Run ETL: python etl\main.py
echo 4. Open Power BI and follow docs\powerbi_guide.md
echo.
echo For more info, see README.md or QUICKSTART.md
echo.
pause
