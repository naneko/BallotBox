import logging
import datetime

import discord
import emoji
from discord.ext import commands, tasks

from ..helpers.database import conn
from ..settings import SUGGEST_CHANNEL

log = logging.getLogger(__name__)


class Suggest(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: discord.ext.commands.Bot = bot
        # TODO: Change storage to database
        self.suggestion_updater.start()

    @commands.command()
    async def suggest(self, ctx: commands.context, *, suggestion: str):
        # For some dumb reason, the timer is 24 hours off so jank fix of 3 days instead of 2
        end_date = datetime.datetime.now() + datetime.timedelta(days=2)
        embed = discord.Embed(
            description=suggestion,
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url,
        )
        embed.set_footer(text=f"Voting ends in 2 days")
        channel = self.bot.get_channel(SUGGEST_CHANNEL)
        msg: discord.Message = await channel.send(embed=embed)
        await ctx.message.delete()
        await msg.add_reaction(emoji.emojize(":thumbs_up:"))
        await msg.add_reaction(emoji.emojize(":person_shrugging:"))
        await msg.add_reaction(emoji.emojize(":thumbs_down:"))
        conn.execute(
            "INSERT INTO suggestions VALUES (?, ?, ?, ?)",
            [msg.id, suggestion, ctx.author.id, end_date],
        )
        conn.commit()

    @tasks.loop(seconds=5.0)
    async def suggestion_updater(self):
        i = 0
        suggestions = conn.execute("SELECT * FROM suggestions").fetchall()
        channel = await self.bot.fetch_channel(SUGGEST_CHANNEL)

        log.debug(f"Updating at {datetime.datetime.now()}")

        for msg_id, content, author_id, end_date in suggestions:
            if end_date > datetime.datetime.now() - datetime.timedelta(seconds=30):
                author = await self.bot.fetch_user(author_id)
                msg = await channel.fetch_message(msg_id)
                log.debug(f'Updated "{content}" by {author} which ends at {end_date}')

                if end_date > datetime.datetime.now() + datetime.timedelta(days=1.25):
                    end_msg = "Voting ends in 2 days"
                elif end_date > datetime.datetime.now() + datetime.timedelta(days=0.5):
                    end_msg = "Voting ends in 1 day"
                elif end_date > datetime.datetime.now() + datetime.timedelta(hours=1):
                    end_msg = f"Voting ends in {round((end_date - datetime.datetime.now()).seconds/(60*60))} hours"
                elif end_date > datetime.datetime.now() + datetime.timedelta(minutes=1):
                    end_msg = f"Voting ends in {round((end_date - datetime.datetime.now()).seconds/60)} minutes"
                elif end_date > datetime.datetime.now():
                    end_msg = "Voting ends in 1 minute"
                else:
                    end_msg = None

                yes_count = 0
                no_count = 0

                for reaction in msg.reactions:
                    if type(reaction.emoji) is str:
                        if emoji.demojize(reaction.emoji) == ":thumbs_up:":
                            yes_count = reaction.count - 1
                        elif emoji.demojize(reaction.emoji) == ":thumbs_down:":
                            no_count = reaction.count - 1

                if end_date > datetime.datetime.now():
                    color = discord.Color.blue()
                    title = None
                elif yes_count > no_count:
                    color = discord.Color.green()
                    title = "Passed"
                elif yes_count < no_count:
                    color = discord.Color.red()
                    title = "Failed"
                else:
                    color = discord.Color.orange()
                    title = "Tied (Failed)"

                embed = discord.Embed(
                    title=title,
                    description=content,
                    color=color,
                )
                embed.set_author(
                    name=author,
                    icon_url=author.avatar_url,
                )
                if end_msg is not None:
                    embed.set_footer(text=end_msg)

                if end_date < datetime.datetime.now():
                    await msg.clear_reactions()
                    if yes_count + no_count != 0:
                        embed.add_field(
                            name=f":thumbsup:",
                            value=f"`{round(yes_count/(yes_count + no_count)*100)}%` ({yes_count} votes)",
                        )
                        embed.add_field(
                            name=f":thumbsdown:",
                            value=f"`{round(no_count / (yes_count + no_count) * 100)}%` ({no_count} votes)",
                        )
                    else:
                        embed.set_footer(text="No votes were cast")

                await msg.edit(embed=embed)

                i += 1


def setup(bot: commands.bot):
    log.debug("Suggest module loaded")
    bot.add_cog(Suggest(bot))


def teardown(bot: commands.bot):
    log.debug("Suggest module unloaded")
