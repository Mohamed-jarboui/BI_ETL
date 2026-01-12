@echo off
REM Run ETL Pipeline

echo ======================================
echo E-commerce ETL Pipeline
echo ======================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if PostgreSQL is running
echo Checking PostgreSQL...
docker ps | findstr ecommerce_dw >nul
if %errorlevel% neq 0 (
    echo ERROR: PostgreSQL container is not running!
    echo Please run: docker-compose up -d
    pause
    exit /b 1
)
echo ✓ PostgreSQL is running
echo.

REM Run ETL
echo Starting ETL Pipeline...
echo.
python etl\main.py %*

echo.
if %errorlevel% equ 0 (
    echo ======================================
    echo ✓ ETL Pipeline Completed Successfully
    echo ======================================
    echo.
    echo Next steps:
    echo 1. Verify data: docker exec -it ecommerce_dw psql -U bi_admin -d ecommerce_dw -f sql\verify_data.sql
    echo 2. Open Power BI Desktop
    echo 3. Follow docs\powerbi_guide.md
) else (
    echo ======================================
    echo ✗ ETL Pipeline Failed
    echo ======================================
    echo Check logs\etl_pipeline.log for details
)
echo.
pause
