@echo off
echo RAG-Powered Multi-Agent Q&A System
echo =================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8 or later.
    goto :end
)

REM Check if .env file exists
if not exist .env (
    if exist dotenv_file (
        echo Copying dotenv_file to .env
        copy dotenv_file .env
    ) else (
        echo WARNING: No .env file found.
        echo Creating default .env file. Please edit it with your Google Gemini API Key.
        echo GOOGLE_API_KEY=your_google_api_key_here> .env
    )
)

REM Display menu
:menu
echo.
echo Choose an option:
echo 1. Setup environment (install dependencies)
echo 2. Initialize vector store
echo 3. Run CLI interactive mode
echo 4. Run Web UI (Full Version with LLM)
echo 5. Run Web UI (Lightweight - No LLM, API quota friendly)
echo 6. Check environment setup
echo 7. Display disk usage
echo 8. Clean vector store (free up space)
echo 9. Exit
echo.

set /p choice=Enter your choice (1-9): 

if "%choice%"=="1" (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    echo.
    echo Setup complete. Please edit the .env file with your Google Gemini API key if you haven't already.
    goto :menu
)

if "%choice%"=="2" (
    echo Initializing vector store...
    python main.py --init
    goto :menu
)

if "%choice%"=="3" (
    echo Starting CLI interactive mode...
    python main.py --interactive
    goto :menu
)

if "%choice%"=="4" (
    echo Starting Web UI (Full Version)...
    start "RAG-QA Web UI" python run_webapp.py
    echo Web UI started in a new window. Close that window when done.
    goto :menu
)

if "%choice%"=="5" (
    echo Starting Web UI (Lightweight Version - No LLM)...
    start "RAG-QA Web UI Light" python run_webapp.py --lightweight
    echo Lightweight Web UI started in a new window. Close that window when done.
    goto :menu
)

if "%choice%"=="6" (
    echo Checking environment setup...
    python main.py --check-env
    pause
    goto :menu
)

if "%choice%"=="7" (
    echo Displaying disk usage information...
    python main.py --disk-usage
    pause
    goto :menu
)

if "%choice%"=="8" (
    echo Cleaning vector store to free up space...
    python main.py --clean-vector-store
    pause
    goto :menu
)

if "%choice%"=="9" (
    goto :end
)

echo Invalid choice. Please try again.
goto :menu

:end
echo.
echo Thank you for using the RAG-Powered Multi-Agent Q&A System!
pause 