"""
A neat little tool to create bot status logs in Discord

Use while executing a task to show a little log.

Upon completion you should update it's color and title.
"""
import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class LogMessage:
    """
    Create status logs in Discord
    """

    def __init__(self, ctx: commands.Context, title="Loading..."):
        """
        Create status logs in Discord

        :param ctx: Discord Context
        :param title: Title of the embed
        """
        self.message = None
        self.ctx = ctx
        self.title = title  # Change and update()/log() to modify the title of the embed
        self.color = (
            discord.Color.orange()
        )  # Change and update()/log() to modify the color of the embed
        self.content = (
            []
        )  # Access directly to modify the log content then run update()/log() to see updates

    async def init(self):
        """
        Create the message
        """
        log.debug("Creating LogMessage Instance...")
        await self.send("One sec...")
        log.debug("LogMessage Instance Created.")

    async def send(self, message):
        """
        Replace all log content with a message (will revert to log when log() is called)
        :param message: Content of message
        """
        embed = discord.Embed(title=self.title, description=message, color=self.color)
        if self.message is None:
            self.message = await self.ctx.send(embed=embed)
        else:
            await self.message.edit(embed=embed)

    async def log(self, message):
        """
        Create a log message (will write a new line in the embed)
        :param message: Content of message
        """
        log.debug(f"LogMessage: {message}")
        self.content.append(message)
        await self.send("\n".join(self.content))

    async def update(self):
        """
        Push updates to the title and/or color
        """
        await self.send("\n".join(self.content))
