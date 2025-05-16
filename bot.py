import os
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

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_voice_state_update(member, before, after):
    # Get the log channel ID from environment variable
    log_channel_id = os.getenv('LOG_CHANNEL_ID')
    if not log_channel_id:
        print("Warning: LOG_CHANNEL_ID not set in .env file")
        return

    log_channel = bot.get_channel(int(log_channel_id))
    if not log_channel:
        print(f"Warning: Could not find channel with ID {log_channel_id}")
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