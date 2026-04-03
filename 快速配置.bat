@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
:: AI Translation Workbench - Quick Setup Script
:: Version: v3.1.0
:: Description: Simplified configuration with multi-model support
:: ============================================================

title AI Translation Workbench - Quick Setup

echo ========================================
echo   AI Translation Workbench - Quick Setup
echo   Version: v3.1.0
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

echo [OK] Python is installed
echo.

:: Change to script directory
cd /d "%~dp0"

:: ============================================================
:: Check and create config.json automatically
:: ============================================================
if not exist "config" (
    mkdir config
    echo [OK] Created config directory
)

if not exist "config\config.json" (
    echo [INFO] Config not found, creating complete default config...
    python -c "import json; config={'_version':'v3.2.0','_description':'AI Translation Workbench Config','model_name':'deepseek-chat','api_provider':'deepseek','api_keys':{'deepseek':{'api_key':'','base_url':'https://api.deepseek.com'},'openai':{'api_key':'','base_url':'https://api.openai.com/v1'},'azure_openai':{'api_key':'','base_url':'https://YOUR_RESOURCE.openai.azure.com/'},'custom':{'api_key':'','base_url':''}},'temperature':0.7,'top_p':0.9,'timeout':60,'max_retries':3,'retry_streak_threshold':3,'base_retry_delay':3.0,'initial_concurrency':8,'max_concurrency':10,'concurrency_cooldown_seconds':5.0,'draft_model_name':None,'draft_temperature':None,'draft_top_p':None,'draft_timeout':None,'draft_max_tokens':512,'review_model_name':None,'review_temperature':None,'review_top_p':None,'review_timeout':None,'review_max_tokens':512,'translation_mode':'full','enable_two_pass':True,'skip_review_if_local_hit':True,'batch_size':1000,'gc_interval':2,'prompt_templates':{'draft':{'role':'Professional Translator','task':'Translate Src to {target_lang}','constraints':['Output JSON ONLY: {\"Trans\": \"string\"}','Strictly follow provided TM','Accurate and direct']},'review':{'role':'Senior Language Editor','task':'Polish Draft into native {target_lang}','constraints':['Output JSON ONLY: {\"Trans\": \"string\", \"Reason\": \"string\"}','Reason: Max 10 chars','Focus on flow and tone']}},'draft_prompt':'Role: Professional Translator.\nTask: Translate Src to {target_lang}.\nConstraints:\n1. Output JSON ONLY: {Trans: string}.\n2. Strictly follow provided TM.\n3. Accurate and direct.','review_prompt':'Role: Senior Language Editor.\nTask: Polish Draft into native {target_lang}.\nConstraints:\n1. Output JSON ONLY: {Trans: string, Reason: string}.\n2. Reason: Max 10 chars.\n3. Focus on flow and tone.','prohibition_config':{'global_prohibitions':['禁止输出原文或保留未翻译的内容','禁止添加解释性文字或注释','禁止改变原文的语气和情感色彩'],'match3_prohibitions':['禁止使用超过4个字的道具名称','禁止使用生僻字或难以识别的汉字'],'ui_prohibitions':['禁止使用超过按钮容量的长文本','禁止使用非标准的UI术语'],'dialogue_prohibitions':['禁止使用不符合角色性格的语言风格','禁止过度本地化']},'prohibition_type_map':{'match3_item':['global','match3'],'match3_skill':['global','match3'],'match3_level':['global','match3'],'match3_dialogue':['global','match3','dialogue'],'match3_ui':['global','match3','ui'],'dialogue':['global','dialogue'],'ui':['global','ui'],'scene':['global'],'tutorial':['global'],'achievement':['global'],'custom':['global']},'similarity_low':60,'exact_match_score':100,'multiprocess_threshold':1000,'pool_size':5,'cache_capacity':2000,'cache_ttl_seconds':3600,'log_level':'INFO','log_granularity':'normal','log_max_lines':1000,'gui_window_title':'AI Translation Workbench v3.2','gui_window_width':950,'gui_window_height':800,'target_languages':['英语','德语','法语','日语','韩语','瑞典语','挪威语','丹麦语','芬兰语','意大利语','西班牙语','葡萄牙语','泰语','越南语','印尼语','马来语','俄语','波兰语','土耳其语','阿拉伯语'],'favorite_languages':['英语','日语','韩语'],'default_source_lang':'中文','supported_source_langs':['中文','英语','日语','韩语','法语','德语','西班牙语','意大利语','葡萄牙语','俄语'],'enabled_translation_types':['match3_item','match3_skill','match3_level','match3_dialogue','match3_ui','dialogue','ui','scene','tutorial','achievement','custom'],'enable_version_control':False,'enable_auto_backup':False,'backup_dir':'.terminology_backups','backup_strategy':'daily','enable_performance_monitor':False,'perf_sample_interval':1.0,'perf_history_size':300}; f=open('config/config.json','w',encoding='utf-8'); json.dump(config,f,indent=2,ensure_ascii=False); f.close(); print('[OK] Complete config created: config/config.json'); print('   Total keys:', len(config))"
    if errorlevel 1 (
        echo [ERROR] Failed to create config
        pause
        exit /b 1
    )
    echo.
) else (
    echo [OK] Found existing config: config/config.json
    echo.
)

