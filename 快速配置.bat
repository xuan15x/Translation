@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
:: AI Translation Workbench - Quick Configuration Script
:: Version: v3.0.1
:: Description: Easy-to-use configuration tool
:: ============================================================

title AI Translation Workbench - Quick Config

echo ========================================
echo   AI Translation Workbench
echo   Quick Configuration v3.0.1
echo ========================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Check config file
if not exist "config\config.json" (
    echo [INFO] Config file not found, creating new one...
    if exist "config\config.deepseek.example.json" (
        copy "config\config.deepseek.example.json" "config\config.json" >nul
        echo [OK] Config created: config\config.json
    ) else if exist "config\config.example.json" (
        copy "config\config.example.json" "config\config.json" >nul
        echo [OK] Config created: config\config.json
    ) else (
        echo [ERROR] Config example file not found
        pause
        exit /b 1
    )
    echo.
) else (
    echo [OK] Existing config found: config\config.json
    echo.
)

:: Main Menu
:MENU
echo ========================================
echo   Configuration Options
echo ========================================
echo   1. Set DeepSeek API Key
echo   2. Set Model Parameters (temperature/top_p)
echo   3. Set Concurrency Control
echo   4. Set Two-Stage Translation Params
echo   5. View Current Config
echo   6. Test API Connection
echo   7. Launch Translation Platform
echo   0. Exit
echo ========================================
echo.

set /p choice="Select option (0-7): "

if "%choice%"=="1" goto SET_API_KEY
if "%choice%"=="2" goto SET_MODEL_PARAMS
if "%choice%"=="3" goto SET_CONCURRENCY
if "%choice%"=="4" goto SET_TWO_PASS
if "%choice%"=="5" goto VIEW_CONFIG
if "%choice%"=="6" goto TEST_API
if "%choice%"=="7" goto START_APP
if "%choice%"=="0" goto EXIT

echo [ERROR] Invalid selection
echo.
goto MENU

:: ============================================================
:: 1. Set API Key
:: ============================================================
:SET_API_KEY
echo.
echo ========================================
echo   Set DeepSeek API Key
echo ========================================
echo.
echo Get your API Key from: https://platform.deepseek.com/
echo.

set /p api_key="Enter DeepSeek API Key: "

if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

:: Update config file using Python
python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_key']='!api_key!'; c['api_provider']='deepseek'; c['base_url']='https://api.deepseek.com'; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [OK] API Key has been set
echo.
pause
goto MENU

:: ============================================================
:: 2. Set Model Parameters
:: ============================================================
:SET_MODEL_PARAMS
echo.
echo ========================================
echo   Set Model Parameters
echo ========================================
echo.
echo Recommended settings:
echo   - Accurate: temperature=0.3, top_p=0.8
echo   - Balanced: temperature=0.7, top_p=0.9
echo   - Creative: temperature=1.0+, top_p=0.95
echo.

set /p temp="Enter temperature (0.0-2.0, default 0.7): "
set /p top_p="Enter top_p (0.0-1.0, default 0.9): "
set /p presence="Enter presence_penalty (-2.0~2.0, default 0.0): "
set /p frequency="Enter frequency_penalty (-2.0~2.0, default 0.0): "

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['temperature']=!temp! if '!temp!'!='' else 0.7; c['top_p']=!top_p! if '!top_p!'!='' else 0.9; c['presence_penalty']=!presence! if '!presence!'!='' else 0.0; c['frequency_penalty']=!frequency! if '!frequency!'!='' else 0.0; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [OK] Model parameters updated
echo.
pause
goto MENU

:: ============================================================
:: 3. Set Concurrency Control
:: ============================================================
:SET_CONCURRENCY
echo.
echo ========================================
echo   Set Concurrency Control
echo ========================================
echo.
echo Recommended settings:
echo   - Beginner: initial_concurrency=2, max_concurrency=5
echo   - Standard: initial_concurrency=8, max_concurrency=10
echo   - Advanced: initial_concurrency=10, max_concurrency=15
echo.

set /p initial="Enter initial_concurrency (default 8): "
set /p max="Enter max_concurrency (default 10): "

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['initial_concurrency']=!initial! if '!initial!'!='' else 8; c['max_concurrency']=!max! if '!max!'!='' else 10; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [OK] Concurrency settings updated
echo.
pause
goto MENU

:: ============================================================
:: 4. Set Two-Stage Translation Params
:: ============================================================
:SET_TWO_PASS
echo.
echo ========================================
echo   Set Two-Stage Translation Params
echo ========================================
echo.
echo Two-stage translation = Draft + Review for better quality
echo.
echo Recommended settings:
echo   - Quality first: draft_temp=0.3, review_temp=0.7
echo   - Speed first: draft_temp=0.5, review_temp=0.5
echo   - Economy mode: use same params for both stages
echo.

set /p draft_temp="Enter draft_temperature (default 0.3): "
set /p review_temp="Enter review_temperature (default 0.7): "

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['draft_temperature']=!draft_temp! if '!draft_temp!'!='' else 0.3; c['review_temperature']=!review_temp! if '!review_temp!'!='' else 0.7; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [OK] Two-stage translation params updated
echo.
pause
goto MENU

:: ============================================================
:: 5. View Current Config
:: ============================================================
:VIEW_CONFIG
echo.
echo ========================================
echo   Current Configuration
echo ========================================
echo.

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); print('API Provider:', c.get('api_provider', 'N/A')); print('Model Name:', c.get('model_name', 'N/A')); print('Temperature:', c.get('temperature', 'N/A')); print('Top P:', c.get('top_p', 'N/A')); print('Concurrency:', c.get('initial_concurrency', 'N/A'), '/', c.get('max_concurrency', 'N/A')); print('Batch Size:', c.get('batch_size', 'N/A'))"

echo.
echo Full config file: config\config.json
echo.
pause
goto MENU

:: ============================================================
:: 6. Test API Connection
:: ============================================================
:TEST_API
echo.
echo ========================================
echo   Test API Connection
echo ========================================
echo.

python scripts\test_deepseek_connection.py
if errorlevel 1 (
    echo.
    echo [ERROR] API connection test failed
    echo Please check:
    echo   1. API Key is correct
    echo   2. Network connection is working
    echo   3. Firewall settings allow API access
) else (
    echo.
    echo [OK] API connection test successful
)
echo.
pause
goto MENU

:: ============================================================
:: 7. Launch Translation Platform
:: ============================================================
:START_APP
echo.
echo ========================================
echo   Launching Translation Platform
echo ========================================
echo.

:: Check virtual environment
if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment...
    call .venv\Scripts\activate.bat
)

echo Starting translation platform...
python presentation\translation.py

goto MENU

:: ============================================================
:: 0. Exit
:: ============================================================
:EXIT
echo.
echo Thank you for using AI Translation Workbench!
echo.
pause
exit /b 0
