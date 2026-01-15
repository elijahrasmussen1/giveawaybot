# QUICK START - Get Your Bot Online NOW!

Follow these steps exactly to get your bot running:

## Step 1: Install Python (if not already installed)

1. Download Python from https://www.python.org/downloads/
2. During installation, **CHECK** "Add Python to PATH"
3. Restart your computer after installation

## Step 2: Install Discord.py

Open Command Prompt (Windows) or Terminal (Mac/Linux) and run:

```bash
python -m pip install discord.py python-dotenv
```

If that doesn't work, try:
```bash
py -m pip install discord.py python-dotenv
```

## Step 3: Get Your Bot Token

1. Go to https://discord.com/developers/applications
2. Click "New Application" (or select existing one)
3. Go to "Bot" section in left sidebar
4. Click "Reset Token" and copy the token that appears
5. **IMPORTANT**: Enable these under "Privileged Gateway Intents":
   - ✅ **MESSAGE CONTENT INTENT** (required - bot cannot read messages without this!)
   - ✅ **SERVER MEMBERS INTENT** (required for -whois command)

## Step 4: Configure Your Bot

### Option A: Use Environment Variable (Recommended)

**Windows Command Prompt:**
```cmd
set DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
```

**Windows PowerShell:**
```powershell
$env:DISCORD_BOT_TOKEN="YOUR_TOKEN_HERE"
```

**Mac/Linux:**
```bash
export DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
```

### Option B: Create .env file

Create a file named `.env` in the same folder as bot.py:
```
DISCORD_BOT_TOKEN=YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with your actual bot token.

## Step 5: Update config.json

Edit `config.json` to set your channel ID:

1. Enable Developer Mode in Discord: User Settings → Advanced → Developer Mode
2. Right-click the channel where you want the game → Copy ID
3. Edit config.json:
```json
{
  "prefix": "&",
  "guessChannelId": "YOUR_CHANNEL_ID_HERE"
}
```

## Step 6: Invite Bot to Your Server

1. Go to https://discord.com/developers/applications
2. Select your application
3. Go to "OAuth2" → "URL Generator"
4. Select scopes: `bot`
5. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Read Message History
6. Copy the URL at the bottom and open it in browser
7. Select your server and authorize

## Step 7: Run the Bot

Open Command Prompt/Terminal in the folder with bot.py and run:

```bash
python bot.py
```

Or try:
```bash
py bot.py
```

Or:
```bash
python3 bot.py
```

## You Should See:

```
Logged in as YourBotName (123456789)
Bot is ready!
------
```

## Test Your Bot

In the Discord channel you configured:

1. Type: `&setnumber 42` (as an admin)
2. Bot should announce the game is activated
3. Type: `42` in the channel
4. Bot should announce you as the winner!

## Common Problems & Solutions

### "python is not recognized"
- Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe bot.py`

### "No module named 'discord'"
```bash
python -m pip install discord.py python-dotenv
```

### "Improper token has been passed"
- Check your token is correct
- Make sure DISCORD_BOT_TOKEN environment variable is set
- Regenerate token in Discord Developer Portal if needed

### "Privileged intent provided is not enabled"
- Go to Discord Developer Portal → Your App → Bot
- Enable **MESSAGE CONTENT INTENT** under Privileged Gateway Intents
- Click "Save Changes"
- **Important**: After enabling, kick and re-invite your bot to the server
- See FIX_INTENTS.md for detailed visual guide

### Bot doesn't respond to commands
- Make sure bot has permissions in the channel
- Check MESSAGE CONTENT INTENT is enabled
- Verify the prefix is `&`

### "Invalid channel ID" or channel not found
- Make sure you copied the channel ID correctly
- Enable Developer Mode in Discord to copy IDs
- Bot must have access to that channel

## Still Not Working?

Run this diagnostic script:

```python
import sys
print(f"Python version: {sys.version}")

try:
    import discord
    print(f"discord.py version: {discord.__version__}")
except ImportError:
    print("❌ discord.py is NOT installed")
    print("Run: python -m pip install discord.py")

import os
token = os.getenv("DISCORD_BOT_TOKEN")
if token:
    print(f"✅ Bot token is set (length: {len(token)})")
else:
    print("❌ Bot token is NOT set")
    print("Set it with: set DISCORD_BOT_TOKEN=your_token")
```

Save this as `check.py` and run: `python check.py`

## Need More Help?

1. Check INSTALL_TROUBLESHOOTING.md for detailed solutions
2. Check README_PYTHON.md for full documentation
3. Make sure you completed ALL steps above