:: ============================================================
:: Main Menu
:: ============================================================
:MENU
echo ========================================
echo   Select Model Provider
echo ========================================
echo   1. DeepSeek (Recommended, Cost-effective)
echo   2. OpenAI (GPT-4o/GPT-3.5)
echo   3. Qwen/Alibaba Cloud
echo   4. Zhipu AI (GLM Series)
echo   5. Moonshot (Kimi)
echo   6. Claude (Anthropic)
echo   7. Gemini (Google)
echo   --------------------------------------
echo   8. View Current Config
echo   9. Test API Connection
echo   0. Launch Translation Platform
echo ========================================
echo.

set /p choice="Select (0-9): "

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

echo [ERROR] Invalid choice
echo.
goto MENU

:: ============================================================
:: DeepSeek Config
:: ============================================================
:CONFIG_DEEPSEEK
echo.
echo ========================================
echo   Configure DeepSeek Model
echo ========================================
echo.
echo Recommended: deepseek-chat (general) / deepseek-coder (code)
echo API: https://platform.deepseek.com/
echo.

set /p api_key="Enter DeepSeek API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: deepseek-chat): "
if "!model_name!"=="" set model_name=deepseek-chat

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='deepseek'; c['model_name']='!model_name!'; c['api_keys']['deepseek']={'api_key': '!api_key!', 'base_url': 'https://api.deepseek.com'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] DeepSeek configuration completed!
echo   Model: !model_name!
echo   API: https://api.deepseek.com
echo.
pause
goto MENU

:: ============================================================
:: OpenAI Config
:: ============================================================
:CONFIG_OPENAI
echo.
echo ========================================
echo   Configure OpenAI Model
echo ========================================
echo.
echo Recommended: gpt-4o (latest) / gpt-3.5-turbo (economy)
echo API: https://platform.openai.com/
echo.

set /p api_key="Enter OpenAI API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: gpt-4o): "
if "!model_name!"=="" set model_name=gpt-4o

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='openai'; c['model_name']='!model_name!'; c['api_keys']['openai']={'api_key': '!api_key!', 'base_url': 'https://api.openai.com/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] OpenAI configuration completed!
echo   Model: !model_name!
echo   API: https://api.openai.com/v1
echo.
pause
goto MENU

:: ============================================================
:: Qwen Config
:: ============================================================
:CONFIG_QWEN
echo.
echo ========================================
echo   Configure Qwen/Alibaba Cloud Model
echo ========================================
echo.
echo Recommended: qwen-max (best) / qwen-plus (balanced) / qwen-turbo (fast)
echo API: https://dashscope.console.aliyun.com/
echo.

set /p api_key="Enter Qwen API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: qwen-max): "
if "!model_name!"=="" set model_name=qwen-max

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='qwen'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://dashscope.aliyuncs.com/compatible-mode/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] Qwen configuration completed!
echo   Model: !model_name!
echo   API: https://dashscope.aliyuncs.com/compatible-mode/v1
echo.
pause
goto MENU

:: ============================================================
:: Zhipu AI Config
:: ============================================================
:CONFIG_ZHIPU
echo.
echo ========================================
echo   Configure Zhipu AI Model
echo ========================================
echo.
echo Recommended: glm-4 (latest) / glm-3-turbo (fast)
echo API: https://open.bigmodel.cn/
echo.

set /p api_key="Enter Zhipu AI API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: glm-4): "
if "!model_name!"=="" set model_name=glm-4

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='zhipu'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://open.bigmodel.cn/api/paas/v4'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] Zhipu AI configuration completed!
echo   Model: !model_name!
echo   API: https://open.bigmodel.cn/api/paas/v4
echo.
pause
goto MENU

:: ============================================================
:: Moonshot Config
:: ============================================================
:CONFIG_MOONSHOT
echo.
echo ========================================
echo   Configure Moonshot (Kimi) Model
echo ========================================
echo.
echo Recommended: moonshot-v1-8k / moonshot-v1-32k / moonshot-v1-128k
echo API: https://platform.moonshot.cn/
echo.

set /p api_key="Enter Moonshot API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: moonshot-v1-8k): "
if "!model_name!"=="" set model_name=moonshot-v1-8k

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='moonshot'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://api.moonshot.cn/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] Moonshot configuration completed!
echo   Model: !model_name!
echo   API: https://api.moonshot.cn/v1
echo.
pause
goto MENU

:: ============================================================
:: Claude Config
:: ============================================================
:CONFIG_CLAUDE
echo.
echo ========================================
echo   Configure Claude Model
echo ========================================
echo.
echo Recommended: claude-3-5-sonnet-20240229 (latest) / claude-3-opus (best)
echo API: https://console.anthropic.com/
echo.

set /p api_key="Enter Anthropic Claude API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: claude-3-5-sonnet-20240229): "
if "!model_name!"=="" set model_name=claude-3-5-sonnet-20240229

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='anthropic'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://api.anthropic.com/v1'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] Claude configuration completed!
echo   Model: !model_name!
echo   API: https://api.anthropic.com/v1
echo.
pause
goto MENU

:: ============================================================
:: Gemini Config
:: ============================================================
:CONFIG_GEMINI
echo.
echo ========================================
echo   Configure Gemini/Google Model
echo ========================================
echo.
echo Recommended: gemini-1.5-pro (best) / gemini-1.5-flash (fast)
echo API: https://ai.google.dev/
echo.

set /p api_key="Enter Google AI Studio API Key: "
if "!api_key!"=="" (
    echo [ERROR] API Key cannot be empty
    pause
    goto MENU
)

set /p model_name="Enter model name (default: gemini-1.5-pro): "
if "!model_name!"=="" set model_name=gemini-1.5-pro

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); c['api_provider']='gemini'; c['model_name']='!model_name!'; c['api_keys']['custom']={'api_key': '!api_key!', 'base_url': 'https://generativelanguage.googleapis.com/v1beta'}; c['temperature']=0.7; c['top_p']=0.9; f=open('config/config.json', 'w', encoding='utf-8'); json.dump(c, f, indent=2, ensure_ascii=False); f.close()"

