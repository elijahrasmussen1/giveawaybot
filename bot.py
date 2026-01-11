"""
Discord Giveaway Bot - Python Implementation
A Discord bot for giveaways, game nights, and guess the number game.
"""

import os
import discord
from discord.ext import commands
import json
from datetime import datetime, timedelta, timezone
import asyncio
import re

# -----------------------------
# CONFIGURATION
# -----------------------------
# Load configuration from config.json
with open('config.json', 'r') as f:
    config = json.load(f)

PREFIX = config.get('prefix', '&')
GUESS_CHANNEL_ID = int(config.get('guessChannelId'))
MODLOG_CHANNEL_ID = int(config.get('modlogChannelId'))
BYPASS_ROLE_ID = int(config.get('bypassRoleId'))

# Warnings database file
WARNINGS_FILE = 'warnings.json'

# Load or initialize warnings data
def load_warnings():
    """Load warnings from JSON file."""
    try:
        with open(WARNINGS_FILE, 'r') as f:
            data = json.load(f)
            # Ensure data has the correct structure
            if not isinstance(data, dict):
                return {"users": {}, "case_counter": 0}
            if "users" not in data:
                # Migrate old format to new format
                return {"users": data, "case_counter": 0}
            return data
    except FileNotFoundError:
        return {"users": {}, "case_counter": 0}

def save_warnings(warnings_data):
    """Save warnings to JSON file."""
    with open(WARNINGS_FILE, 'w') as f:
        json.dump(warnings_data, f, indent=2)

warnings = load_warnings()
# Ensure warnings has the correct structure
if "users" not in warnings:
    warnings = {"users": warnings, "case_counter": 0}
if "case_counter" not in warnings:
    warnings["case_counter"] = 0

# Message tracking database file
MESSAGES_FILE = 'messages.json'

# Load or initialize message tracking data
def load_messages():
    """Load message tracking data from JSON file."""
    try:
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_messages(messages_data):
    """Save message tracking data to JSON file."""
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages_data, f, indent=2)

messages_data = load_messages()

# Giveaway database file
GIVEAWAYS_FILE = 'giveaways.json'

