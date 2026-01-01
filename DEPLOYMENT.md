# Deployment Guide for Giveaway Bot

This guide will help you deploy and run the Discord Giveaway Bot.

## Prerequisites

- Node.js (version 16.9.0 or higher)
- A Discord account
- A Discord server where you have administrative permissions

## Step 1: Create a Discord Bot

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name (e.g., "Giveaway Bot")
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot" and confirm
5. Under the bot's username, click "Reset Token" and copy your bot token (keep this secret!)
6. Enable the following Privileged Gateway Intents:
   - MESSAGE CONTENT INTENT (required for reading message content)

## Step 2: Invite the Bot to Your Server

1. In the Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select the following scopes:
   - `bot`
3. Select the following bot permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Read Message History
4. Copy the generated URL and paste it into your browser
5. Select your server and authorize the bot

## Step 3: Configure the Bot

1. Download or clone this repository to your computer
2. Open a terminal/command prompt in the bot's directory
3. Install dependencies:
   ```bash
   npm install
   ```

4. Create a `.env` file in the root directory (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file and add your bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

6. Edit `config.json` to set your guess channel ID:
   - To get a channel ID: Enable Developer Mode in Discord (Settings > Advanced > Developer Mode)
   - Right-click on the channel and select "Copy ID"
   - Replace the channel ID in `config.json`:
   ```json
   {
     "prefix": "&",
     "guessChannelId": "YOUR_CHANNEL_ID_HERE"
   }
   ```

## Step 4: Run the Bot

### Running Locally

To run the bot on your local machine:

```bash
npm start
```

The bot should now be online! You should see a message like:
```
Logged in as YourBot#1234!
Bot is ready! Using prefix: &
```

### Keeping the Bot Running

For local development, you can use `pm2` or `nodemon`:

#### Using PM2 (Recommended for production)
```bash
npm install -g pm2
pm2 start index.js --name "giveawaybot"
pm2 save
pm2 startup
```

#### Using nodemon (for development)
```bash
npm install -g nodemon
nodemon index.js
```

## Step 5: Hosting Options

### Option 1: Heroku (Free Tier Available)

1. Create a Heroku account at [heroku.com](https://www.heroku.com/)
2. Install the Heroku CLI
3. Login to Heroku:
   ```bash
   heroku login
   ```
4. Create a new Heroku app:
   ```bash
   heroku create your-bot-name
   ```
5. Add your bot token as an environment variable:
   ```bash
   heroku config:set DISCORD_TOKEN=your_bot_token_here
   ```
6. Create a `Procfile` in the root directory:
   ```
   worker: node index.js
   ```
7. Commit and push to Heroku:
   ```bash
   git add .
   git commit -m "Deploy bot"
   git push heroku main
   ```
8. Scale the worker:
   ```bash
   heroku ps:scale worker=1
   ```

### Option 2: Railway.app

1. Go to [railway.app](https://railway.app/)
2. Create a new project from GitHub repository
3. Add your `DISCORD_TOKEN` as an environment variable in the Railway dashboard
4. Deploy!

### Option 3: VPS (DigitalOcean, AWS, etc.)

1. Set up a VPS with Ubuntu/Debian
2. Install Node.js:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```
3. Clone your repository
4. Install dependencies: `npm install`
5. Create `.env` file with your token
6. Use PM2 to keep the bot running:
   ```bash
   npm install -g pm2
   pm2 start index.js --name "giveawaybot"
   pm2 startup
   pm2 save
   ```

### Option 4: Replit

1. Go to [replit.com](https://replit.com/)
2. Create a new Node.js Repl
3. Upload your bot files
4. Add your `DISCORD_TOKEN` to the Secrets (environment variables)
5. Click "Run"

## Bot Usage

### Commands

- `&setnumber <number>` - (Admin only) Sets the target number for the guess game

### How It Works

1. An administrator uses `&setnumber` to set a secret number
2. The bot announces in the designated channel that the game is active
3. Users guess by typing numbers in the channel
4. When someone guesses correctly, the bot announces the winner
5. The winner should ping an owner to claim their prize

## Troubleshooting

### Bot is offline
- Check that your bot token is correct in the `.env` file
- Make sure the bot process is running
- Check the console for error messages

### Bot doesn't respond to commands
- Make sure you enabled "MESSAGE CONTENT INTENT" in the Discord Developer Portal
- Check that the prefix is correct (default is `&`)
- Verify the bot has permission to read and send messages in the channel

### Guess channel not working
- Verify the channel ID is correct in `config.json`
- Make sure the bot has access to that channel

## Security Notes

- **Never** commit your `.env` file or share your bot token
- Keep your bot token secret - if it's leaked, reset it in the Developer Portal
- The `.gitignore` file is configured to exclude sensitive files

## Support

For issues or questions, please open an issue on the GitHub repository.
