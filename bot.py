import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
import uptime_server  # Import the uptime server module

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Required for voice channel monitoring

bot = commands.Bot(command_prefix='!', intents=intents)

# File to store guild-specific channel settings
GUILD_CONFIG_FILE = 'guild_config.json'

# Load guild configuration from file
def load_guild_config():
    """Load guild configuration from JSON file, create if not exists"""
    if os.path.exists(GUILD_CONFIG_FILE):
        try:
            with open(GUILD_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error loading {GUILD_CONFIG_FILE}, using empty config")
            return {}
    else:
        # Create empty config file if it doesn't exist
        save_guild_config({})
        return {}

# Save guild configuration to file
def save_guild_config(config):
    """Save guild configuration to JSON file"""
    with open(GUILD_CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Guild configuration cache
guild_config = load_guild_config()

@bot.event
async def on_ready():
    """Called when the bot is connected and ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Create config file if it doesn't exist
    if not os.path.exists(GUILD_CONFIG_FILE):
        save_guild_config({})

@bot.command(name='setlog')
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    """Set the channel for voice activity logs. Usage: !setlog #channel-name"""
    # Get guild ID as string for JSON storage
    guild_id = str(ctx.guild.id)
    
    # Save channel ID to guild config
    guild_config[guild_id] = channel.id
    save_guild_config(guild_config)
    
    # Send confirmation message
    await ctx.send(f"Voice log channel set to {channel.mention}")

@set_log_channel.error
async def set_log_channel_error(ctx, error):
    """Handle errors from the setlog command"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a channel. Usage: `!setlog #channel-name`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid channel. Please use the format: `!setlog #channel-name`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You need administrator permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

def get_log_channel(guild):
    """
    Get the configured log channel for a guild, with fallback logic
    
    1. Check guild_config.json for saved channel ID
    2. Fall back to #general if exists
    3. Otherwise use first available text channel
    """
    guild_id = str(guild.id)
    
    # Check if we have a configured channel in settings
    if guild_id in guild_config:
        channel_id = guild_config[guild_id]
        channel = guild.get_channel(channel_id)
        if channel:
            return channel
    
    # Try to find #general as fallback
    for channel in guild.text_channels:
        if channel.name.lower() == 'general':
            return channel
            
    # If all else fails, get the first text channel
    if guild.text_channels:
        return guild.text_channels[0]
    
    return None

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state update events - join, leave, move"""
    # Get the guild from the member
    guild = member.guild
    
    # Dynamic log channel lookup
    log_channel = get_log_channel(guild)
    
    if not log_channel:
        print(f"Warning: No suitable log channel found in {guild.name}")
        return

    # User joined a voice channel
    if before.channel is None and after.channel is not None:
        message = f"🔊 {member.name} has joined {after.channel.name}"
        await log_channel.send(message)
    
    # User left a voice channel
    elif before.channel is not None and after.channel is None:
        message = f"❌ {member.name} has left {before.channel.name}"
        await log_channel.send(message)
    
    # User switched voice channels
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        message = f"🔄 {member.name} has moved from {before.channel.name} to {after.channel.name}"
        await log_channel.send(message)

def main():
    """Main entry point for the bot"""
    # Get the token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in .env file")
        return
    
    # Start HTTP server in a separate thread
    uptime_server.run_server()

    try:
        bot.run(token)
    except discord.LoginFailure:
        print("Error: Invalid token provided")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 