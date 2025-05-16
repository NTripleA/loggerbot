# Discord Voice Channel Logger Bot

A Discord bot that monitors and logs user activity in voice channels within a server.

## Features

- Monitors when users join voice channels
- Monitors when users leave voice channels
- Monitors when users switch between voice channels
- Sends formatted messages to a designated logging channel

## Setup Instructions

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Discord Bot**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to the "Bot" section and click "Add Bot"
   - Under "Privileged Gateway Intents", enable:
     - MESSAGE CONTENT INTENT
     - SERVER MEMBERS INTENT
     - VOICE STATE INTENT
   - Copy the bot token

3. **Create .env File**
   Create a file named `.env` in the project root with the following content:
   ```
   DISCORD_TOKEN=your_bot_token_here
   LOG_CHANNEL_ID=your_channel_id_here
   ```
   Replace:
   - `your_bot_token_here` with your Discord bot token
   - `your_channel_id_here` with the ID of the channel where you want the logs to appear

4. **Invite the Bot to Your Server**
   - In the Discord Developer Portal, go to OAuth2 > URL Generator
   - Select the following scopes:
     - `bot`
     - `applications.commands`
   - Select the following bot permissions:
     - `Send Messages`
     - `View Channels`
   - Use the generated URL to invite the bot to your server

5. **Run the Bot**
   ```bash
   python bot.py
   ```

## Testing

The project includes a Docker-based test setup for end-to-end testing of the bot's functionality.

### Prerequisites

- Docker and Docker Compose installed
- A test Discord bot token
- A test channel ID for logging

### Setup Test Environment

1. Create a `.env.test` file with your test credentials:
   ```
   TEST_DISCORD_TOKEN=your_test_bot_token_here
   TEST_LOG_CHANNEL_ID=your_test_channel_id_here
   ```

2. Run the tests using Docker Compose:
   ```bash
   docker-compose -f docker-compose.test.yml up --build
   ```

### Test Coverage

The test suite includes:
- Voice channel join events
- Voice channel leave events
- Voice channel switch events

Each test verifies that the bot sends the correct formatted message to the logging channel.

### Running Tests Locally

If you prefer to run tests without Docker:

1. Install test dependencies:
   ```bash
   pip install -r requirements.test.txt
   ```

2. Run the tests:
   ```bash
   pytest tests/ -v
   ```

## Usage

Once the bot is running, it will automatically:
- Log when users join voice channels (🔊)
- Log when users leave voice channels (❌)
- Log when users switch between voice channels (🔄)

## Error Handling

The bot includes error handling for:
- Missing environment variables
- Invalid bot token
- Channel not found
- General exceptions

## Requirements

- Python 3.x
- discord.py
- python-dotenv
