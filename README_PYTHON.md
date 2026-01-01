# Discord Giveaway Bot - Python Version

Python implementation of the Discord Giveaway Bot with the same features as the Node.js version.

## Quick Start

### Installation

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Bot**
   - Copy `.env.example` to `.env`
   - Add your Discord bot token to `.env`:
     ```
     DISCORD_BOT_TOKEN=your_bot_token_here
     ```

3. **Update Configuration**
   - Edit `config.json` to set your guess channel ID

4. **Run the Bot**
   ```bash
   python3 bot.py
   ```

## Features

- **&setnumber Command**: Admin-only command to set target number
- **Automatic Guess Detection**: Bot listens in designated channel
- **Winner Announcements**: Professional embed messages
- **Permission Checks**: Admin verification for commands
- **Error Handling**: Comprehensive error messages

## Commands

| Command | Permission | Description |
|---------|-----------|-------------|
| `&setnumber <number>` | Administrator | Sets the target number for the guess game |

## Requirements

- Python 3.8 or higher
- discord.py 2.3.2 or higher
- python-dotenv 1.0.0 or higher

## Bot Token Security

⚠️ **IMPORTANT**: Never share or hardcode your bot token!

- Always use environment variables to store your token
- The `.env` file is excluded from git via `.gitignore`
- If your token is compromised, regenerate it immediately in the Discord Developer Portal

## How to Get a Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select an existing one
3. Go to the "Bot" section
4. Click "Reset Token" to get your bot token
5. Copy the token and add it to your `.env` file
6. Enable "MESSAGE CONTENT INTENT" under Privileged Gateway Intents

## Usage Example

1. Admin runs: `&setnumber 42`
2. Bot announces in game channel: "GUESS THE NUMBER ACTIVATED!"
3. Players type numbers to guess
4. First correct guess wins and bot announces winner
5. Game resets automatically

## Deployment

### Local Development
```bash
python3 bot.py
```

### Using Screen (Linux/Unix)
```bash
screen -S giveawaybot
python3 bot.py
# Press Ctrl+A then D to detach
```

### Using systemd (Linux)
Create a service file: `/etc/systemd/system/giveawaybot.service`

```ini
[Unit]
Description=Discord Giveaway Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/giveawaybot
Environment="DISCORD_BOT_TOKEN=your_token_here"
ExecStart=/usr/bin/python3 /path/to/giveawaybot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable giveawaybot
sudo systemctl start giveawaybot
```

## Troubleshooting

### Bot doesn't respond to commands
- Check that MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- Verify the bot has permissions to read and send messages
- Check the prefix is correct (default: `&`)

### Channel not found error
- Verify the channel ID in `config.json` is correct
- Enable Developer Mode in Discord to copy channel IDs
- Ensure the bot has access to the channel

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher

## File Structure

```
bot.py              # Main Python bot file
requirements.txt    # Python dependencies
config.json         # Bot configuration
.env               # Environment variables (create from .env.example)
.env.example       # Environment variable template
```

## Comparison with Node.js Version

Both implementations provide the same features:
- Same command structure (`&setnumber`)
- Same embed messaging
- Same game logic
- Same configuration files

Choose based on your preference:
- **Python (bot.py)**: Simpler syntax, easier for Python developers
- **Node.js (index.js)**: Modular command structure, easier to extend

## License

ISC
