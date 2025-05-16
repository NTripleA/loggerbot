import asyncio
import discord
import discord.ext.test as dpytest
import pytest
import os
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
    
    @bot.event
    async def on_ready():
        print(f'Test bot {bot.user} is ready!')
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        # Get the log channel ID from environment variable
        log_channel_id = int(os.getenv('TEST_LOG_CHANNEL_ID'))
        log_channel = bot.get_channel(log_channel_id)
        
        if not log_channel:
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

@pytest.mark.asyncio
async def test_voice_channel_join(bot):
    """Test the bot's response when a user joins a voice channel."""
    # Create a mock voice channel
    guild = dpytest.get_config().guilds[0]
    voice_channel = await guild.create_voice_channel("Test Voice Channel")
    
    # Create a mock member
    member = dpytest.get_config().members[0]
    
    # Simulate voice state update (join)
    before = discord.VoiceState(member, None)
    after = discord.VoiceState(member, voice_channel)
    
    # Trigger the event
    await bot.on_voice_state_update(member, before, after)
    
    # Get the last message sent
    message = dpytest.get_message()
    
    # Verify the message content
    assert message.content == f"🔊 {member.name} has joined {voice_channel.name}"

@pytest.mark.asyncio
async def test_voice_channel_leave(bot):
    """Test the bot's response when a user leaves a voice channel."""
    # Create a mock voice channel
    guild = dpytest.get_config().guilds[0]
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
async def test_voice_channel_switch(bot):
    """Test the bot's response when a user switches voice channels."""
    # Create mock voice channels
    guild = dpytest.get_config().guilds[0]
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