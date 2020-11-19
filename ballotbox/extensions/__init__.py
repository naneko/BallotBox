"""
Extensions loaded by the bot

You can organize this however you want as long as you configure INIT_EXTENSIONS to point to them

Use these to organize your code. The bot is able to hot-reload anything in an extension using the reload command without having to shut the bot down.

For example, you could put all your event listeners in one extension, all your user commands in one, and all your admin commands in one.

See example.py for an example of an extension
"""

# Default Cog Extensions to be loaded
# Module location is relative to bot package
INIT_EXTENSIONS = ["ballotbox.extensions.system", "ballotbox.extensions.suggest"]