# Load or initialize giveaway data
def load_giveaways():
    """Load giveaway data from JSON file."""
    try:
        with open(GIVEAWAYS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_giveaways(giveaways_data):
    """Save giveaway data to JSON file."""
    with open(GIVEAWAYS_FILE, 'w') as f:
        json.dump(giveaways_data, f, indent=2)

giveaways_data = load_giveaways()

# Invite tracking database file
INVITES_FILE = 'invites.json'

# Load or initialize invite tracking data
def load_invites():
    """Load invite tracking data from JSON file."""
    try:
        with open(INVITES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_invites(invites_data):
    """Save invite tracking data to JSON file."""
    with open(INVITES_FILE, 'w') as f:
        json.dump(invites_data, f, indent=2)

invites_data = load_invites()

# Giveaway configuration from config.json
GIVEAWAY_CHANNEL_ID = int(config.get('giveawayChannelId', 0))
INVITE_CHANNEL_ID = int(config.get('inviteChannelId', 0))
GUILD_ID = int(config.get('guildId', 0))
TICKET_CATEGORY_ID = int(config.get('ticketCategoryId', 0))
OWNER_ROLE_ID = int(config.get('ownerRoleId', 0))
ROLE_IDS = config.get('roles', {})
MEMBER_ROLE_ID = int(ROLE_IDS.get('member', 0))
LEVEL5_ROLE_ID = int(ROLE_IDS.get('level5', 0))
SHOP_OWNER_ROLE_ID = int(ROLE_IDS.get('shopOwner', 0))
SERVER_BOOSTER_ROLE_ID = int(ROLE_IDS.get('serverBooster', 0))

# -----------------------------
# BOT SETUP
# -----------------------------
# Configure intents - only request what we need
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content and commands
intents.members = True  # Required for member information in whois command
intents.reactions = True  # Required for giveaway reactions
intents.invites = True  # Required for tracking user invites

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
    
    # Track message for statistics
    user_id = str(message.author.id)
    timestamp = datetime.utcnow().isoformat()
    
    if user_id not in messages_data:
        messages_data[user_id] = []
    
    messages_data[user_id].append(timestamp)
    save_messages(messages_data)
    
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

@bot.command(name='warn')
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    """
    Warns a member and logs it to the modlog channel.
    
    Usage: -warn @username reason
           -warn user_id reason
    """
    global warnings
    
    # Check if a member was provided
    if member is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}warn @member [reason]\n\nExample: {PREFIX}warn @user Spamming in chat",
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Cannot warn bots
    if member.bot:
        embed = discord.Embed(
            title="Cannot Warn Bot",
            description="You cannot warn bot users.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Cannot warn yourself
    if member.id == ctx.author.id:
        embed = discord.Embed(
            title="Cannot Warn Yourself",
            description="You cannot warn yourself.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Get member ID as string for storage
    member_id = str(member.id)
    
    # Initialize member warnings if not exists
    if member_id not in warnings["users"]:
        warnings["users"][member_id] = []
    
    # Increment case counter
    warnings["case_counter"] += 1
    case_id = warnings["case_counter"]
    
    # Add warning
    warning_data = {
        "case_id": case_id,
        "moderator": str(ctx.author.id),
        "moderator_name": str(ctx.author),
        "member_id": member_id,
        "member_name": str(member),
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    warnings["users"][member_id].append(warning_data)
    
    # Save warnings to file
    save_warnings(warnings)
    
    # Get warning count
    warning_count = len(warnings["users"][member_id])
    
    # Send confirmation to moderator
    confirm_embed = discord.Embed(
        title="⚠️ Member Warned",
        description=f"{member.mention} has been warned.\n**Reason:** {reason}",
        color=discord.Color.orange()
    )
    confirm_embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
    confirm_embed.add_field(name="Total Warnings", value=f"{warning_count}/15", inline=True)
    confirm_embed.set_footer(text=f"Warned by {ctx.author}")
    confirm_embed.timestamp = discord.utils.utcnow()
    await ctx.reply(embed=confirm_embed)
    
    # Send DM to the warned member
    try:
        dm_embed = discord.Embed(
            title="⚠️ You Have Been Warned",
            description=f"You have been warned in **{ctx.guild.name}**.",
            color=discord.Color.orange()
        )
        dm_embed.add_field(name="Reason", value=reason, inline=False)
        dm_embed.add_field(name="Total Warnings", value=f"{warning_count}/15", inline=True)
        dm_embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
        dm_embed.add_field(
            name="⚠️ Important",
            value=f"If you reach 15 warnings, you will be automatically banned from {ctx.guild.name}.",
            inline=False
        )
        dm_embed.set_footer(text=f"Warned by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        dm_embed.timestamp = discord.utils.utcnow()
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        # Member has DMs disabled, that's okay
        pass
    except Exception as e:
        print(f"Error sending DM to warned member: {e}")
    
    # Send modlog
    try:
        modlog_channel = bot.get_channel(MODLOG_CHANNEL_ID)
        if modlog_channel is None:
            modlog_channel = await bot.fetch_channel(MODLOG_CHANNEL_ID)
        
        if modlog_channel:
            modlog_embed = discord.Embed(
                title="🚨 Warning Issued",
                color=discord.Color.orange()
            )
            modlog_embed.add_field(name="Case ID", value=f"#{case_id}", inline=True)
            modlog_embed.add_field(name="Warnings", value=f"{warning_count}/15", inline=True)
            modlog_embed.add_field(name="Member", value=f"{member.mention} ({member})", inline=False)
            modlog_embed.add_field(name="Member ID", value=member.id, inline=True)
            modlog_embed.add_field(name="Moderator", value=f"{ctx.author.mention} ({ctx.author})", inline=False)
            modlog_embed.add_field(name="Reason", value=reason, inline=False)
            modlog_embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            modlog_embed.set_footer(text=f"Case #{case_id}")
            modlog_embed.timestamp = discord.utils.utcnow()
            await modlog_channel.send(embed=modlog_embed)
    except Exception as e:
        print(f"Error sending to modlog channel: {e}")
    
    # Check if member should be banned (15 warnings)
    if warning_count >= 15:
        try:
            # Send DM to user before banning
            try:
                dm_embed = discord.Embed(
                    title="🔨 Banned from Server",
                    description=f"You have been banned from **{ctx.guild.name}** for accumulating 15 warnings.",
                    color=discord.Color.red()
                )
                dm_embed.add_field(name="Total Warnings", value="15/15", inline=False)
                dm_embed.add_field(name="Latest Reason", value=reason, inline=False)
                dm_embed.timestamp = discord.utils.utcnow()
                await member.send(embed=dm_embed)
            except:
                pass  # Couldn't send DM, continue with ban
            
            # Ban the member
            await member.ban(reason=f"Automatic ban: 15 warnings reached. Latest: {reason}")
            
            # Send ban notification to modlog
            if modlog_channel:
                ban_embed = discord.Embed(
                    title="🔨 Automatic Ban",
                    description=f"{member.mention} has been automatically banned for reaching 15 warnings.",
                    color=discord.Color.red()
                )
                ban_embed.add_field(name="Member", value=f"{member} (ID: {member.id})", inline=False)
                ban_embed.add_field(name="Final Reason", value=reason, inline=False)
                ban_embed.timestamp = discord.utils.utcnow()
                await modlog_channel.send(embed=ban_embed)
            
            # Notify in channel
            ban_notify = discord.Embed(
                title="🔨 Member Banned",
                description=f"{member.mention} has been automatically banned for accumulating 15 warnings.",
                color=discord.Color.red()
            )
            await ctx.send(embed=ban_notify)
            
        except discord.Forbidden:
            error_embed = discord.Embed(
                title="Ban Failed",
                description=f"Failed to ban {member.mention}. I don't have permission to ban members.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)
        except Exception as e:
            print(f"Error banning member: {e}")
            error_embed = discord.Embed(
                title="Ban Failed",
                description=f"An error occurred while trying to ban {member.mention}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)

@warn.error
async def warn_error(ctx, error):
    """Error handler for warn command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="Member Not Found",
            description="Could not find that member. Make sure you're using a valid @mention or user ID.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in warn command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='warnings', aliases=['warns'])
@commands.has_permissions(administrator=True)
async def check_warnings(ctx, member: discord.Member = None):
    """
    Check warnings for a member.
    
    Usage: -warnings @username
           -warnings user_id
    """
    global warnings
    
    # Check if a member was provided
    if member is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}warnings @member\n\nExample: {PREFIX}warnings @user",
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    member_id = str(member.id)
    member_warnings = warnings["users"].get(member_id, [])
    warning_count = len(member_warnings)
    
    # Create embed
    embed = discord.Embed(
        title=f"📋 Warnings for {member.name}",
        description=f"{member.mention} has **{warning_count}/15** warnings.",
        color=discord.Color.orange() if warning_count > 0 else discord.Color.green()
    )
    
    if warning_count == 0:
        embed.add_field(name="Status", value="✅ No warnings", inline=False)
    else:
        # Show last 5 warnings
        recent_warnings = member_warnings[-5:] if len(member_warnings) > 5 else member_warnings
        
        for i, warn in enumerate(reversed(recent_warnings), 1):
            case_id = warn.get('case_id', 'N/A')
            moderator_name = warn.get('moderator_name', 'Unknown')
            reason = warn.get('reason', 'No reason')
            timestamp = warn.get('timestamp', '')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M UTC")
            except:
                time_str = "Unknown time"
            
            embed.add_field(
                name=f"Case #{case_id}",
                value=f"**Moderator:** {moderator_name}\n**Reason:** {reason}\n**Time:** {time_str}",
                inline=False
            )
        
        if len(member_warnings) > 5:
            embed.set_footer(text=f"Showing last 5 of {warning_count} warnings • Use -viewcase <id> for details")
        else:
            embed.set_footer(text=f"Use -viewcase <id> for details")
    
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@check_warnings.error
async def check_warnings_error(ctx, error):
    """Error handler for warnings command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="Member Not Found",
            description="Could not find that member. Make sure you're using a valid @mention or user ID.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        print(f"Unexpected error in warnings command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='viewcase', aliases=['case'])
@commands.has_permissions(administrator=True)
async def view_case(ctx, case_id: int = None):
    """
    View details of a specific warning case by case ID.
    
    Usage: -viewcase <case_id>
           -case <case_id>
    """
    global warnings
    
    # Check if case ID was provided
    if case_id is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}viewcase <case_id>\n\nExample: {PREFIX}viewcase 42",
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Search for the case across all users
    found_case = None
    case_member_id = None
    
    for member_id, member_warns in warnings["users"].items():
        for warn in member_warns:
            if warn.get('case_id') == case_id:
                found_case = warn
                case_member_id = member_id
                break
        if found_case:
            break
    
    if not found_case:
        embed = discord.Embed(
            title="Case Not Found",
            description=f"Could not find case #{case_id}.\n\nMake sure the case ID is correct.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Extract case details
    member_id = found_case.get('member_id', case_member_id)
    member_name = found_case.get('member_name', 'Unknown Member')
    moderator_id = found_case.get('moderator', 'Unknown')
    moderator_name = found_case.get('moderator_name', 'Unknown')
    reason = found_case.get('reason', 'No reason provided')
    timestamp = found_case.get('timestamp', '')
    
    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%A, %B %d, %Y at %I:%M %p UTC")
    except:
        time_str = "Unknown time"
    
    # Try to get the actual member object for thumbnail
    try:
        member = await ctx.guild.fetch_member(int(member_id))
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        member_display = f"{member.mention} ({member})"
    except:
        avatar_url = None
        member_display = f"{member_name} (ID: {member_id})"
    
    # Try to get moderator object
    try:
        moderator = await ctx.guild.fetch_member(int(moderator_id))
        moderator_display = f"{moderator.mention} ({moderator})"
    except:
        moderator_display = f"{moderator_name} (ID: {moderator_id})"
    
    # Get member's warning count
    member_warns = warnings["users"].get(member_id, [])
    warning_count = len(member_warns)
    
    # Create detailed embed
    embed = discord.Embed(
        title=f"📋 Case #{case_id}",
        description="**Warning Details**",
        color=discord.Color.orange()
    )
    
    embed.add_field(name="Member", value=member_display, inline=False)
    embed.add_field(name="Member ID", value=member_id, inline=True)
    embed.add_field(name="Total Warnings", value=f"{warning_count}/15", inline=True)
    embed.add_field(name="Moderator", value=moderator_display, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.add_field(name="Date & Time", value=time_str, inline=False)
    
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)
    
    embed.set_footer(text=f"Case #{case_id}")
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@view_case.error
async def view_case_error(ctx, error):
    """Error handler for viewcase command."""
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
            title="Invalid Case ID",
            description=f"Please provide a valid case ID number.\n\nUsage: {PREFIX}viewcase <case_id>",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        print(f"Unexpected error in viewcase command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='lock')
@commands.has_permissions(administrator=True)
async def lock(ctx):
    """
    Locks the current channel to prevent raids.
    Only members with the bypass role can send messages after locking.
    
    Usage: -lock
    """
    channel = ctx.channel
    
    # Get the bypass role
    bypass_role = ctx.guild.get_role(BYPASS_ROLE_ID)
    if bypass_role is None:
        embed = discord.Embed(
            title="Error",
            description=f"Could not find bypass role with ID {BYPASS_ROLE_ID}. Please check config.json",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    try:
        # Get the @everyone role
        everyone_role = ctx.guild.default_role
        
        # Create permission overwrites to deny send_messages and add_reactions
        overwrites_deny = discord.PermissionOverwrite(
            send_messages=False,
            add_reactions=False
        )
        
        # Create permission overwrites to allow for bypass role
        overwrites_allow = discord.PermissionOverwrite(
            send_messages=True,
            add_reactions=True
        )
        
        # Set permissions for @everyone to deny - this is the base lock
        await channel.set_permissions(
            everyone_role,
            overwrite=overwrites_deny,
            reason=f"Channel locked by {ctx.author}"
        )
        
        # Set permissions for bypass role to allow (this overrides the @everyone deny)
        await channel.set_permissions(
            bypass_role,
            overwrite=overwrites_allow,
            reason=f"Bypass role exemption for locked channel by {ctx.author}"
        )
        
        # Send confirmation embed
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"This channel has been locked. Only members with {bypass_role.mention} can send messages.",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Locked by {ctx.author}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Error",
            description="I don't have permission to manage channel permissions. Please ensure I have the 'Manage Channels' permission.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    except Exception as e:
        print(f"Error locking channel: {e}")
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while locking the channel: {str(e)}",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@lock.error
async def lock_error(ctx, error):
    """Error handler for lock command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in lock command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='unlock')
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    """
    Unlocks the current channel and restores normal permissions.
    
    Usage: -unlock
    """
    channel = ctx.channel
    
    try:
        # Get the @everyone role
        everyone_role = ctx.guild.default_role
        
        # Get the bypass role
        bypass_role = ctx.guild.get_role(BYPASS_ROLE_ID)
        
        # Remove permission overwrites we added during lock
        # Setting overwrite to None removes the overwrite entirely
        
        # Restore @everyone permissions (remove override)
        await channel.set_permissions(
            everyone_role,
            overwrite=None,
            reason=f"Channel unlocked by {ctx.author}"
        )
        
        # Remove the bypass role's explicit permissions
        if bypass_role:
            await channel.set_permissions(
                bypass_role,
                overwrite=None,
                reason=f"Channel unlocked, removing bypass role overrides by {ctx.author}"
            )
        
        # Send confirmation embed
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description="This channel has been unlocked. Normal permissions have been restored.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Unlocked by {ctx.author}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Error",
            description="I don't have permission to manage channel permissions. Please ensure I have the 'Manage Channels' permission.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    except Exception as e:
        print(f"Error unlocking channel: {e}")
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while unlocking the channel: {str(e)}",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@unlock.error
async def unlock_error(ctx, error):
    """Error handler for unlock command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in unlock command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='t', aliases=['timeout'])
@commands.has_permissions(administrator=True)
async def timeout_user(ctx, member: discord.Member = None, duration_str: str = "10m", *, reason: str = "No reason provided"):
    """
    Timeout a member (prevents them from sending messages, reacting, speaking in voice).
    
    Usage: -t @username [duration] [reason]
           -t user_id [duration] [reason]
    
    Duration formats: 5m (minutes), 5h (hours), 5d (days)
    Default duration is 10 minutes if not specified.
    Maximum duration is 28 days.
    """
    # Check if a member was provided
    if member is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}t @member [duration] [reason]\n\nExample: {PREFIX}t @user 5h Spamming",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="Duration Formats",
            value="• `5m` - 5 minutes\n• `5h` - 5 hours\n• `5d` - 5 days\n\nDefault: 10 minutes\nMaximum: 28 days",
            inline=False
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Parse duration string
    duration_minutes = 10  # Default
    try:
        duration_str = duration_str.lower().strip()
        if duration_str.endswith('m'):
            # Minutes
            duration_minutes = int(duration_str[:-1])
        elif duration_str.endswith('h'):
            # Hours
            duration_minutes = int(duration_str[:-1]) * 60
        elif duration_str.endswith('d'):
            # Days
            duration_minutes = int(duration_str[:-1]) * 1440
        else:
            # Try parsing as plain number (minutes)
            duration_minutes = int(duration_str)
    except (ValueError, AttributeError):
        embed = discord.Embed(
            title="Invalid Duration Format",
            description=f"Invalid duration format: `{duration_str}`\n\nValid formats: `5m`, `5h`, `5d`, or just `5` for minutes.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Cannot timeout bots
    if member.bot:
        embed = discord.Embed(
            title="Cannot Timeout Bot",
            description="You cannot timeout bot users.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Cannot timeout yourself
    if member.id == ctx.author.id:
        embed = discord.Embed(
            title="Cannot Timeout Yourself",
            description="You cannot timeout yourself.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Cannot timeout server owner
    if member.id == ctx.guild.owner_id:
        embed = discord.Embed(
            title="Cannot Timeout Owner",
            description="You cannot timeout the server owner.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Check if member has higher or equal role than the command author
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        embed = discord.Embed(
            title="Cannot Timeout Member",
            description="You cannot timeout someone with a role equal to or higher than yours.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Validate duration (max is 28 days = 40320 minutes)
    if duration_minutes < 1:
        duration_minutes = 1
    if duration_minutes > 40320:
        duration_minutes = 40320
    
    # Format duration display (human-readable)
    def format_duration(minutes):
        if minutes >= 1440:
            days = minutes // 1440
            remaining_hours = (minutes % 1440) // 60
            if remaining_hours > 0:
                return f"{days}d {remaining_hours}h"
            return f"{days}d"
        elif minutes >= 60:
            hours = minutes // 60
            remaining_mins = minutes % 60
            if remaining_mins > 0:
                return f"{hours}h {remaining_mins}m"
            return f"{hours}h"
        else:
            return f"{minutes}m"
    
    duration_display = format_duration(duration_minutes)
    
    try:
        # Calculate timeout until time (duration in minutes)
        from datetime import timedelta
        timeout_until = discord.utils.utcnow() + timedelta(minutes=duration_minutes)
        
        # Apply timeout
        await member.timeout(timeout_until, reason=f"Timed out by {ctx.author}: {reason}")
        
        # Send confirmation embed
        embed = discord.Embed(
            title="⏰ Member Timed Out",
            description=f"{member.mention} has been timed out.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Member", value=f"{member} ({member.mention})", inline=False)
        embed.add_field(name="Duration", value=duration_display, inline=True)
        embed.add_field(name="Until", value=discord.utils.format_dt(timeout_until, style='F'), inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Timed out by {ctx.author}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
        
        # Try to DM the member
        try:
            dm_embed = discord.Embed(
                title="⏰ You Have Been Timed Out",
                description=f"You have been timed out in **{ctx.guild.name}**.",
                color=discord.Color.orange()
            )
            dm_embed.add_field(name="Duration", value=duration_display, inline=True)
            dm_embed.add_field(name="Ends", value=discord.utils.format_dt(timeout_until, style='F'), inline=True)
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(
                name="What does this mean?",
                value="You cannot send messages, add reactions, or speak in voice channels during the timeout period.",
                inline=False
            )
            dm_embed.set_footer(text=f"Timed out by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.timestamp = discord.utils.utcnow()
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # Member has DMs disabled, that's okay
            pass
        except Exception as e:
            print(f"Error sending timeout DM: {e}")
        
        # Log to modlog channel
        try:
            modlog_channel = bot.get_channel(MODLOG_CHANNEL_ID)
            if modlog_channel:
                log_embed = discord.Embed(
                    title="⏰ Member Timed Out",
                    description=f"{member.mention} has been timed out.",
                    color=discord.Color.orange()
                )
                log_embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
                log_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
                log_embed.add_field(name="Duration", value=duration_display, inline=True)
                log_embed.add_field(name="Until", value=discord.utils.format_dt(timeout_until, style='F'), inline=True)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                log_embed.timestamp = discord.utils.utcnow()
                await modlog_channel.send(embed=log_embed)
        except Exception as e:
            print(f"Error logging timeout to modlog: {e}")
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Error",
            description="I don't have permission to timeout this member. Please ensure I have the 'Moderate Members' permission and my role is higher than the target member's highest role.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    except Exception as e:
        print(f"Error timing out member: {e}")
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while timing out the member: {str(e)}",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@timeout_user.error
async def timeout_error(ctx, error):
    """Error handler for timeout command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="Member Not Found",
            description="Could not find that member. Make sure you're using a valid @mention or user ID.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in timeout command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='ut', aliases=['untimeout', 'removetimeout'])
@commands.has_permissions(administrator=True)
async def untimeout_user(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
    """
    Remove timeout from a member early.
    
    Usage: -ut @username [reason]
           -ut user_id [reason]
    """
    # Check if a member was provided
    if member is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}ut @member [reason]\n\nExample: {PREFIX}ut @user Apologized",
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    # Check if member is actually timed out
    if member.timed_out_until is None or member.timed_out_until < discord.utils.utcnow():
        embed = discord.Embed(
            title="Not Timed Out",
            description=f"{member.mention} is not currently timed out.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    try:
        # Remove timeout (set timeout to None)
        await member.timeout(None, reason=f"Timeout removed by {ctx.author}: {reason}")
        
        # Send confirmation embed
        embed = discord.Embed(
            title="✅ Timeout Removed",
            description=f"Timeout has been removed from {member.mention}.",
            color=discord.Color.green()
        )
        embed.add_field(name="Member", value=f"{member} ({member.mention})", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Removed by {ctx.author}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
        
        # Try to DM the member
        try:
            dm_embed = discord.Embed(
                title="✅ You Have Been Successfully Unmuted",
                description=f"You have been successfully unmuted in **{ctx.guild.name}**.",
                color=discord.Color.green()
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(
                name="You can now:",
                value="• Send messages in text channels\n• Add reactions to messages\n• Speak in voice channels",
                inline=False
            )
            dm_embed.set_footer(text=f"Unmuted by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
            dm_embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            dm_embed.timestamp = discord.utils.utcnow()
            await member.send(embed=dm_embed)
        except discord.Forbidden:
            # Member has DMs disabled, that's okay
            pass
        except Exception as e:
            print(f"Error sending untimeout DM: {e}")
        
        # Log to modlog channel
        try:
            modlog_channel = bot.get_channel(MODLOG_CHANNEL_ID)
            if modlog_channel:
                log_embed = discord.Embed(
                    title="✅ Timeout Removed",
                    description=f"Timeout removed from {member.mention}.",
                    color=discord.Color.green()
                )
                log_embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
                log_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=False)
                log_embed.add_field(name="Reason", value=reason, inline=False)
                log_embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
                log_embed.timestamp = discord.utils.utcnow()
                await modlog_channel.send(embed=log_embed)
        except Exception as e:
            print(f"Error logging untimeout to modlog: {e}")
        
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Error",
            description="I don't have permission to remove timeout from this member. Please ensure I have the 'Moderate Members' permission and my role is higher than the target member's highest role.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    except Exception as e:
        print(f"Error removing timeout: {e}")
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while removing timeout: {str(e)}",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@untimeout_user.error
async def untimeout_error(ctx, error):
    """Error handler for untimeout command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="Member Not Found",
            description="Could not find that member. Make sure you're using a valid @mention or user ID.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in untimeout command: {error}")
        embed = discord.Embed(
            title="Error",
            description="An unexpected error occurred. Please try again.",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)

@bot.command(name='m', aliases=['messages'])
async def message_stats(ctx, member: discord.Member = None):
    """
    Shows message count statistics for a user.
    
    Usage: -m @username
    
    Displays:
    - Messages today
    - Messages this week
    - Messages this month
    - All-time messages
    """
    # If no member specified, show stats for the command author
    if member is None:
        member = ctx.author
    
    user_id = str(member.id)
    
    # Get user's message timestamps
    user_messages = messages_data.get(user_id, [])
    
    if not user_messages:
        embed = discord.Embed(
            title="Message Statistics",
            description=f"No messages tracked for {member.mention} yet.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
        return
    
    # Calculate time periods
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=now.weekday())
    week_start = datetime(week_start.year, week_start.month, week_start.day)
    month_start = datetime(now.year, now.month, 1)
    
    # Count messages in each period
    messages_today = 0
    messages_week = 0
    messages_month = 0
    messages_all_time = len(user_messages)
    
    for timestamp_str in user_messages:
        try:
            msg_time = datetime.fromisoformat(timestamp_str)
            
            if msg_time >= today_start:
                messages_today += 1
            if msg_time >= week_start:
                messages_week += 1
            if msg_time >= month_start:
                messages_month += 1
        except (ValueError, AttributeError):
            # Skip invalid timestamps
            continue
    
    # Create embed
    embed = discord.Embed(
        title="Message Statistics",
        description=f"Activity stats for {member.mention}",
        color=discord.Color.blue()
    )
    
    # Add statistics fields
    embed.add_field(name="Today", value=f"**{messages_today:,}** messages", inline=True)
    embed.add_field(name="This Week", value=f"**{messages_week:,}** messages", inline=True)
    embed.add_field(name="This Month", value=f"**{messages_month:,}** messages", inline=True)
    embed.add_field(name="All Time", value=f"**{messages_all_time:,}** messages", inline=True)
    
    # Set user's profile picture in the corner
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    # Add footer with context
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

# -----------------------------
# INVITE TRACKING COMMANDS
# -----------------------------

@bot.command(name='i', aliases=['invites'])
async def check_invites(ctx, member: discord.Member = None):
    """
    Check invite statistics for a user.
    
    Usage: -i [@user]
    Shows total invites and breakdown of regular, fake, left, and added invites.
    """
    # Default to command author if no member specified
    if member is None:
        member = ctx.author
    
    guild = ctx.guild
    if not guild:
        await ctx.send("This command can only be used in a server.")
        return
    
    # Get invite statistics
    invite_stats = await get_user_invites(guild, member.id)
    
    # Create embed
    embed = discord.Embed(
        title="Invite Statistics",
        description=f"Invite stats for {member.mention}",
        color=discord.Color.blue()
    )
    
    # Main total display
    embed.add_field(
        name="Total Invites",
        value=f"**{invite_stats['total']:,}** ({invite_stats['regular']:,} regular, {invite_stats['fake']:,} fake, {invite_stats['left']:,} left, {invite_stats['added']:,} added)",
        inline=False
    )
    
    # Set user's profile picture
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    
    # Add footer
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@bot.command(name='addinvites')
@commands.has_permissions(administrator=True)
async def add_invites(ctx, member: discord.Member, amount: int):
    """
    Add bonus invites to a user that count toward giveaway requirements.
    
    Usage: -addinvites @user <amount>
    Example: -addinvites @john 50
    """
    if amount <= 0:
        embed = discord.Embed(
            title="Invalid Amount",
            description="Amount must be a positive number.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    user_id_str = str(member.id)
    
    # Initialize user data if not exists
    if user_id_str not in invites_data:
        invites_data[user_id_str] = {
            'regular': 0,
            'fake': 0,
            'left': 0,
            'added': 0
        }
    
    # Add invites
    invites_data[user_id_str]['added'] = invites_data[user_id_str].get('added', 0) + amount
    save_invites(invites_data)
    
    # Get updated stats
    invite_stats = await get_user_invites(ctx.guild, member.id)
    
    # Create confirmation embed
    embed = discord.Embed(
        title="Invites Added",
        description=f"Added **{amount:,}** bonus invites to {member.mention}",
        color=discord.Color.green()
    )
    embed.add_field(
        name="New Total",
        value=f"**{invite_stats['total']:,}** invites",
        inline=False
    )
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@add_invites.error
async def add_invites_error(ctx, error):
    """Error handler for addinvites command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need administrator permissions to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title="Member Not Found",
            description="Could not find that member. Make sure you're using a valid @mention.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage: {PREFIX}addinvites @user <amount>\n\nExample: {PREFIX}addinvites @john 50",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

@bot.command(name='resetinvites')
@commands.has_permissions(administrator=True)
async def reset_invites(ctx, target=None):
    """
    Reset invite data for a user or all users.
    
    Usage: -resetinvites @user  (reset specific user)
           -resetinvites all    (reset everyone)
    """
    if target is None:
        embed = discord.Embed(
            title="Invalid Usage",
            description=f"Usage:\n`{PREFIX}resetinvites @user` - Reset specific user\n`{PREFIX}resetinvites all` - Reset all users",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # Check if resetting all
    if target == 'all':
        # Reset all user invite data to 0 instead of clearing
        for user_id in list(invites_data.keys()):
            invites_data[user_id] = {
                'regular': 0,
                'fake': 0,
                'left': 0,
                'added': 0
            }
        save_invites(invites_data)
        
        embed = discord.Embed(
            title="All Invites Reset",
            description="All server invite data has been completely reset to 0.",
            color=discord.Color.green()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
        return
    
    # Try to parse as member mention or ID
    try:
        member = await commands.MemberConverter().convert(ctx, target)
    except commands.MemberNotFound:
        embed = discord.Embed(
            title="Member Not Found",
            description=f"Could not find member `{target}`. Use a valid @mention or 'all'.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    user_id_str = str(member.id)
    
    # Reset user's invite data - set all to 0 instead of deleting
    invites_data[user_id_str] = {
        'regular': 0,
        'fake': 0,
        'left': 0,
        'added': 0
    }
    save_invites(invites_data)
    
    embed = discord.Embed(
        title="Invites Reset",
        description=f"Invite data for {member.mention} has been completely reset to 0.",
        color=discord.Color.green()
    )
    embed.timestamp = discord.utils.utcnow()
    await ctx.send(embed=embed)

@reset_invites.error
async def reset_invites_error(ctx, error):
    """Error handler for resetinvites command."""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permission Denied",
            description="You need administrator permissions to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@bot.command(name='invlb', aliases=['inviteleaderboard', 'invitelb'])
async def invite_leaderboard(ctx):
    """
    Display the server's invite leaderboard.
    
    Usage: -invlb
    Shows top members ranked by total invite count.
    """
    guild = ctx.guild
    if not guild:
        await ctx.send("This command can only be used in a server.")
        return
    
    # Fetch guild invites ONCE to avoid rate limiting
    try:
        guild_invites = await guild.invites()
    except discord.Forbidden:
        embed = discord.Embed(
            title="Permission Error",
            description="Bot needs 'Manage Guild' permission to track invites.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Calculate invites for all users in a single pass
    user_invites = {}
    
    # Count regular invites from Discord's invite system
    for invite in guild_invites:
        if invite.inviter:
            inviter_id = str(invite.inviter.id)
            if inviter_id not in user_invites:
                user_invites[inviter_id] = 0
            user_invites[inviter_id] += invite.uses
    
    # Collect leaderboard data
    leaderboard_data = []
    
    for member in guild.members:
        if member.bot:
            continue
        
        user_id_str = str(member.id)
        
        # Get regular invites from our calculated data
        regular = user_invites.get(user_id_str, 0)
        
        # Get additional data from persistent storage
        user_data = invites_data.get(user_id_str, {'regular': 0, 'fake': 0, 'left': 0, 'added': 0})
        fake = user_data.get('fake', 0)
        left = user_data.get('left', 0)
        added = user_data.get('added', 0)
        
        # Calculate total
        total = max(0, regular + added - fake - left)
        
        if total > 0:
            leaderboard_data.append({
                'member': member,
                'total': total
            })
    
    # Sort by total invites descending
    leaderboard_data.sort(key=lambda x: x['total'], reverse=True)
    
    # Take top 10
    top_users = leaderboard_data[:10]
    
    if not top_users:
        embed = discord.Embed(
            title="Invite Leaderboard",
            description="No invite data available yet.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
        return
    
    # Create embed
    embed = discord.Embed(
        title="Invite Leaderboard",
        description="Top members by invite count",
        color=discord.Color.blue()
    )
    
    # Add leaderboard entries
    leaderboard_text = ""
    for i, entry in enumerate(top_users, 1):
        member = entry['member']
        total = entry['total']
        leaderboard_text += f"**{i}.** {member.mention} - **{total:,}** invites\n"
    
    embed.add_field(name="Rankings", value=leaderboard_text, inline=False)
    
    # Add footer
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

# -----------------------------
# GIVEAWAY COMMANDS
# -----------------------------

def parse_duration(duration_str):
    """Parse duration string like '10 minutes', '5 hours', '2 days' into seconds."""
    match = re.match(r'^(\d+)\s*(m|min|minute|minutes|h|hr|hour|hours|d|day|days)$', duration_str.lower())
    if not match:
        return None
    
    value = int(match.group(1))
    unit = match.group(2)
    
    if unit.startswith('m'):
        return value * 60  # minutes to seconds
    elif unit.startswith('h'):
        return value * 3600  # hours to seconds
    elif unit.startswith('d'):
        return value * 86400  # days to seconds
    
    return None

def get_entry_count(member):
    """Get the number of entries a member gets based on their roles."""
    # Server Booster gets 4 entries and bypasses requirements
    if member.get_role(SERVER_BOOSTER_ROLE_ID):
        return 4, True
    
    # Shop Owner gets 3 entries
    if member.get_role(SHOP_OWNER_ROLE_ID):
        return 3, False
    
    # Level 5 gets 2 entries
    if member.get_role(LEVEL5_ROLE_ID):
        return 2, False
    
    # Member role gets 1 entry
    if member.get_role(MEMBER_ROLE_ID):
        return 1, False
    
    return 0, False

def check_message_requirement(user_id, requirement, period):
    """Check if user meets message requirements."""
    user_messages = messages_data.get(str(user_id), [])
    
    if not user_messages:
        return False
    
    now = datetime.utcnow()
    
    if period == 'today':
        start_time = datetime(now.year, now.month, now.day)
    elif period == 'weekly':
        start_time = now - timedelta(days=now.weekday())
        start_time = datetime(start_time.year, start_time.month, start_time.day)
    elif period == 'monthly':
        start_time = datetime(now.year, now.month, 1)
    else:
        return False
    
    message_count = 0
    for timestamp_str in user_messages:
        try:
            msg_time = datetime.fromisoformat(timestamp_str)
            if msg_time >= start_time:
                message_count += 1
        except (ValueError, AttributeError):
            continue
    
    return message_count >= requirement

async def get_user_invites(guild, user_id):
    """
    Get user's total invite count including regular, added, fake, and left tracking.
    This tracks invites created by the user that have been used, plus any manually added bonuses.
    Works similarly to Invite Tracker bot (ID: 720351927581278219).
    Returns dict with: regular, fake, left, added, total
    """
    user_id_str = str(user_id)
    
    # Initialize user data if not exists
    if user_id_str not in invites_data:
        invites_data[user_id_str] = {
            'regular': 0,
            'fake': 0,
            'left': 0,
            'added': 0
        }
    
    try:
        # Fetch all guild invites to get regular invites
        guild_invites = await guild.invites()
        
        # Count invites created by this user
        regular_count = 0
        for invite in guild_invites:
            if invite.inviter and invite.inviter.id == user_id:
                # Add the number of times this invite code has been used
                regular_count += invite.uses
        
        # Update regular invite count
        invites_data[user_id_str]['regular'] = regular_count
        save_invites(invites_data)
        
    except discord.Forbidden:
        # Bot doesn't have permission to view invites
        print(f"Missing permissions to view invites in guild {guild.id}")
        regular_count = invites_data[user_id_str].get('regular', 0)
    except Exception as e:
        print(f"Error fetching invites for user {user_id}: {e}")
        regular_count = invites_data[user_id_str].get('regular', 0)
    
    # Get all invite stats
    stats = invites_data[user_id_str]
    fake = stats.get('fake', 0)
    left = stats.get('left', 0)
    added = stats.get('added', 0)
    
    # Calculate total: regular + added - fake - left
    total = regular_count + added - fake - left
    
    return {
        'regular': regular_count,
        'fake': fake,
        'left': left,
        'added': added,
        'total': max(0, total)  # Don't allow negative totals
    }

def calculate_total_entries(participants):
    """Calculate total entries from all participants."""
    total = 0
    for participant_data in participants.values():
        total += participant_data.get('entries', 1)
    return total

async def update_giveaway_embed(giveaway_id):
    """Update giveaway embed with current entry count."""
    giveaway = giveaways_data.get(giveaway_id)
    if not giveaway or giveaway.get('ended', False):
        return
    
    try:
        guild = bot.get_guild(giveaway['guildId'])
        if not guild:
            return
        
        channel = guild.get_channel(giveaway['channelId'])
        if not channel:
            return
        
        message = await channel.fetch_message(giveaway['messageId'])
        if not message:
            return
        
        # Calculate total entries
        total_entries = calculate_total_entries(giveaway.get('participants', {}))
        
        # Recreate the embed with updated entry count
        giveaway_embed = discord.Embed(
            title=f"GIVEAWAY: {giveaway['prize']}",
            description='Click the button below to enter!',
            color=discord.Color.green()
        )
        giveaway_embed.add_field(name='Prize', value=giveaway['prize'], inline=False)
        giveaway_embed.add_field(name='Winners', value=str(giveaway['winners']), inline=True)
        giveaway_embed.add_field(name='Ends', value=f"<t:{int(giveaway['endsAt'])}:R>", inline=True)
        giveaway_embed.add_field(name='Entries', value=f"**{total_entries}**", inline=True)
        
        # Add image if provided
        if giveaway.get('imageUrl'):
            giveaway_embed.set_image(url=giveaway['imageUrl'])
        
        # Add requirements to embed
        requirements_text = ''
        if giveaway['inviteRequirement'] > 0:
            requirements_text += f"Invites: {giveaway['inviteRequirement']}\n"
        if giveaway['messageRequirement'] > 0:
            requirements_text += f"Messages: {giveaway['messageRequirement']} ({giveaway['messagePeriod']})\n"
        if requirements_text:
            giveaway_embed.add_field(name='Giveaway Requirements', value=requirements_text, inline=False)
        
        giveaway_embed.add_field(
            name='Entry Bonuses',
            value=f'<@&{MEMBER_ROLE_ID}>: 1 entry\n<@&{LEVEL5_ROLE_ID}>: 2 entries\n<@&{SHOP_OWNER_ROLE_ID}>: 3 entries\n<@&{SERVER_BOOSTER_ROLE_ID}>: 4 entries (bypass requirements)',
            inline=False
        )
        giveaway_embed.set_footer(text=f"Giveaway ID: {giveaway_id}")
        giveaway_embed.timestamp = discord.utils.utcnow()
        
        # Update the message
        await message.edit(embed=giveaway_embed)
        
    except Exception as e:
        print(f"Error updating giveaway embed: {e}")

async def end_giveaway(giveaway_id):
    """End a giveaway and select winners."""
    giveaway = giveaways_data.get(giveaway_id)
    
    if not giveaway or giveaway.get('ended', False):
        return
    
    try:
        guild = bot.get_guild(giveaway['guildId'])
        if not guild:
            return
        
        channel = guild.get_channel(giveaway['channelId'])
        if not channel:
            return
        
        message = await channel.fetch_message(giveaway['messageId'])
        if not message:
            return
        
        # Get participants from stored data
        participants = giveaway.get('participants', {})
        
        if not participants:
            await channel.send('No one entered the giveaway!')
            giveaway['ended'] = True
            save_giveaways(giveaways_data)
            return
        
        valid_entries = []
        
        # Process each participant
        for user_id_str, participant_data in participants.items():
            try:
                user_id = int(user_id_str)
                entries = participant_data.get('entries', 1)
                
                # Add entries for this user
                for _ in range(entries):
                    valid_entries.append(user_id)
            
            except Exception as e:
                print(f"Error processing user {user_id_str}: {e}")
        
        if not valid_entries:
            await channel.send('No valid entries for the giveaway!')
            giveaway['ended'] = True
            save_giveaways(giveaways_data)
            return
        
        # Pick winners
        import random
        winners = []
        winner_ids = set()
        max_winners = min(giveaway['winners'], len(set(valid_entries)))
        
        while len(winners) < max_winners:
            winner_id = random.choice(valid_entries)
            if winner_id not in winner_ids:
                winners.append(winner_id)
                winner_ids.add(winner_id)
        
        # Announce winners
        winner_mentions = ' '.join([f'<@{wid}>' for wid in winners])
        winner_embed = discord.Embed(
            title='Giveaway Ended!',
            description=f"**Prize:** {giveaway['prize']}\n\n**Winner(s):** {winner_mentions}",
            color=discord.Color.gold()
        )
        winner_embed.set_footer(text=f"Giveaway ID: {giveaway_id}")
        winner_embed.timestamp = discord.utils.utcnow()
        
        await channel.send(embed=winner_embed)
        
        # Update giveaway message
        ended_embed = discord.Embed(
            title=f"GIVEAWAY ENDED: {giveaway['prize']}",
            description='This giveaway has ended!',
            color=discord.Color.red()
        )
        ended_embed.add_field(name='Winner(s)', value=winner_mentions, inline=False)
        ended_embed.set_footer(text=f"Giveaway ID: {giveaway_id}")
        ended_embed.timestamp = discord.utils.utcnow()
        
        await message.edit(embed=ended_embed)
        
        # Mark as ended
        giveaway['ended'] = True
        giveaway['winners'] = winners
        save_giveaways(giveaways_data)
        
        # Create tickets for each winner
        try:
            ticket_category = guild.get_channel(TICKET_CATEGORY_ID)
            owner_role = guild.get_role(OWNER_ROLE_ID)
            
            if ticket_category and owner_role:
                for winner_id in winners:
                    try:
                        winner_member = guild.get_member(winner_id)
                        if not winner_member:
                            continue
                        
                        # Create ticket channel
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            winner_member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                            owner_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                        }
                        
                        ticket_channel = await guild.create_text_channel(
                            name=f'gw-{winner_member.name}',
                            category=ticket_category,
                            overwrites=overwrites
                        )
                        
                        # Send congratulations message with pings
                        congrats_embed = discord.Embed(
                            title='Congratulations!',
                            description=f'Congratulations {winner_member.mention} for winning our giveaway! An owner will be with you very soon.',
                            color=discord.Color.gold()
                        )
                        congrats_embed.add_field(name='Prize', value=giveaway['prize'], inline=False)
                        congrats_embed.timestamp = discord.utils.utcnow()
                        
                        await ticket_channel.send(f'{winner_member.mention} {owner_role.mention}', embed=congrats_embed)
                        
                    except Exception as e:
                        print(f"Error creating ticket for winner {winner_id}: {e}")
        except Exception as e:
            print(f"Error creating tickets: {e}")
        
    except Exception as e:
        print(f"Error ending giveaway: {e}")

# Giveaway Button View
class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)  # No timeout for persistent buttons
        self.giveaway_id = giveaway_id
    
    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="giveaway_enter")
    async def enter_giveaway(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle giveaway entry button click."""
        giveaway = giveaways_data.get(self.giveaway_id)
        
        if not giveaway or giveaway.get('ended', False):
            await interaction.response.send_message('This giveaway has ended!', ephemeral=True)
            return
        
        try:
            member = interaction.user
            guild = interaction.guild
            
            # Check if already entered first
            if 'participants' not in giveaway:
                giveaway['participants'] = {}
            
            if str(member.id) in giveaway['participants']:
                # User already entered - re-verify their requirements to give updated feedback
                entries, bypass = get_entry_count(member)
                
                if entries == 0:
                    # Remove them if they no longer have the role
                    del giveaway['participants'][str(member.id)]
                    save_giveaways(giveaways_data)
                    
                    # Update the giveaway embed with new entry count
                    await update_giveaway_embed(self.giveaway_id)
                    
                    await interaction.response.send_message('You no longer have the required role for this giveaway!', ephemeral=True)
                    return
                
                # Check requirements again (unless bypassed)
                if not bypass:
                    invite_met = True
                    message_met = True
                    
                    if giveaway.get('inviteRequirement', 0) > 0:
                        invite_stats = await get_user_invites(guild, member.id)
                        invite_met = invite_stats['total'] >= giveaway['inviteRequirement']
                    
                    if giveaway.get('messageRequirement', 0) > 0:
                        message_met = check_message_requirement(member.id, giveaway['messageRequirement'], giveaway.get('messagePeriod'))
                    
                    if not (invite_met and message_met):
                        # Remove them if they no longer meet requirements
                        del giveaway['participants'][str(member.id)]
                        save_giveaways(giveaways_data)
                        
                        # Update the giveaway embed with new entry count
                        await update_giveaway_embed(self.giveaway_id)
                        
                        # Determine error message
                        if not invite_met and not message_met:
                            error_message = f"No requirements met! Use -i command to check your invites and spam messages to meet requirement is a blacklist from giveaways!"
                        elif not invite_met:
                            error_message = f"Join failed! You must complete the invite requirement. Use -i command to check your invites."
                        else:
                            error_message = 'Join failed! You must complete the message requirement. Spamming messages is a blacklist from the giveaway!'
                        
                        await interaction.response.send_message(error_message, ephemeral=True)
                        return
                
                # Still meets requirements
                await interaction.response.send_message(f'You have already entered this giveaway with {entries} {"entry" if entries == 1 else "entries"}!', ephemeral=True)
                return
            
            # New entry - verify everything
            entries, bypass = get_entry_count(member)
            
            # Check if user has valid roles
            if entries == 0:
                await interaction.response.send_message('You do not have the required role to enter this giveaway!', ephemeral=True)
                return
            
            # Check requirements (unless bypassed by Server Booster)
            if not bypass:
                invite_met = True
                message_met = True
                error_message = ''
                
                if giveaway.get('inviteRequirement', 0) > 0:
                    invite_stats = await get_user_invites(guild, member.id)
                    invite_met = invite_stats['total'] >= giveaway['inviteRequirement']
                
                if giveaway.get('messageRequirement', 0) > 0:
                    message_met = check_message_requirement(member.id, giveaway['messageRequirement'], giveaway.get('messagePeriod'))
                
                # Determine error message
                if not invite_met and not message_met:
                    error_message = f"No requirements met! Use -i command to check your invites and spam messages to meet requirement is a blacklist from giveaways!"
                elif not invite_met:
                    error_message = f"Join failed! You must complete the invite requirement. Use -i command to check your invites."
                elif not message_met:
                    error_message = 'Join failed! You must complete the message requirement. Spamming messages is a blacklist from the giveaway!'
                
                if error_message:
                    await interaction.response.send_message(error_message, ephemeral=True)
                    return
            
            # User successfully entered - track their entry
            giveaway['participants'][str(member.id)] = {
                'entries': entries,
                'bypass': bypass,
                'timestamp': datetime.utcnow().timestamp()
            }
            save_giveaways(giveaways_data)
            
            # Update the giveaway embed with new entry count
            await update_giveaway_embed(self.giveaway_id)
            
            await interaction.response.send_message(f'Successfully entered the giveaway with {entries} {"entry" if entries == 1 else "entries"}!', ephemeral=True)
            
        except Exception as e:
            print(f"Error processing giveaway entry: {e}")
            await interaction.response.send_message('An error occurred while processing your entry.', ephemeral=True)

@bot.command(name='gcreate')
@commands.has_permissions(administrator=True)
async def create_giveaway(ctx):
    """
    Create a new giveaway with interactive setup (Admin only).
    
    Usage: -gcreate
    """
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    giveaway_data = {}
    messages_to_delete = [ctx.message]  # Track messages to delete later
    
    try:
        # Question 1: Duration
        q1 = await ctx.send('**Giveaway Setup - Question 1/6**\nEnter the duration (e.g., "10 minutes", "5 hours", "2 days"):')
        messages_to_delete.append(q1)
        duration_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(duration_msg)
        duration_seconds = parse_duration(duration_msg.content)
        
        if not duration_seconds:
            error_msg = await ctx.send('Invalid duration format. Giveaway creation cancelled.')
            messages_to_delete.append(error_msg)
            return
        
        giveaway_data['duration'] = duration_seconds
        giveaway_data['endsAt'] = (datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)).timestamp()
        
        # Question 2: Number of Winners
        q2 = await ctx.send('**Giveaway Setup - Question 2/6**\nEnter the number of winners:')
        messages_to_delete.append(q2)
        winners_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(winners_msg)
        
        try:
            winners = int(winners_msg.content)
            if winners < 1:
                raise ValueError
        except ValueError:
            error_msg = await ctx.send('Invalid number of winners. Giveaway creation cancelled.')
            messages_to_delete.append(error_msg)
            return
        
        giveaway_data['winners'] = winners
        
        # Question 3: Prize
        q3 = await ctx.send('**Giveaway Setup - Question 3/6**\nEnter the prize:')
        messages_to_delete.append(q3)
        prize_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(prize_msg)
        giveaway_data['prize'] = prize_msg.content
        
        # Question 4: Invite Requirement
        q4 = await ctx.send('**Giveaway Setup - Question 4/6 (Requirements)**\nEnter the invite requirement (or 0 for no requirement):')
        messages_to_delete.append(q4)
        invite_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(invite_msg)
        
        try:
            invite_req = int(invite_msg.content)
            if invite_req < 0:
                raise ValueError
        except ValueError:
            error_msg = await ctx.send('Invalid invite requirement. Giveaway creation cancelled.')
            messages_to_delete.append(error_msg)
            return
        
        giveaway_data['inviteRequirement'] = invite_req
        
        # Question 5: Message Requirement
        q5 = await ctx.send('**Giveaway Setup - Question 5/6 (Requirements)**\nEnter the message requirement followed by period (e.g., "250 weekly", "100 today", "500 monthly") or "0" for no requirement:')
        messages_to_delete.append(q5)
        message_req_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(message_req_msg)
        message_req_content = message_req_msg.content.strip()
        
        if message_req_content == '0':
            giveaway_data['messageRequirement'] = 0
            giveaway_data['messagePeriod'] = None
        else:
            msg_match = re.match(r'^(\d+)\s+(today|weekly|monthly)$', message_req_content, re.IGNORECASE)
            if not msg_match:
                error_msg = await ctx.send('Invalid message requirement format. Use format like "250 weekly". Giveaway creation cancelled.')
                messages_to_delete.append(error_msg)
                return
            giveaway_data['messageRequirement'] = int(msg_match.group(1))
            giveaway_data['messagePeriod'] = msg_match.group(2).lower()
        
        # Question 6: Optional Picture
        q6 = await ctx.send('**Giveaway Setup - Question 6/6 (Optional Picture)**\nSend an image URL or type "no" to skip:')
        messages_to_delete.append(q6)
        picture_msg = await bot.wait_for('message', check=check, timeout=60.0)
        messages_to_delete.append(picture_msg)
        picture_content = picture_msg.content.strip().lower()
        
        if picture_content != 'no':
            # Check if message has attachments or contains a URL
            if picture_msg.attachments:
                giveaway_data['imageUrl'] = picture_msg.attachments[0].url
            elif picture_content.startswith('http://') or picture_content.startswith('https://'):
                giveaway_data['imageUrl'] = picture_content
            else:
                giveaway_data['imageUrl'] = None
        else:
            giveaway_data['imageUrl'] = None
        
        # Generate giveaway ID
        giveaway_id = f"giveaway_{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Create giveaway embed
        giveaway_embed = discord.Embed(
            title=f"GIVEAWAY: {giveaway_data['prize']}",
            description='Click the button below to enter!',
            color=discord.Color.green()
        )
        giveaway_embed.add_field(name='Prize', value=giveaway_data['prize'], inline=False)
        giveaway_embed.add_field(name='Winners', value=str(giveaway_data['winners']), inline=True)
        giveaway_embed.add_field(name='Ends', value=f"<t:{int(giveaway_data['endsAt'])}:R>", inline=True)
        giveaway_embed.add_field(name='Entries', value='**0**', inline=True)
        
        # Add image if provided
        if giveaway_data.get('imageUrl'):
            giveaway_embed.set_image(url=giveaway_data['imageUrl'])
        
        # Add requirements to embed
        requirements_text = ''
        if giveaway_data['inviteRequirement'] > 0:
            requirements_text += f"Invites: {giveaway_data['inviteRequirement']}\n"
        if giveaway_data['messageRequirement'] > 0:
            requirements_text += f"Messages: {giveaway_data['messageRequirement']} ({giveaway_data['messagePeriod']})\n"
        if requirements_text:
            giveaway_embed.add_field(name='Giveaway Requirements', value=requirements_text, inline=False)
        
        giveaway_embed.add_field(
            name='Entry Bonuses',
            value=f'<@&{MEMBER_ROLE_ID}>: 1 entry\n<@&{LEVEL5_ROLE_ID}>: 2 entries\n<@&{SHOP_OWNER_ROLE_ID}>: 3 entries\n<@&{SERVER_BOOSTER_ROLE_ID}>: 4 entries (bypass requirements)',
            inline=False
        )
        giveaway_embed.set_footer(text=f"Giveaway ID: {giveaway_id}")
        giveaway_embed.timestamp = discord.utils.utcnow()
        
        # Create button view
        view = GiveawayView(giveaway_id)
        
        # Send giveaway message with button
        giveaway_msg = await ctx.send(embed=giveaway_embed, view=view)
        
        # Save giveaway data
        giveaways_data[giveaway_id] = {
            **giveaway_data,
            'messageId': giveaway_msg.id,
            'channelId': ctx.channel.id,
            'guildId': ctx.guild.id,
            'createdBy': ctx.author.id,
            'participants': {},
            'ended': False
        }
        save_giveaways(giveaways_data)
        
        # Send confirmation to giveaway channel
        try:
            giveaway_channel = bot.get_channel(GIVEAWAY_CHANNEL_ID)
            if giveaway_channel:
                confirm_embed = discord.Embed(
                    title='New Giveaway Created',
                    description=f"A new giveaway has been created in <#{ctx.channel.id}>",
                    color=discord.Color.blue()
                )
                confirm_embed.add_field(name='Giveaway ID', value=giveaway_id, inline=False)
                confirm_embed.add_field(name='Prize', value=giveaway_data['prize'], inline=False)
                confirm_embed.add_field(name='Duration', value=f"Ends <t:{int(giveaway_data['endsAt'])}:R>", inline=False)
                confirm_embed.add_field(name='Created By', value=f"<@{ctx.author.id}>", inline=False)
                confirm_embed.timestamp = discord.utils.utcnow()
                
                await giveaway_channel.send(embed=confirm_embed)
        except Exception as e:
            print(f"Error sending to giveaway channel: {e}")
        
        # Setup timer to end giveaway
        bot.loop.create_task(schedule_giveaway_end(giveaway_id, giveaway_data['duration']))
        
        success_msg = await ctx.send('Giveaway created successfully!')
        messages_to_delete.append(success_msg)
        
        # Purge all setup messages after 2 seconds
        await asyncio.sleep(2)
        try:
            await ctx.channel.delete_messages(messages_to_delete)
        except Exception as e:
            print(f"Error deleting messages: {e}")
        
    except asyncio.TimeoutError:
        timeout_msg = await ctx.send('Giveaway creation timed out. Please try again.')
        messages_to_delete.append(timeout_msg)
    except Exception as e:
        print(f"Error creating giveaway: {e}")
        error_msg = await ctx.send(f'An error occurred while creating the giveaway: {str(e)}')
        messages_to_delete.append(error_msg)

async def schedule_giveaway_end(giveaway_id, delay):
    """Schedule giveaway to end after delay seconds."""
    await asyncio.sleep(delay)
    await end_giveaway(giveaway_id)

@bot.command(name='greroll')
@commands.has_permissions(administrator=True)
async def reroll_giveaway(ctx, giveaway_id: str = None):
    """
    Reroll a giveaway to pick new winner(s) (Admin only).
    
    Usage: -greroll <giveaway_id>
    """
    if not giveaway_id:
        embed = discord.Embed(
            title='Invalid Usage',
            description='Usage: -greroll <giveaway_id>\n\nYou can find the giveaway ID in the footer of the giveaway message.',
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    giveaway = giveaways_data.get(giveaway_id)
    
    if not giveaway:
        embed = discord.Embed(
            title='Giveaway Not Found',
            description=f"No giveaway found with ID: {giveaway_id}",
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    if not giveaway.get('ended', False):
        embed = discord.Embed(
            title='Giveaway Not Ended',
            description='You can only reroll giveaways that have already ended!',
            color=discord.Color.red()
        )
        embed.timestamp = discord.utils.utcnow()
        await ctx.reply(embed=embed)
        return
    
    try:
        guild = bot.get_guild(giveaway['guildId'])
        channel = guild.get_channel(giveaway['channelId'])
        message = await channel.fetch_message(giveaway['messageId'])
        
        # Get participants from stored data
        participants = giveaway.get('participants', {})
        previous_winners = set(giveaway.get('winners', []))
        
        if not participants:
            await ctx.reply('No one entered the giveaway!')
            return
        
        valid_entries = []
        
        # Process each participant (excluding previous winners)
        for user_id_str, participant_data in participants.items():
            user_id = int(user_id_str)
            if user_id in previous_winners:
                continue
            
            try:
                entries = participant_data.get('entries', 1)
                
                # Add entries for this user
                for _ in range(entries):
                    valid_entries.append(user_id)
            
            except Exception as e:
                print(f"Error processing user {user.id}: {e}")
        
        if not valid_entries:
            await ctx.reply('No valid entries remaining for reroll!')
            return
        
        # Pick new winners
        import random
        new_winners = []
        winner_ids = set()
        max_winners = min(giveaway['winners'], len(set(valid_entries)))
        
        while len(new_winners) < max_winners:
            winner_id = random.choice(valid_entries)
            if winner_id not in winner_ids:
                new_winners.append(winner_id)
                winner_ids.add(winner_id)
        
        # Announce new winners
        winner_mentions = ' '.join([f'<@{wid}>' for wid in new_winners])
        reroll_embed = discord.Embed(
            title='Giveaway Rerolled!',
            description=f"**Prize:** {giveaway['prize']}\n\n**New Winner(s):** {winner_mentions}",
            color=discord.Color.gold()
        )
        reroll_embed.set_footer(text=f"Giveaway ID: {giveaway_id}")
        reroll_embed.timestamp = discord.utils.utcnow()
        
        await channel.send(embed=reroll_embed)
        
        # Update stored winners
        giveaway['winners'] = new_winners
        save_giveaways(giveaways_data)
        
        await ctx.reply('Giveaway rerolled successfully!')
        
    except Exception as e:
        print(f"Error rerolling giveaway: {e}")
        embed = discord.Embed(
            title='Error',
            description='An error occurred while rerolling the giveaway.',
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
