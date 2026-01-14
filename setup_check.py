"""
Setup Checker and Diagnostic Tool
Run this to check if your environment is ready for the Discord bot.
"""

import sys
import os

print("=" * 60)
print("Discord Bot Setup Checker")
print("=" * 60)
print()

# Check Python version
print("1. Checking Python version...")
python_version = sys.version_info
print(f"   Python {python_version.major}.{python_version.minor}.{python_version.micro}")
if python_version.major >= 3 and python_version.minor >= 8:
    print("   ✅ Python version is compatible (3.8+)")
else:
    print("   ❌ Python version too old. Need 3.8 or higher.")
    print("   Download from: https://www.python.org/downloads/")
print()

# Check discord.py
print("2. Checking discord.py installation...")
try:
    import discord
    print(f"   ✅ discord.py {discord.__version__} is installed")
except ImportError:
    print("   ❌ discord.py is NOT installed")
    print("   Fix: Run 'python -m pip install discord.py'")
print()

# Check python-dotenv
print("3. Checking python-dotenv installation...")
try:
    import dotenv
    print("   ✅ python-dotenv is installed")
except ImportError:
    print("   ⚠️  python-dotenv is NOT installed (optional)")
    print("   Fix: Run 'python -m pip install python-dotenv'")
print()

# Check bot token
print("4. Checking bot token...")
token = os.getenv("DISCORD_BOT_TOKEN")
if token:
    if len(token) > 50:
        print(f"   ✅ Bot token is set (length: {len(token)} characters)")
    else:
        print(f"   ⚠️  Bot token seems too short (length: {len(token)})")
        print("   Discord bot tokens are usually 70+ characters")
else:
    print("   ❌ Bot token is NOT set")
    print("   Fix: Set environment variable DISCORD_BOT_TOKEN")
    print("   Windows CMD: set DISCORD_BOT_TOKEN=your_token")
    print("   PowerShell: $env:DISCORD_BOT_TOKEN=\"your_token\"")
    print("   Or create a .env file with: DISCORD_BOT_TOKEN=your_token")
print()

# Check config.json
print("5. Checking config.json...")
try:
    import json
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    if 'prefix' in config:
        print(f"   ✅ Prefix is set to: {config['prefix']}")
    else:
        print("   ⚠️  Prefix not found in config.json")
    
    if 'guessChannelId' in config:
        channel_id = config['guessChannelId']
        print(f"   ✅ Channel ID is set to: {channel_id}")
        if len(str(channel_id)) < 17:
            print("   ⚠️  Channel ID seems too short. Make sure it's correct.")
    else:
        print("   ❌ guessChannelId not found in config.json")
        print("   Fix: Add your channel ID to config.json")
    
except FileNotFoundError:
    print("   ❌ config.json file NOT found")
    print("   Fix: Create config.json with:")
    print('   {"prefix": "&", "guessChannelId": "YOUR_CHANNEL_ID"}')
except json.JSONDecodeError:
    print("   ❌ config.json has invalid JSON format")
    print("   Fix: Check for syntax errors in config.json")
print()

# Check bot.py
print("6. Checking bot.py...")
if os.path.exists('bot.py'):
    print("   ✅ bot.py file exists")
    file_size = os.path.getsize('bot.py')
    print(f"   File size: {file_size} bytes")
else:
    print("   ❌ bot.py file NOT found")
    print("   Make sure you're in the correct directory")
print()

print("=" * 60)
print("Summary")
print("=" * 60)

# Count issues
issues = []
if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
    issues.append("Python version too old")

try:
    import discord
except ImportError:
    issues.append("discord.py not installed")

if not token:
    issues.append("Bot token not set")

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    if 'guessChannelId' not in config:
        issues.append("Channel ID not configured")
except:
    issues.append("config.json missing or invalid")

if not os.path.exists('bot.py'):
    issues.append("bot.py not found")

if len(issues) == 0:
    print("✅ All checks passed! You're ready to run the bot.")
    print("\nRun your bot with:")
    print("   python bot.py")
else:
    print(f"❌ Found {len(issues)} issue(s):")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print("\nFix these issues and run this script again.")

print()
print("For detailed help, see QUICKSTART.md")
print("=" * 60)