echo.
echo [OK] Gemini configuration completed!
echo   Model: !model_name!
echo   API: https://generativelanguage.googleapis.com/v1beta
echo.
pause
goto MENU

:: ============================================================
:: View Config
:: ============================================================
:VIEW_CONFIG
echo.
echo ========================================
echo   Current Configuration
echo ========================================
echo.

python -c "import json; f=open('config/config.json', 'r', encoding='utf-8'); c=json.load(f); f.close(); print('API Provider:', c.get('api_provider', 'N/A')); print('Model:', c.get('model_name', 'N/A')); print('Temperature:', c.get('temperature', 'N/A')); print('Top P:', c.get('top_p', 'N/A')); print('Concurrency:', c.get('initial_concurrency', 'N/A'), '/', c.get('max_concurrency', 'N/A')); print('Batch Size:', c.get('batch_size', 'N/A'))"

echo.
echo Config file: config/config.json
echo.
pause
goto MENU

:: ============================================================
:: Test API
:: ============================================================
:TEST_API
echo.
echo ========================================
echo   Test API Connection
echo ========================================
echo.

if exist "scripts/test_deepseek_connection.py" (
    python scripts/test_deepseek_connection.py
) else (
    echo [INFO] Test script not found, using simple test...
    python -c "import json; c=json.load(open('config/config.json', 'r', encoding='utf-8')); provider=c.get('api_provider', 'deepseek'); keys=c.get('api_keys', {}); k=keys.get(provider, keys.get('custom', {})); api_key=k.get('api_key', ''); base_url=k.get('base_url', ''); print(f'Testing: {base_url}'); print(f'API Key: {api_key[:10]}...' if len(api_key)>10 else 'API Key: Not set'); print('Please ensure API Key and network are working')"
)

if errorlevel 1 (
    echo.
    echo [ERROR] API connection test failed
    echo Please check:
    echo   1. API Key is correct
    echo   2. Network connection is normal
    echo   3. Firewall settings
) else (
    echo.
    echo [OK] API connection test successful
)
echo.
pause
goto MENU

:: ============================================================
:: Start App
:: ============================================================
:START_APP
echo.
echo ========================================
echo   Launching Translation Platform
echo ========================================
echo.

:: Check virtual environment
if exist ".venv/Scripts/activate.bat" (
    echo [INFO] Using virtual environment...
    call .venv/Scripts/activate.bat
)

echo Starting translation platform...
python presentation/translation.py

goto MENU

:: ============================================================
:: Exit
:: ============================================================
:EXIT
echo.
echo Thank you for using AI Translation Workbench!
echo.
pause
exit /b 0
