import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Required for voice channel monitoring

bot = commands.Bot(command_prefix='!', intents=intents)

# File to store channel settings
SETTINGS_FILE = 'channel_settings.json'

# Load channel settings from file
def load_channel_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error loading {SETTINGS_FILE}, using defaults")
            return {}
    return {}

# Save channel settings to file
def save_channel_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

# Channel settings cache
channel_settings = load_channel_settings()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    
    # Create settings file if it doesn't exist
    if not os.path.exists(SETTINGS_FILE):
        save_channel_settings({})

@bot.command(name='setlog')
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    """Set the channel for voice activity logs. Usage: !setlog #channel-name"""
    guild_id = str(ctx.guild.id)
    channel_settings[guild_id] = channel.id
    save_channel_settings(channel_settings)
    await ctx.send(f"Voice log channel set to {channel.mention}")

@set_log_channel.error
async def set_log_channel_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a channel. Usage: `!setlog #channel-name`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid channel. Please use the format: `!setlog #channel-name`")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You need administrator permissions to use this command.")
    else:
        await ctx.send(f"An error occurred: {error}")

def get_log_channel(guild):
    """Get the configured log channel for a guild, or find #general as fallback"""
    guild_id = str(guild.id)
    
    # Check if we have a configured channel in settings
    if guild_id in channel_settings:
        channel_id = channel_settings[guild_id]
        channel = guild.get_channel(channel_id)
        if channel:
            return channel
    
    # Check for environment variable as secondary option
    env_channel_id = os.getenv('LOG_CHANNEL_ID')
    if env_channel_id:
        try:
            channel = guild.get_channel(int(env_channel_id))
            if channel:
                return channel
        except ValueError:
            pass
    
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
    guild = member.guild
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
    # Get the token from environment variable
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in .env file")
        return

    try:
        bot.run(token)
    except discord.LoginFailure:
        print("Error: Invalid token provided")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 