"""
Contains all configuration for bot.

All settings should be loaded from enviroment variables.
For development, create a .env file in the repository root.
"""

import logging
import os

from dotenv import load_dotenv

log = logging.getLogger(__name__)

load_dotenv()
log.debug(".env file loaded")

# Get config from environment variables (returns none if not found)
DEBUG: bool = bool(os.getenv("DEBUG", False))
TOKEN: str = os.getenv("TOKEN")
DATABASE_URI: str = os.getenv("DATABASE_URI")
COMMAND_PREFIX: str = os.getenv("COMMAND_PREFIX", "!")  # Default set to !

SUGGEST_CHANNEL: int = int(os.getenv("SUGGEST_CHANNEL"))

log.debug("Settings loaded")

# Debug Mode Setup
if DEBUG is True:
    # Set Logger Level
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARN)
    logger = logging.getLogger("websockets")
    logger.setLevel(logging.WARN)
    log.info("Debug Mode Enabled")
else:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("discord")
    logger.setLevel(logging.ERROR)
    logger = logging.getLogger("websockets")
    logger.setLevel(logging.ERROR)

log.debug("Logger configured")

# Check for token and exit if not exists
if TOKEN is None:
    log.error("Discord API token not set")
    exit()

# Check for database URI
if DATABASE_URI is None:
    log.warning(
        "Database URI was not set. Set it to 'database.db' in the directory root of the bot."
    )
    DATABASE_URI = "database.db"
