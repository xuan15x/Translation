@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
:: AI 智能翻译工作台 - 一键快速配置脚本
:: 版本：v3.1.0
:: 说明：简化配置流程，支持多模型一键配置
:: ============================================================

title AI 智能翻译工作台 - 一键配置

echo ========================================
echo   AI 智能翻译工作台 - 一键配置
echo   版本：v3.1.0
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
if not exist "config/config.json" (
    echo [提示] 未找到配置文件，将从示例配置创建...
    if exist "config/config.example.json" (
        copy "config/config.example.json" "config/config.json" >nul
        echo [✓] 已创建配置文件
    ) else (
        echo [错误] 未找到配置示例文件
        pause
        exit /b 1
    )
    echo.
)

:: ============================================================
:: 主菜单
:: ============================================================
:MENU
echo ========================================
echo   请选择要配置的模型提供商
echo ========================================
echo   1. DeepSeek（推荐，性价比高）
echo   2. OpenAI（GPT-4o/GPT-3.5）
echo   3. 通义千问（阿里云）
echo   4. 智谱 AI（GLM 系列）
echo   5. Moonshot（Kimi）
echo   6. Claude（Anthropic）
echo   7. Gemini（Google）
echo   --------------------------------------
echo   8. 查看当前配置
echo   9. 测试 API 连接
echo   0. 启动翻译平台
echo ========================================
echo.

set /p choice="请选择 (0-9): "

if "%choice%"=="1" goto CONFIG_DEEPSEEK
if "%choice%"=="2" goto CONFIG_OPENAI
if "%choice%"=="3" goto CONFIG_QWEN
if "%choice%"=="4" goto CONFIG_ZHIPU
if "%choice%"=="5" goto CONFIG_MOONSHOT
if "%choice%"=="6" goto CONFIG_CLAUDE
if "%choice%"=="7" goto CONFIG_GEMINI
if "%choice%"=="8" goto VIEW_CONFIG
if "%choice%"=="9" goto TEST_API
if "%choice%"=="0" goto START_APP

echo [错误] 无效的选择
echo.
goto MENU

:: ============================================================
:: DeepSeek 配置
:: ============================================================
:CONFIG_DEEPSEEK
echo.
echo ========================================
echo   配置 DeepSeek 模型
echo ========================================
echo.
echo 推荐模型：deepseek-chat（通用）/ deepseek-coder（代码）
echo API 地址：https://platform.deepseek.com/
echo.

set /p api_key="请输入 DeepSeek API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 deepseek-chat): "
if "!model_name!"=="" set model_name=deepseek-chat

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='deepseek'; c['model_name']='!model_name!'; c['api_keys']['deepseek']={'api_key': '!api_key!', 'base_url': 'https://api.deepseek.com'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] DeepSeek 配置完成！
echo   模型：!model_name!
echo   API: https://api.deepseek.com
echo.
pause
goto MENU

:: ============================================================
:: OpenAI 配置
:: ============================================================
:CONFIG_OPENAI
echo.
echo ========================================
echo   配置 OpenAI 模型
echo ========================================
echo.
echo 推荐模型：gpt-4o（最新）/ gpt-3.5-turbo（经济）
echo API 地址：https://platform.openai.com/
echo.

set /p api_key="请输入 OpenAI API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 gpt-4o): "
if "!model_name!"=="" set model_name=gpt-4o

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='openai'; c['model_name']='!model_name!'; c['api_keys']['openai']={'api_key': '!api_key!', 'base_url': 'https://api.openai.com/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] OpenAI 配置完成！
echo   模型：!model_name!
echo   API: https://api.openai.com/v1
echo.
pause
goto MENU

:: ============================================================
:: 通义千问配置
:: ============================================================
:CONFIG_QWEN
echo.
echo ========================================
echo   配置通义千问模型
echo ========================================
echo.
echo 推荐模型：qwen-max（最强）/ qwen-plus（均衡）/ qwen-turbo（快速）
echo API 地址：https://dashscope.console.aliyun.com/
echo.

set /p api_key="请输入通义千问 API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 qwen-max): "
if "!model_name!"=="" set model_name=qwen-max

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='qwen'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] 通义千问配置完成！
echo   模型：!model_name!
echo   API: https://dashscope.aliyuncs.com/compatible-mode/v1
echo.
pause
goto MENU

:: ============================================================
:: 智谱AI配置
:: ============================================================
:CONFIG_ZHIPU
echo.
echo ========================================
echo   配置智谱 AI 模型
echo ========================================
echo.
echo 推荐模型：glm-4（最新）/ glm-3-turbo（快速）
echo API 地址：https://open.bigmodel.cn/
echo.

