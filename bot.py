#!/usr/bin/env python3
"""
Telegram bot for generating round robin tournament pairings.
"""
import os
import logging
from typing import List, Tuple
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

# Persistent keyboard with Start button
START_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton("🔄 Start New Tournament")]],
    resize_keyboard=True,
    one_time_keyboard=False
)


def generate_round_robin(players: List[str]) -> Tuple[List[List[Tuple[str, str]]], List[str]]:
    """
    Generate round robin tournament pairings using the circle method.

    Args:
        players: List of player names

    Returns:
        Tuple of (rounds, byes_per_round) where:
        - rounds: List of rounds, each round is a list of (player1, player2) tuples
        - byes_per_round: List of players who have a bye in each round (empty string if none)
    """
    n = len(players)
    if n < 2:
        return [], []

    # If odd number of players, add a "BYE" player
    if n % 2 == 1:
        players_list = players + ["BYE"]
    else:
        players_list = players

    num_players = len(players_list)
    rounds = []
    byes_per_round = []

    # Generate num_players - 1 rounds
    for round_num in range(num_players - 1):
        round_pairings = []
        bye_player = None

        # Pair players: first with last, second with second-to-last, etc.
        for i in range(num_players // 2):
            player1 = players_list[i]
            player2 = players_list[num_players - 1 - i]

            # Only add pairing if neither is BYE
            if player1 != "BYE" and player2 != "BYE":
                round_pairings.append((player1, player2))
            elif player1 != "BYE":
                # player2 is BYE, so player1 has a bye
                bye_player = player1
            elif player2 != "BYE":
                # player1 is BYE, so player2 has a bye
                bye_player = player2

        rounds.append(round_pairings)
        byes_per_round.append(bye_player if bye_player else "")

        # Rotate players: keep first fixed, rotate the rest counter-clockwise
        # [A, B, C, D] -> [A, C, D, B]
        players_list = [players_list[0]] + players_list[2:] + [players_list[1]]

    return rounds, byes_per_round


def format_round_robin_output(players: List[str], rounds: List[List[Tuple[str, str]]], byes_per_round: List[str]) -> str:
    """
    Format the round robin tournament as a readable string.

    Args:
        players: List of player names
        rounds: List of rounds with pairings
        byes_per_round: List of players who have a bye in each round

    Returns:
        Formatted string representation
    """
    if not rounds:
        return "❌ Need at least 2 players to generate pairings."

    output = f"🎯 **Round Robin Tournament**\n\n"
    output += f"👥 **Players:** {', '.join(players)}\n"
    output += f"📊 **Total Players:** {len(players)}\n"
    output += f"🔄 **Total Rounds:** {len(rounds)}\n\n"

    if len(players) % 2 == 1:
        output += "ℹ️ *Note: Odd number of players - one player will have a bye each round*\n\n"

    # Display each round
    for round_num, round_pairings in enumerate(rounds, 1):
        output += f"**Round {round_num}:**\n"

        # Display active pairings
        for player1, player2 in round_pairings:
            output += f"  ⚔️ {player1} vs {player2}\n"

        # Display bye if applicable
        if round_num <= len(byes_per_round) and byes_per_round[round_num - 1]:
            output += f"  😴 {byes_per_round[round_num - 1]} (bye)\n"

        output += "\n"

    return output


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    usage_text = """
🤖 **Round Robin Duel Bot**

Welcome! This bot generates round robin tournament pairings.

**Usage:**
Send me a comma-separated list of players, and I'll generate the tournament schedule.

**Example:**
```
Alice, Bob, Charlie, David
```

**Features:**
• Each player plays every opponent exactly once
• If odd number of players, one player gets a bye each round
• All rounds are displayed with pairings

Send me your player list to get started! 🎯
"""
    await update.message.reply_text(
        usage_text,
        parse_mode='Markdown',
        reply_markup=START_KEYBOARD
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages with player lists."""
    message_text = update.message.text.strip()

    # Handle "Start New Tournament" button press
    if message_text == "🔄 Start New Tournament" or message_text == "/start":
        await start(update, context)
        return

    # Parse comma-separated players
    players = [p.strip() for p in message_text.split(',') if p.strip()]

    if len(players) < 2:
        await update.message.reply_text(
            "❌ Please provide at least 2 players separated by commas.\n\n"
            "Example: Alice, Bob, Charlie",
            reply_markup=START_KEYBOARD
        )
        return

    # Remove duplicates while preserving order
    seen = set()
    unique_players = []
    for player in players:
        if player.lower() not in seen:
            seen.add(player.lower())
            unique_players.append(player)

    if len(unique_players) < 2:
        await update.message.reply_text(
            "❌ Please provide at least 2 unique players.",
            reply_markup=START_KEYBOARD
        )
        return

    # Generate round robin pairings
    try:
        rounds, byes_per_round = generate_round_robin(unique_players)
        output = format_round_robin_output(unique_players, rounds, byes_per_round)
        await update.message.reply_text(
            output,
            parse_mode='Markdown',
            reply_markup=START_KEYBOARD
        )
    except Exception as e:
        logger.error(f"Error generating round robin: {e}")
        await update.message.reply_text(
            "❌ An error occurred while generating the tournament schedule. Please try again.",
            reply_markup=START_KEYBOARD
        )


def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

