"""
Example of an extension

Try the hello command in discord.

The bot will also log any messages sent to channels it can see to the console.
"""
import logging

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class Example(commands.Cog):
    """
    An example of an extension
    """

    def __init__(self, bot: commands.bot):
        """
        An example of an extension
        :param bot: The bot object (passed on setup)
        """
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.context, member: discord.Member = None):
        """
        Hello command: responds hello to the person who executes it
        For more information on command commands, arguments, and converters: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
        For troubleshooting commands: https://discordpy.readthedocs.io/en/latest/faq.html?highlight=process_commands#commands-extension
        :param member: Will automatically turn an ID or mention into a member object
        :param ctx: Discord command context
        """
        # Create an embed
        embed = discord.Embed(
            title="The bot is working!",
            description="**Crazy!** In the description of embeds and the value of fields you can put formatting and [links](https://github.com/naneko/KikiBoilerplate)",
            color=discord.Color.green(),
        )
        embed.set_author(
            name=ctx.author,
            url="https://github.com/naneko/KikiBoilerplate",
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(
            name="Isn't this cool?!",
            value=f"{ctx.author.mention} must just be wowed by this command.\n\n*Thanks for the example Kiki!*",
        )
        embed.add_field(
            name="Had trouble getting an invite link?",
            value="Just paste the ID of the bot user (client ID) into [this website](https://discordapi.com/permissions.html) and set your permissions. It will generate the link for you.",
        )
        # Send the message
        await ctx.channel.send(
            f"Hello {member.mention if member else ctx.author.mention}!", embed=embed
        )
        # Delete the original command
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """
        Log messages to the console
        :param msg: Message sent (discord.Message object)
        """
        await self.bot.process_commands(msg)
        log.info(f'New message from {msg.author}: "{msg.content}"')


def setup(bot: commands.bot):
    """
    This runs when the extension is loaded.

    It adds itself as a cog to the bot object, which is passed by load_extension() in bot.py.
    :param bot: The bot object
    """
    log.debug("Example module loaded")
    bot.add_cog(Example(bot))


def teardown(bot: commands.bot):
    """
    This runs when the extension is unloaded
    :param bot: The bot object
    """
    log.debug("Example module unloaded")
