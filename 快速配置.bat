@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
:: AI 智能翻译工作台 - DeepSeek 快速配置脚本
:: 版本：v3.0.1
:: 说明：Windows 下直接运行的配置工具，降低使用门槛
:: ============================================================

title AI 智能翻译工作台 - DeepSeek 快速配置

echo ========================================
echo   AI 智能翻译工作台 - DeepSeek 快速配置
echo   版本：v3.0.1
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [✓] Python 已安装
echo.

:: 检查配置文件是否存在
if not exist "config\config.json" (
    echo [提示] 未找到配置文件，将创建新的配置文件...
    if exist "config\config.deepseek.example.json" (
        copy "config\config.deepseek.example.json" "config\config.json" >nul
        echo [✓] 已创建配置文件：config\config.json
    ) else if exist "config\config.example.json" (
        copy "config\config.example.json" "config\config.json" >nul
        echo [✓] 已创建配置文件：config\config.json
    ) else (
        echo [错误] 未找到配置示例文件
        pause
        exit /b 1
    )
    echo.
) else (
    echo [✓] 检测到现有配置文件：config\config.json
    echo.
)

:: 主菜单
:MENU
echo ========================================
echo   配置选项
echo ========================================
echo   1. 设置 DeepSeek API Key
echo   2. 设置模型参数（温度/Top P 等）
echo   3. 设置并发控制
echo   4. 设置双阶段翻译参数
echo   5. 查看当前配置
echo   6. 测试 API 连接
echo   7. 启动翻译平台
echo   0. 退出
echo ========================================
echo.

set /p choice="请选择操作 (0-7): "

if "%choice%"=="1" goto SET_API_KEY
if "%choice%"=="2" goto SET_MODEL_PARAMS
if "%choice%"=="3" goto SET_CONCURRENCY
if "%choice%"=="4" goto SET_TWO_PASS
if "%choice%"=="5" goto VIEW_CONFIG
if "%choice%"=="6" goto TEST_API
if "%choice%"=="7" goto START_APP
if "%choice%"=="0" goto EXIT

echo [错误] 无效的选择
echo.
goto MENU

:: ============================================================
:: 1. 设置 API Key
:: ============================================================
:SET_API_KEY
echo.
echo ========================================
echo   设置 DeepSeek API Key
echo ========================================
echo.
echo 请前往 https://platform.deepseek.com/ 获取 API Key
echo.

set /p api_key="请输入 DeepSeek API Key: "

if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

:: 使用 Python 脚本更新配置文件
python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_key']='!api_key!'; c['api_provider']='deepseek'; c['base_url']='https://api.deepseek.com'; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [✓] API Key 已设置
echo.
pause
goto MENU

:: ============================================================
:: 2. 设置模型参数
:: ============================================================
:SET_MODEL_PARAMS
echo.
echo ========================================
echo   设置模型参数
echo ========================================
echo.
echo 推荐配置:
echo   - 准确翻译：temperature=0.3, top_p=0.8
echo   - 平衡模式：temperature=0.7, top_p=0.9
echo   - 创意翻译：temperature=1.0+, top_p=0.95
echo.

set /p temp="请输入 temperature (0.0-2.0, 默认 0.7): "
set /p top_p="请输入 top_p (0.0-1.0, 默认 0.9): "
set /p presence="请输入 presence_penalty (-2.0~2.0, 默认 0.0): "
set /p frequency="请输入 frequency_penalty (-2.0~2.0, 默认 0.0): "

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['temperature']=!temp! if '!temp!'!='' else 0.7; c['top_p']=!top_p! if '!top_p!'!='' else 0.9; c['presence_penalty']=!presence! if '!presence!'!='' else 0.0; c['frequency_penalty']=!frequency! if '!frequency!'!='' else 0.0; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [✓] 模型参数已更新
echo.
pause
goto MENU

:: ============================================================
:: 3. 设置并发控制
:: ============================================================
:SET_CONCURRENCY
echo.
echo ========================================
echo   设置并发控制
echo ========================================
echo.
echo 推荐配置:
echo   - 新手：initial_concurrency=2, max_concurrency=5
echo   - 常规：initial_concurrency=8, max_concurrency=10
echo   - 高级：initial_concurrency=10, max_concurrency=15
echo.

set /p initial="请输入 initial_concurrency (默认 8): "
set /p max="请输入 max_concurrency (默认 10): "

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['initial_concurrency']=!initial! if '!initial!'!='' else 8; c['max_concurrency']=!max! if '!max!'!='' else 10; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [✓] 并发控制已更新
echo.
pause
goto MENU

:: ============================================================
:: 4. 设置双阶段翻译参数
:: ============================================================
:SET_TWO_PASS
echo.
echo ========================================
echo   设置双阶段翻译参数
echo ========================================
echo.
echo 双阶段翻译 = 初译 + 校对，确保翻译质量
echo.
echo 推荐配置:
echo   - 质量优先：draft_temp=0.3, review_temp=0.7
echo   - 速度优先：draft_temp=0.5, review_temp=0.5
echo   - 经济模式：两阶段使用相同参数
echo.

set /p draft_temp="请输入 draft_temperature (默认 0.3): "
set /p review_temp="请输入 review_temperature (默认 0.7): "

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['draft_temperature']=!draft_temp! if '!draft_temp!'!='' else 0.3; c['review_temperature']=!review_temp! if '!review_temp!'!='' else 0.7; f=open('config\config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo [✓] 双阶段翻译参数已更新
echo.
pause
goto MENU

:: ============================================================
:: 5. 查看当前配置
:: ============================================================
:VIEW_CONFIG
echo.
echo ========================================
echo   当前配置
echo ========================================
echo.

python -c "import json; f=open('config\config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); print('API 提供商:', c.get('api_provider', 'N/A')); print('模型名称:', c.get('model_name', 'N/A')); print('Temperature:', c.get('temperature', 'N/A')); print('Top P:', c.get('top_p', 'N/A')); print('并发数:', c.get('initial_concurrency', 'N/A'), '/', c.get('max_concurrency', 'N/A')); print('批量大小:', c.get('batch_size', 'N/A'))"

echo.
echo 完整配置文件：config\config.json
echo.
pause
goto MENU

:: ============================================================
:: 6. 测试 API 连接
:: ============================================================
:TEST_API
echo.
echo ========================================
echo   测试 API 连接
echo ========================================
echo.

python scripts\test_deepseek_connection.py
if errorlevel 1 (
    echo.
    echo [错误] API 连接测试失败
    echo 请检查:
    echo   1. API Key 是否正确
    echo   2. 网络连接是否正常
    echo   3. 防火墙设置
) else (
    echo.
    echo [✓] API 连接测试成功
)
echo.
pause
goto MENU

:: ============================================================
:: 7. 启动翻译平台
:: ============================================================
:START_APP
echo.
echo ========================================
echo   启动翻译平台
echo ========================================
echo.

:: 检查虚拟环境
if exist ".venv\Scripts\python.exe" (
    echo [提示] 使用虚拟环境...
    call .venv\Scripts\activate.bat
)

echo 正在启动翻译平台...
python presentation\translation.py

goto MENU

:: ============================================================
:: 0. 退出
:: ============================================================
:EXIT
echo.
echo 感谢使用 AI 智能翻译工作台！
echo.
pause
exit /b 0
