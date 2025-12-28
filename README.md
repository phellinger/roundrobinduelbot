# Round Robin Duel Bot

A Telegram bot that generates round robin tournament pairings. Each player plays every opponent exactly once, with proper handling of odd numbers of players (one player gets a bye each round).

## Features

- 🤖 Telegram bot interface
- 🎯 Round robin tournament generation
- 👥 Supports any number of players (2+)
- 😴 Automatic bye handling for odd numbers of players
- 🐳 Docker containerization
- 🚀 Easy deployment via Makefile

## Setup

1. **Create a Telegram Bot**
   - Talk to [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Save the bot token

2. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN, TARGET_HOST, and TARGET_PATH
   ```

3. **Install Dependencies** (for local testing)
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Locally**
   ```bash
   python bot.py
   ```

## Usage

1. Start a conversation with your bot on Telegram
2. Send `/start` to see usage instructions
3. Send a comma-separated list of players, e.g.:
   ```
   Alice, Bob, Charlie, David
   ```
4. The bot will respond with a complete round robin tournament schedule

## Deployment

Deploy to a remote server using Docker:

```bash
make deploy
```

This will:
1. Copy all necessary files to `TARGET_HOST` at `TARGET_PATH`
2. Build and start the Docker container on the remote host

Make sure your `.env` file contains:
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TARGET_HOST`: SSH connection string (e.g., `user@example.com`)
- `TARGET_PATH`: Remote deployment path (e.g., `/opt/roundrobin-bot`)

## Docker

Build and run with Docker Compose:

```bash
docker-compose up -d --build
```

The bot will automatically restart on failure and read configuration from `.env`.

## How It Works

The bot uses the circle method to generate round robin pairings:
- For even numbers of players: n-1 rounds
- For odd numbers of players: n rounds (one player has a bye each round)
- Each player plays every opponent exactly once

## Files

- `bot.py` - Main bot handler with round robin logic
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition
- `docker-compose.yml` - Docker Compose configuration
- `Makefile` - Deployment automation
- `.env.template` - Environment variable template

