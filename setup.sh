#!/bin/bash
# Linux/Mac Setup Script for Discord Bot
# Run this script to automatically set up your bot

echo "================================================"
echo "Discord Bot - Automatic Setup for Linux/Mac"
echo "================================================"
echo ""

echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  Mac: brew install python3"
    exit 1
fi
python3 --version
echo ""

echo "Step 2: Installing dependencies..."
echo "This may take a minute..."
python3 -m pip install --upgrade pip
python3 -m pip install discord.py python-dotenv
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies"
    echo "Try: python3 -m pip install --user discord.py python-dotenv"
    echo "Or see INSTALL_TROUBLESHOOTING.md for more solutions"
    exit 1
fi
echo "Dependencies installed successfully!"
echo ""

echo "Step 3: Checking configuration files..."
if [ ! -f config.json ]; then
    echo "WARNING: config.json not found"
    echo "Creating default config.json..."
    echo '{"prefix": "&", "guessChannelId": "1456120708475125843"}' > config.json
    echo "Created config.json - EDIT THIS FILE with your channel ID!"
else
    echo "config.json found"
fi
echo ""

if [ ! -f .env ]; then
    echo "WARNING: .env file not found"
    echo "Creating .env template..."
    echo "DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE" > .env
    echo "Created .env - EDIT THIS FILE with your bot token!"
else
    echo ".env file found"
fi
echo ""

echo "Step 4: Running setup checker..."
python3 setup_check.py
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "IMPORTANT: Before running the bot, you MUST:"
echo "1. Edit .env file and add your Discord bot token"
echo "2. Edit config.json and add your channel ID"
echo ""
echo "After editing those files, run the bot with:"
echo "   python3 bot.py"
echo ""
echo "For help getting your bot token, see QUICKSTART.md"
echo "================================================"
