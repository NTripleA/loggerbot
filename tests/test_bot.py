import asyncio
import discord
import discord.ext.test as dpytest
import pytest
import os
import json
from dotenv import load_dotenv

# Load test environment variables
load_dotenv('.env.test')

@pytest.fixture
def bot():
    """Create a bot instance for testing."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    
    bot = discord.ext.commands.Bot(command_prefix='!', intents=intents)
    
    # File to store channel settings
    SETTINGS_FILE = 'channel_settings_test.json'
    
    # Load channel settings from file
    def load_channel_settings():
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    # Save channel settings to file
    def save_channel_settings(settings):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)
    
    # Channel settings cache
    channel_settings = load_channel_settings()
    
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
    async def on_ready():
        print(f'Test bot {bot.user} is ready!')
    
    @bot.command(name='setlog')
    @discord.ext.commands.has_permissions(administrator=True)
    async def set_log_channel(ctx, channel: discord.TextChannel):
        """Set the channel for voice activity logs. Usage: !setlog #channel-name"""
        guild_id = str(ctx.guild.id)
        channel_settings[guild_id] = channel.id
        save_channel_settings(channel_settings)
        await ctx.send(f"Voice log channel set to {channel.mention}")
    
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
    
    return bot

@pytest.fixture
async def setup_guild(bot):
    """Set up a test guild with channels."""
    await dpytest.configure(bot)
    
    # Create a general text channel
    guild = dpytest.get_config().guilds[0]
    general_channel = await guild.create_text_channel("general")
    
    return guild, general_channel

@pytest.mark.asyncio
async def test_voice_channel_join(bot, setup_guild):
    """Test the bot's response when a user joins a voice channel."""
    guild, general_channel = await setup_guild
    
    # Create a mock voice channel
    voice_channel = await guild.create_voice_channel("Test Voice Channel")
    
    # Create a mock member
    member = dpytest.get_config().members[0]
    
    # Simulate voice state update (join)
    before = discord.VoiceState(member, None)
    after = discord.VoiceState(member, voice_channel)
    
    # Trigger the event
    await bot.on_voice_state_update(member, before, after)
    
    # Get the last message sent to general channel
    message = dpytest.get_message()
    
    # Verify the message content
    assert message.content == f"🔊 {member.name} has joined {voice_channel.name}"

@pytest.mark.asyncio
async def test_voice_channel_leave(bot, setup_guild):
    """Test the bot's response when a user leaves a voice channel."""
    guild, general_channel = await setup_guild
    
    # Create a mock voice channel
    voice_channel = await guild.create_voice_channel("Test Voice Channel")
    
    # Create a mock member
    member = dpytest.get_config().members[0]
    
    # Simulate voice state update (leave)
    before = discord.VoiceState(member, voice_channel)
    after = discord.VoiceState(member, None)
    
    # Trigger the event
    await bot.on_voice_state_update(member, before, after)
    
    # Get the last message sent
    message = dpytest.get_message()
    
    # Verify the message content
    assert message.content == f"❌ {member.name} has left {voice_channel.name}"

@pytest.mark.asyncio
async def test_voice_channel_switch(bot, setup_guild):
    """Test the bot's response when a user switches voice channels."""
    guild, general_channel = await setup_guild
    
    # Create mock voice channels
    voice_channel1 = await guild.create_voice_channel("Test Voice Channel 1")
    voice_channel2 = await guild.create_voice_channel("Test Voice Channel 2")
    
    # Create a mock member
    member = dpytest.get_config().members[0]
    
    # Simulate voice state update (switch)
    before = discord.VoiceState(member, voice_channel1)
    after = discord.VoiceState(member, voice_channel2)
    
    # Trigger the event
    await bot.on_voice_state_update(member, before, after)
    
    # Get the last message sent
    message = dpytest.get_message()
    
    # Verify the message content
    assert message.content == f"🔄 {member.name} has moved from {voice_channel1.name} to {voice_channel2.name}"

@pytest.mark.asyncio
async def test_setlog_command(bot, setup_guild):
    """Test the setlog command."""
    guild, general_channel = await setup_guild
    
    # Create a new log channel
    log_channel = await guild.create_text_channel("voice-logs")
    
    # Create a mock member with admin permissions
    member = dpytest.get_config().members[0]
    
    # Make the member an admin
    role = await guild.create_role(name="Admin", permissions=discord.Permissions(administrator=True))
    await member.add_roles(role)
    
    # Call the setlog command
    await dpytest.message(f"!setlog {log_channel.mention}")
    
    # Check for confirmation message
    confirmation = dpytest.get_message()
    assert confirmation.content == f"Voice log channel set to {log_channel.mention}"
    
    # Now test if voice events go to the new channel
    voice_channel = await guild.create_voice_channel("Test Voice Channel")
    
    # Simulate voice state update (join)
    before = discord.VoiceState(member, None)
    after = discord.VoiceState(member, voice_channel)
    
    # Trigger the event
    await bot.on_voice_state_update(member, before, after)
    
    # Get the last message sent (should be in the new log channel)
    message = dpytest.get_message()
    
    # Verify the message content
    assert message.content == f"🔊 {member.name} has joined {voice_channel.name}"
    assert message.channel.id == log_channel.id 