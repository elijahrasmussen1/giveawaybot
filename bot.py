"""
Discord Giveaway Bot - Python Implementation
A Discord bot for giveaways, game nights, and guess the number game.
"""

import os
import discord
from discord.ext import commands
import json

# -----------------------------
# CONFIGURATION
# -----------------------------
# Load configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

PREFIX = config.get('prefix', '&')
GUESS_CHANNEL_ID = int(config.get('guessChannelId'))

# -----------------------------
# BOT SETUP
# -----------------------------
# Configure intents - only request what we need
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content and commands

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Store the target number for the guess game
target_number = None

# -----------------------------
# EVENTS
# -----------------------------
@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready!')
    print('------')

@bot.event
async def on_message(message):
    """Event handler for all messages."""
    # Ignore messages from bots
    if message.author.bot:
        return
    
    # Process commands first
    await bot.process_commands(message)
    
    # Check for number guesses in the designated channel
    global target_number
    if message.channel.id == GUESS_CHANNEL_ID and target_number is not None:
        # Check if message is a number
        try:
            guess = int(message.content.strip())
            
            # Check if the guess matches the target number
            if guess == target_number:
                embed = discord.Embed(
                    title="🎉 WINNER! 🎉",
                    description=f"{message.author.mention} guessed the number! Ping an owner to obtain your prize!",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Congratulations!")
                embed.timestamp = discord.utils.utcnow()
                
                await message.channel.send(embed=embed)
                
                # Reset the target number after someone wins
                target_number = None
        except ValueError:
            # Not a valid number, ignore
            pass

# -----------------------------
# COMMANDS
# -----------------------------
@bot.command(name='setnumber')
@commands.has_permissions(administrator=True)
async def setnumber(ctx, number: int = None):
    """
    Sets the target number for the guess the number game (Admin only).
    
    Usage: &setnumber <number>
    """
    global target_number
    
    # Check if a number was provided
    if number is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}setnumber <number>",
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Set the target number
    target_number = number
    
    # Send confirmation to admin
    confirm_embed = discord.Embed(
        title="Number Set!",
        description=f"Target number has been set to: ||{number}||",
        color=discord.Color.green()
    )
    confirm_embed.timestamp = discord.utils.utcnow()
    await ctx.reply(embed=confirm_embed)
    
    # Send activation message to the guess channel
    try:
        guess_channel = bot.get_channel(GUESS_CHANNEL_ID)
        if guess_channel is None:
            guess_channel = await bot.fetch_channel(GUESS_CHANNEL_ID)
        
        if guess_channel:
            activation_embed = discord.Embed(
                title="🎮 GUESS THE NUMBER ACTIVATED! 🎮",
                description="YOU MAY GUESS UNTIL SOMEBODY GETS IT RIGHT!",
                color=discord.Color.blue()
            )
            activation_embed.set_footer(text="Good luck!")
            activation_embed.timestamp = discord.utils.utcnow()
            
            await guess_channel.send(embed=activation_embed)
        else:
            error_embed = discord.Embed(
                title="Error",
                description="Could not find the guess channel. Please check the channel ID in config.json",
                color=discord.Color.red()
            )
            error_embed.timestamp = discord.utils.utcnow()
            await ctx.reply(embed=error_embed)
    except Exception as e:
        print(f"Error sending to guess channel: {e}")
        error_embed = discord.Embed(
            title="Error",
            description=f"Could not send message to guess channel: {str(e)}",
            color=discord.Color.red()
        )
        error_embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@setnumber.error
async def setnumber_error(ctx, error):
    """Error handler for setnumber command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Invalid Number",
            description="Please provide a valid number!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in setnumber command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

# -----------------------------
# RUN BOT
# -----------------------------
# Get bot token from environment variable or use placeholder
bot_token = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
if bot_token == "YOUR_BOT_TOKEN_HERE":
    print("⚠️ WARNING: Using placeholder bot token. Set DISCORD_BOT_TOKEN environment variable.")
bot.run(bot_token)
