# Giveaway Bot

A Discord bot for community engagement and moderation featuring a "guess the number" game, member information lookups, and professional embed messaging.

**Available in two implementations:**
- 🐍 **Python** (`bot.py`) - Simple, single-file implementation
- 📦 **Node.js** (`index.js`) - Modular architecture with command handler

Both implementations provide identical features. Choose based on your preference!

## 🚀 NEED HELP GETTING STARTED?

**→ See [QUICKSTART.md](QUICKSTART.md) for step-by-step instructions to get your bot online NOW!**

**→ Run the automated setup script:**
- Windows: Double-click `setup.bat`
- Linux/Mac: Run `./setup.sh`

**→ Check your setup:** Run `python setup_check.py` to diagnose issues

## Features

### Moderation System
- **-warn Command**: Warn members for rule violations (Admin only)
- **-t Command (Timeout)**: Timeout members to prevent them from sending messages, reactions, or speaking (Admin only)
- **Case Number System**: Each warning gets a unique case ID for tracking
- **-viewcase Command**: View detailed information about specific warning cases (Admin only)
- **Automatic Warning Tracking**: Persistent storage of all warnings with case numbers
- **Auto-ban at 15 Warnings**: Automatic ban when a user reaches 15 warnings
- **Modlog Channel**: All moderation actions logged to designated channel with case IDs
- **-warnings Command**: View a member's warning history with case numbers (Admin only)
- **-lock Command**: Lock channels to prevent raids - only bypass role can send messages (Admin only)
- **-unlock Command**: Restore normal channel permissions (Admin only)

### Member Information
- **-whois Command**: Display detailed member information including join date, roles, and account creation date

### Guess the Number Game
- **-setnumber Command**: Admins can set a target number for players to guess
- **Automatic Winner Detection**: Bot listens for correct guesses and announces winners
- **Professional Embeds**: All messages use Discord embeds for a polished appearance
- **Designated Channel**: Game runs in a specific channel to avoid spam

### Bot Capabilities
- Prefix-based commands (default: `-`)
- Modular command handler for easy expansion
- Permission checks for admin commands
- Professional embed messages throughout

## Quick Start

### Python Version (Recommended for Simplicity)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the Bot**
   - Copy `.env.example` to `.env`
   - Add your Discord bot token to `.env` as `DISCORD_BOT_TOKEN`
   - Update the channel ID in `config.json`

3. **Run the Bot**
   ```bash
   python3 bot.py
   ```

See [README_PYTHON.md](README_PYTHON.md) for detailed Python setup.

### Node.js Version (Modular Architecture)

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure the Bot**
   - Copy `.env.example` to `.env`
   - Add your Discord bot token to `.env` as `DISCORD_TOKEN`
   - Update the channel ID in `config.json`

3. **Run the Bot**
   ```bash
   npm start
   ```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Node.js setup and hosting options.

## Commands

| Command | Description | Permission |
|---------|-------------|------------|
| `&setnumber <number>` | Sets the target number for the guess game | Administrator |

## How to Play Guess the Number

1. An administrator runs `&setnumber 42` (or any number)
2. The bot announces in the game channel: "GUESS THE NUMBER ACTIVATED!"
3. Players type their guesses as regular messages (e.g., "42")
4. The first person to guess correctly wins!
5. Winner should ping an owner to claim their prize

## Configuration

Edit `config.json` to customize:
- `prefix`: Command prefix (default: `&`)
- `guessChannelId`: Channel ID where the guess game runs

## Deployment

For detailed deployment instructions including hosting options (Heroku, Railway, VPS, etc.), see [DEPLOYMENT.md](DEPLOYMENT.md).

## Project Structure

```
giveawaybot/
├── commands/           # Command modules
│   └── setnumber.js   # Set number command
├── config.json        # Bot configuration
├── index.js           # Main bot file
├── package.json       # Dependencies
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore file
└── DEPLOYMENT.md      # Detailed deployment guide
```

## Future Features

This bot is designed to be modular and can be easily extended with:
- Giveaway commands
- Game night scheduling
- Additional mini-games
- Leaderboards
- Prize management

## Security

- Bot token is stored in `.env` file (not committed to git)
- Admin commands require Administrator permission
- Input validation on all commands

## Requirements

- Node.js 16.9.0 or higher
- Discord.js v14
- A Discord bot token

## License

ISC

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

