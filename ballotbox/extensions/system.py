"""
Utility commands to help you manage your bot
"""

import logging
from datetime import timedelta

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class System(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def upgrade(self, ctx: commands.context):
        """
        Pulls an update from GitHub. You can then reload your extensions with the reload command.
        :param ctx: Command context
        """
        from git import Repo

        with ctx.channel.typing():
            log.warning("Upgrading bot from git repo")
            repo = Repo("..")
            o = repo.remotes.origin
            o.pull()

        log.info(f"Pulled update successfully ({repo.heads[0].commit})")

        await ctx.send(
            f"Pulled `{repo.heads[0].commit}` from master branch. Run `;;reload` to complete upgrade."
        )

    @commands.command()
    async def ping(self, ctx: commands.context):
        """
        Pings the bot
        :param ctx: Discord Context
        """
        await ctx.send(
            embed=discord.Embed(title=f"Pong ({timedelta(seconds=self.bot.latency)})")
        )


def setup(bot: commands.bot):
    log.debug("System module loaded")
    bot.add_cog(System(bot))


def teardown(bot: commands.bot):
    log.debug("System module unloaded")
