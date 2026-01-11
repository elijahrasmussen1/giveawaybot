@echo off
REM Windows Setup Script for Discord Bot
REM Run this script to automatically set up your bot

echo ================================================
echo Discord Bot - Automatic Setup for Windows
echo ================================================
echo.

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
python --version
echo.

echo Step 2: Installing dependencies...
echo This may take a minute...
python -m pip install --upgrade pip
python -m pip install discord.py python-dotenv
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running as Administrator or see INSTALL_TROUBLESHOOTING.md
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo Step 3: Checking configuration files...
if not exist config.json (
    echo WARNING: config.json not found
    echo Creating default config.json...
    echo {"prefix": "&", "guessChannelId": "1456120708475125843"} > config.json
    echo Created config.json - EDIT THIS FILE with your channel ID!
) else (
    echo config.json found
)
echo.

if not exist .env (
    echo WARNING: .env file not found
    echo Creating .env template...
    echo DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE > .env
    echo Created .env - EDIT THIS FILE with your bot token!
) else (
    echo .env file found
)
echo.

echo Step 4: Running setup checker...
python setup_check.py
echo.

echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo IMPORTANT: Before running the bot, you MUST:
echo 1. Edit .env file and add your Discord bot token
echo 2. Edit config.json and add your channel ID
echo.
echo After editing those files, run the bot with:
echo    python bot.py
echo.
echo For help getting your bot token, see QUICKSTART.md
echo ================================================
pause
