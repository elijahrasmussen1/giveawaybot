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
- **-t Command (Timeout)**: Timeout members with flexible duration formats: `5m` (minutes), `5h` (hours), `5d` (days) - prevents them from sending messages, reactions, or speaking (Admin only)
- **-ut Command (Untimeout)**: Remove timeout from members early (Admin only)
- **Case Number System**: Each warning gets a unique case ID for tracking
- **-viewcase Command**: View detailed information about specific warning cases (Admin only)
- **Automatic Warning Tracking**: Persistent storage of all warnings with case numbers
- **Auto-ban at 15 Warnings**: Automatic ban when a user reaches 15 warnings
- **Modlog Channel**: All moderation actions (warnings, timeouts, bans) logged to designated channel with case IDs
- **-warnings Command**: View a member's warning history with case numbers (Admin only)
- **-lock Command**: Lock channels to prevent raids - only bypass role can send messages (Admin only)
- **-unlock Command**: Restore normal channel permissions (Admin only)

### Member Information
- **-whois Command**: Display detailed member information including join date, roles, and account creation date
- **-m Command (Message Statistics)**: Track and display message counts for any user
  - Shows messages sent today, this week, this month, and all-time
  - Professional embed with user's profile picture
  - Perfect for giveaway eligibility and activity tracking
  - Automatically tracks all messages in real-time

### Invite Tracking System
- **-i Command (Check Invites)**: Display user's invite statistics
  - Shows total invites with breakdown: regular, fake, left, and added
  - Professional embed with user's profile picture
  - Works seamlessly with giveaway requirements
  - Tracks invites created by users using Discord's native API
- **-addinvites Command**: Add bonus invites to users (Admin only)
  - Bonus invites count toward giveaway requirements
  - Example: `-addinvites @user 50`
- **-resetinvites Command**: Reset invite data (Admin only)
  - Reset specific user: `-resetinvites @user`
  - Reset all users: `-resetinvites all`
- **-invlb Command (Invite Leaderboard)**: Display top members by invite count
  - Shows top 10 members ranked by total invites
  - Professional embed with clean formatting
  - Updates in real-time

### Guess the Number Game
- **-setnumber Command**: Admins can set a target number for players to guess
- **Automatic Winner Detection**: Bot listens for correct guesses and announces winners
- **Professional Embeds**: All messages use Discord embeds for a polished appearance
- **Designated Channel**: Game runs in a specific channel to avoid spam

### Giveaway System
- **-gcreate Command**: Create giveaways with interactive setup (Admin only)
  - Set duration (minutes, hours, or days)
  - Specify number of winners
  - Define prize
  - Set invite requirements (uses native Discord invite tracking)
  - Set message requirements (today, weekly, or monthly)
  - Optional giveaway image
- **Interactive Button Entry**: Modern button-based entry system (Python version)
  - Click "🎉 Enter Giveaway" button to participate
  - Automatic requirement verification on click
  - Real-time entry counter updates
  - Ephemeral feedback messages
- **Role-Based Entry System**:
  - Member role: 1 entry
  - Level 5 role: 2 entries
  - Shop Owner role: 3 entries
  - Server Booster role: 4 entries + bypasses all requirements
- **Invite Integration**: Uses same invite tracking as `-i` command for accurate requirement verification
- **Automatic Validation**: Users must meet invite and message requirements to enter
- **Dynamic Re-verification**: Requirements checked on each button click, allowing users to enter after meeting requirements
- **-greroll Command**: Reroll giveaway to select new winners (Admin only)
- **Automatic Winner Selection**: Picks winners based on weighted entries when giveaway ends
- **Automated Winner Tickets**: Creates private ticket channels for winners with congratulations message
- **Requirements Enforcement**: Users who don't meet criteria are automatically removed from entries with appropriate error messages

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
| `-setnumber <number>` | Sets the target number for the guess game | Administrator |
| `-m @username` | Shows message count statistics (today, this week, this month, all time) | Everyone |
| `-whois @member` | Display detailed member information | Everyone |
| `-warn @member <reason>` | Warn a member for rule violations | Administrator |
| `-warnings @member` | View a member's warning history | Administrator |
| `-viewcase <case_id>` | View detailed information about a specific case | Administrator |
| `-t @member <duration> <reason>` | Timeout a member (e.g., `5m`, `5h`, `5d`) | Administrator |
| `-ut @member [reason]` | Remove timeout from a member | Administrator |
| `-lock [role]` | Lock channel to prevent raids | Administrator |
| `-unlock` | Restore normal channel permissions | Administrator |
| `-gcreate` | Create a new giveaway with interactive setup | Administrator |
| `-greroll <giveaway_id>` | Reroll a giveaway to pick new winners | Administrator |

