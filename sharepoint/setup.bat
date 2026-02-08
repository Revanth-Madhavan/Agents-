@echo off
echo Setting up environment...

:: Check if python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Ask for keys if .env doesn't exist
if not exist .env (
    echo.
    echo Please configure your .env file with SharePoint and OpenAI credentials.
    copy .env.example .env
    notepad .env
)

echo.
echo environment setup complete.
echo To run the Agent UI: streamlit run app.py
echo To run the CLI Agent: python agent.py
pause
