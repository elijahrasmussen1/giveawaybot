"""
Discord Giveaway Bot - Python Implementation
A Discord bot for giveaways, game nights, and guess the number game.
"""

import os
import discord
from discord.ext import commands
import json
from datetime import datetime

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
        
        # First, set permissions for @everyone to deny
        await channel.set_permissions(
            everyone_role,
            overwrite=overwrites_deny,
            reason=f"Channel locked by {ctx.author}"
        )
        
        # Then, explicitly set permissions for bypass role to allow (this overrides the @everyone deny)
        await channel.set_permissions(
            bypass_role,
            overwrite=overwrites_allow,
            reason=f"Bypass role exemption for locked channel by {ctx.author}"
        )
        
        # Also deny for all other roles except the bypass role to ensure lock works
        # This is important because role-specific permissions can override @everyone
        for role in ctx.guild.roles:
            # Skip @everyone (already handled), bypass role (already handled), and managed roles (bots)
            if role == everyone_role or role == bypass_role or role.managed or role.is_bot_managed():
                continue
            
            # Only set deny if the role currently has overwrites in this channel
            # or if it's a role with significant permissions
            if channel.overwrites_for(role).send_messages is not False:
                await channel.set_permissions(
                    role,
                    overwrite=overwrites_deny,
                    reason=f"Channel locked by {ctx.author} - denying role {role.name}"
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
        
        # Remove all permission overwrites we added during lock
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
        
        # Also remove overwrites from all other roles that were set during lock
        for role in ctx.guild.roles:
            # Skip @everyone (already handled), bypass role (already handled), and managed roles
            if role == everyone_role or role == bypass_role or role.managed or role.is_bot_managed():
                continue
            
            # If this role has overwrites in this channel, remove them
            overwrites = channel.overwrites_for(role)
            if overwrites.send_messages is False:
                await channel.set_permissions(
                    role,
                    overwrite=None,
                    reason=f"Channel unlocked by {ctx.author} - removing lock overrides from {role.name}"
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

# -----------------------------
# RUN BOT
# -----------------------------
# Get bot token from environment variable or use placeholder
bot_token = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
if bot_token == "YOUR_BOT_TOKEN_HERE":
    print("⚠️ WARNING: Using placeholder bot token. Set DISCORD_BOT_TOKEN environment variable.")
bot.run(bot_token)
