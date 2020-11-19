import logging
import sqlite3

import discord
from discord.ext import commands

from .extensions import INIT_EXTENSIONS
from .helpers.database import init_db
from .settings import DEBUG, COMMAND_PREFIX, TOKEN

log = logging.getLogger(__name__)

bot = commands.Bot(command_prefix=COMMAND_PREFIX)

# Load extensions
log.debug("Loading default extensions...")
if DEBUG is True:
    log.info("=== DEBUG MODE ENABLED ===")
    # Add debug-specific code/extensions here

for ext in INIT_EXTENSIONS:
    log.debug(f"Loading {ext}...")
    bot.load_extension(ext)

log.debug("Default extensions loaded.")

# Initialize Database
init_db()


@bot.event
async def on_ready():
    """
    Execute on bot initialization with the Discord API. This may happen more than once.
    """
    log.info(f"Started as {bot.user}")


@bot.command()
@commands.is_owner()
async def reload(ctx: commands.context):
    """
    Reload default extensions (cogs)

    :param ctx: Discord Context
    """
    async with ctx.channel.typing():
        log.info("Reloading Extensions...")

        msg = await ctx.send(
            embed=discord.Embed(
                title="Reloading extensions...", color=discord.Color.orange()
            )
        )

        for extension in INIT_EXTENSIONS:
            from discord.ext.commands import (
                ExtensionNotLoaded,
                ExtensionNotFound,
                ExtensionFailed,
            )

            try:
                bot.reload_extension(extension)
            except (
                ExtensionNotLoaded,
                ExtensionNotFound,
                ExtensionFailed,
            ) as e:
                log.exception(e)
                await ctx.send(
                    embed=discord.Embed(
                        title=f"Module {extension} failed to reload",
                        color=discord.Color.red(),
                    )
                )
            log.debug(f"{extension} reloaded")

        try:
            log.info("Re-initializing database")
            init_db()
        except sqlite3.OperationalError:
            await ctx.send(
                embed=discord.Embed(
                    title=f"Database failed to re-initialize (i.e. upgrade)",
                    color=discord.Color.red(),
                )
            )

        await msg.delete()
        await ctx.send(
            embed=discord.Embed(title="Reload Successful", color=discord.Color.green())
        )
        log.info("Reloading complete.")


bot.run(TOKEN)
