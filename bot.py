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
intents.members = True  # Required for member information in whois command

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

@bot.command(name='whois')
async def whois(ctx, member: discord.Member = None):
    """
    Shows detailed information about a server member.
    
    Usage: -whois @username or -whois user_id
    """
    # If no member specified, show info about the command author
    if member is None:
        member = ctx.author
    
    # Create embed with member information
    embed = discord.Embed(
        title=f"{member.name}",
        color=member.color if member.color != discord.Color.default() else discord.Color.blue()
    )
    
    # Set the member's avatar as thumbnail
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    
    # Add username field
    embed.add_field(name="Username", value=member.name, inline=False)
    
    # Add mention field
    embed.add_field(name="Mention", value=member.mention, inline=False)
    
    # Add joined server date
    if member.joined_at:
        joined_date = discord.utils.format_dt(member.joined_at, style='F')
        embed.add_field(name="Joined", value=joined_date, inline=False)
    
    # Add account creation date
    created_date = discord.utils.format_dt(member.created_at, style='F')
    embed.add_field(name="Registered", value=created_date, inline=False)
    
    # Add roles (excluding @everyone)
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    if roles:
        roles_text = f"[{len(roles)}] " + " ".join(roles)
        # Limit roles display to avoid embed size limits
        if len(roles_text) > 1024:
            roles_text = f"[{len(roles)}] Too many roles to display"
        embed.add_field(name="Roles", value=roles_text, inline=False)
    else:
        embed.add_field(name="Roles", value="[0] No roles", inline=False)
    
    # Set footer with member ID and timestamp
    embed.set_footer(text=f"ID: {member.id}")
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@whois.error
async def whois_error(ctx, error):
    """Error handler for whois command."""
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="Member Not Found",
            description="Could not find that member. Make sure you're using a valid @mention or user ID.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in whois command: {error}")
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