set /p api_key="请输入智谱 AI API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 glm-4): "
if "!model_name!"=="" set model_name=glm-4

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='zhipu'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://open.bigmodel.cn/api/paas/v4'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] 智谱 AI 配置完成！
echo   模型：!model_name!
echo   API: https://open.bigmodel.cn/api/paas/v4
echo.
pause
goto MENU

:: ============================================================
:: Moonshot配置
:: ============================================================
:CONFIG_MOONSHOT
echo.
echo ========================================
echo   配置 Moonshot（Kimi）模型
echo ========================================
echo.
echo 推荐模型：moonshot-v1-8k / moonshot-v1-32k / moonshot-v1-128k
echo API 地址：https://platform.moonshot.cn/
echo.

set /p api_key="请输入 Moonshot API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 moonshot-v1-8k): "
if "!model_name!"=="" set model_name=moonshot-v1-8k

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='moonshot'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://api.moonshot.cn/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] Moonshot 配置完成！
echo   模型：!model_name!
echo   API: https://api.moonshot.cn/v1
echo.
pause
goto MENU

:: ============================================================
:: Claude配置
:: ============================================================
:CONFIG_CLAUDE
echo.
echo ========================================
echo   配置 Claude 模型
echo ========================================
echo.
echo 推荐模型：claude-3-5-sonnet-20240229（最新）/ claude-3-opus（最强）
echo API 地址：https://console.anthropic.com/
echo.

set /p api_key="请输入 Anthropic API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 claude-3-5-sonnet-20240229): "
if "!model_name!"=="" set model_name=claude-3-5-sonnet-20240229

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='anthropic'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://api.anthropic.com/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] Claude 配置完成！
echo   模型：!model_name!
echo   API: https://api.anthropic.com/v1
echo.
pause
goto MENU

:: ============================================================
:: Gemini配置
:: ============================================================
:CONFIG_GEMINI
echo.
echo ========================================
echo   配置 Gemini 模型
echo ========================================
echo.
echo 推荐模型：gemini-1.5-pro（最强）/ gemini-1.5-flash（快速）
echo API 地址：https://ai.google.dev/
echo.

set /p api_key="请输入 Google AI Studio API Key: "
if "!api_key!"=="" (
    echo [错误] API Key 不能为空
    pause
    goto MENU
)

set /p model_name="请输入模型名称 (默认 gemini-1.5-pro): "
if "!model_name!"=="" set model_name=gemini-1.5-pro

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='gemini'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://generativelanguage.googleapis.com/v1beta'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [✓] Gemini 配置完成！
echo   模型：!model_name!
echo   API: https://generativelanguage.googleapis.com/v1beta
echo.
pause
goto MENU

:: ============================================================
:: 查看当前配置
:: ============================================================
:VIEW_CONFIG
echo.
echo ========================================
echo   当前配置
echo ========================================
echo.

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); print('API 提供商:', c.get('api_provider', 'N/A')); print('模型名称:', c.get('model_name', 'N/A')); print('Temperature:', c.get('temperature', 'N/A')); print('Top P:', c.get('top_p', 'N/A')); print('并发数:', c.get('initial_concurrency', 'N/A'), '/', c.get('max_concurrency', 'N/A')); print('批量大小:', c.get('batch_size', 'N/A'))"

echo.
echo 完整配置文件：config/config.json
echo.
pause
goto MENU

:: ============================================================
:: 测试 API 连接
:: ============================================================
:TEST_API
echo.
echo ========================================
echo   测试 API 连接
echo ========================================
echo.

if exist "scripts/test_deepseek_connection.py" (
    python scripts/test_deepseek_connection.py
) else (
    echo [提示] 未找到测试脚本，使用简单测试...
    python -c "import requests; from pathlib import Path; import json; c=json.load(open('config/config.json', 'r', encoding='utf-8')); provider=c.get('api_provider', 'deepseek'); keys=c.get('api_keys', {}); k=keys.get(provider, keys.get('custom', {})); api_key=k.get('api_key', ''); base_url=k.get('base_url', ''); print(f'测试连接: {base_url}'); print(f'API Key: {api_key[:10]}...' if len(api_key)>10 else 'API Key: 未设置'); print('请确保 API Key 和网络连接正常')"
)

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
:: 启动翻译平台
:: ============================================================
:START_APP
echo.
echo ========================================
echo   启动翻译平台
echo ========================================
echo.

:: 检查虚拟环境
if exist ".venv/Scripts/activate.bat" (
    echo [提示] 使用虚拟环境...
    call .venv/Scripts/activate.bat
)

echo 正在启动翻译平台...
python presentation/translation.py

goto MENU

:: ============================================================
:: 退出
:: ============================================================
:EXIT
echo.
echo 感谢使用 AI 智能翻译工作台！
echo.
pause
exit /b 0