## How to Create a Giveaway

1. An administrator runs `-gcreate`
2. Answer the interactive questions:
   - **Duration**: Enter time like "10 minutes", "5 hours", or "2 days"
   - **Number of Winners**: Enter how many winners (e.g., 1)
   - **Prize**: Enter what the prize is (e.g., "Discord Nitro")
   - **Invite Requirement**: Enter minimum invites needed (or 0 for none)
   - **Message Requirement**: Enter minimum messages and period (e.g., "250 weekly" or "0" for none)
3. The bot creates the giveaway and posts it with a 🎉 reaction
4. Users react with 🎉 to enter
5. Bot automatically validates requirements and entry eligibility
6. When time expires, winners are automatically selected based on weighted entries
7. Use `-greroll <giveaway_id>` to pick new winners if needed

**Entry System:**
- Member role: 1 entry
- Level 5 role: 2 entries  
- Shop Owner role: 3 entries
- Server Booster role: 4 entries + bypasses all requirements

## How to Play Guess the Number

1. An administrator runs `&setnumber 42` (or any number)
2. The bot announces in the game channel: "GUESS THE NUMBER ACTIVATED!"
3. Players type their guesses as regular messages (e.g., "42")
4. The first person to guess correctly wins!
5. Winner should ping an owner to claim their prize

## Configuration

Edit `config.json` to customize:
- `prefix`: Command prefix (default: `-`)
- `guessChannelId`: Channel ID where the guess game runs
- `modlogChannelId`: Channel ID for moderation logs
- `bypassRoleId`: Role ID that can bypass channel locks
- `giveawayChannelId`: Channel ID where giveaway notifications are sent
- `inviteChannelId`: Channel ID for invite tracking
- `guildId`: Your Discord server ID
- `roles`: Role IDs for giveaway entry system
  - `member`: Member role ID (1 entry)
  - `level5`: Level 5 role ID (2 entries)
  - `shopOwner`: Shop Owner role ID (3 entries)
  - `serverBooster`: Server Booster role ID (4 entries + bypass)
- `inviteTrackerBotId`: Invite Tracker bot ID for integration

## Required Bot Permissions

For the bot to function properly, it needs the following Discord permissions:

**Essential Permissions:**
- `Read Messages/View Channels` - View channels and their content
- `Send Messages` - Send responses and embeds
- `Embed Links` - Send embed messages
- `Manage Messages` - Delete messages for cleanup and moderation
- `Read Message History` - Read past messages
- `Add Reactions` - Add reactions to messages
- `Manage Roles` - For moderation features (timeout, role checks)
- `Manage Channels` - For lock/unlock commands
- `Ban Members` - For auto-ban at 15 warnings
- `Moderate Members` - For timeout command
- `Manage Guild` - **Required for invite tracking** - allows bot to view server invites

**Required Intents** (configure in Discord Developer Portal):
- `Server Members Intent` - Required for member information
- `Message Content Intent` - Required for reading commands
- `Invites Intent` - **Required for giveaway invite tracking**

**Note on Invite Tracking:** The bot tracks invites by fetching Discord's native invite data, compatible with Invite Tracker bot (ID: 720351927581278219). The bot needs `Manage Guild` permission to view invite usage counts.

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

