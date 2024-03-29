import logging
import datetime
import time

import discord
import emoji
from discord.ext import commands, tasks

from ..helpers.database import conn
from ..settings import SUGGEST_CHANNEL, DEBUG

log = logging.getLogger(__name__)


class Suggest(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot: discord.ext.commands.Bot = bot
        # TODO: Change storage to database
        self.suggestion_updater.start()

    @commands.command()
    async def suggest(self, ctx: commands.context, *, suggestion: str):
        # For some dumb reason, the timer is 24 hours off so jank fix of 3 days instead of 2
        if DEBUG:
            end_date = datetime.datetime.now() + datetime.timedelta(days=0.5)
        else:
            end_date = datetime.datetime.now() + datetime.timedelta(days=2)
        embed = discord.Embed(
            description=suggestion,
            color=discord.Color.blue(),
        )
        embed.set_author(
            name=ctx.author,
            icon_url=ctx.author.avatar_url,
        )
        embed.add_field(name="Cast your votes now using the reactions below!", value=f"Voting ends <t:{int(time.mktime(end_date.timetuple()))}:R>")
        channel = self.bot.get_channel(SUGGEST_CHANNEL)
        msg: discord.Message = await channel.send(embed=embed)
        await ctx.message.delete()
        await msg.add_reaction(emoji.emojize(":thumbs_up:"))
        await msg.add_reaction(emoji.emojize(":person_shrugging:"))
        await msg.add_reaction(emoji.emojize(":thumbs_down:"))
        conn.execute(
            "INSERT INTO suggestions VALUES (?, ?, ?, ?, null, null)",
            [msg.id, suggestion, ctx.author.id, end_date],
        )
        conn.commit()

    @tasks.loop(hours=24.0)
    async def auto_refresh(self):
        suggestions = conn.execute("SELECT * FROM suggestions").fetchall()
        log.info(f"[AUTO] Refreshing at {datetime.datetime.now()}")
        await self.refresh_helper(suggestions)

    @tasks.loop(seconds=5.0 if DEBUG else 30.0)
    async def suggestion_updater(self):
        suggestions = conn.execute("SELECT * FROM suggestions WHERE yes_votes IS null AND no_votes IS null").fetchall()
        log.debug(f"[AUTO] Updating at {datetime.datetime.now()}")
        await self.refresh_helper(suggestions)

    @commands.command()
    @commands.is_owner()
    async def refresh(self, ctx):
        async with ctx.typing():
            suggestions = conn.execute("SELECT * FROM suggestions").fetchall()

            log.info(f"[FORCED] Refreshing at {datetime.datetime.now()}")

            await self.refresh_helper(suggestions)
        
        await ctx.message.delete()
        await ctx.send("Done", delete_after=5)

    
    async def refresh_helper(self, suggestions):
        i = 0
        channel = await self.bot.fetch_channel(SUGGEST_CHANNEL)

        for msg_id, content, author_id, end_date, yes_count, no_count in suggestions:
            try:
                author = await self.bot.fetch_user(author_id)
            except discord.errors.NotFound:
                author = None
            try:
                msg = await channel.fetch_message(msg_id)
            except discord.errors.NotFound:
                log.error(
                    f'Failed to update "{content}" by {author_id} in message {msg_id} which ends at {end_date}. Closing vote to avoid further errors.')
                conn.execute("UPDATE suggestions SET yes_votes = ?, no_votes = ? WHERE msg = ?",
                                [yes_count or 0, no_count or 0, msg_id])
                conn.commit()
                continue
            log.info(f'Updated "{content}" by {author} which ends at {end_date}')

            end_msg = f"Voting ends <t:{int(time.mktime(end_date.timetuple()))}:R>"

            if yes_count is None or no_count is None:
                yes_count = 0
                no_count = 0

                if end_date < datetime.datetime.now():
                    end_msg = None
                    for reaction in msg.reactions:
                        if type(reaction.emoji) is str:
                            if emoji.demojize(reaction.emoji) == ":thumbs_up:":
                                yes_count = reaction.count - 1
                            elif emoji.demojize(reaction.emoji) == ":thumbs_down:":
                                no_count = reaction.count - 1
                    conn.execute("UPDATE suggestions SET yes_votes = ?, no_votes = ? WHERE msg = ?",
                                    [yes_count, no_count, msg_id])
                    conn.commit()

            if end_date < datetime.datetime.now():
                if yes_count > no_count:
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
                if author is not None:
                    embed.set_author(
                        name=author,
                        icon_url=author.avatar_url,
                    )
                else:
                    embed.set_author(
                        name=f"Unknown User ({author_id})"
                    )

                if end_date < datetime.datetime.now():
                    await msg.clear_reactions()
                    if yes_count + no_count != 0:
                        embed.add_field(
                            name=f":thumbsup:",
                            value=f"`{round(yes_count / (yes_count + no_count) * 100)}%` ({yes_count} votes)",
                        )
                        embed.add_field(
                            name=f":thumbsdown:",
                            value=f"`{round(no_count / (yes_count + no_count) * 100)}%` ({no_count} votes)",
                        )
                    else:
                        embed.set_footer(text="No votes were cast")
                        
                elif end_msg is not None:
                    embed.add_field(name="Cast your votes now using the reactions below!", value=f"{end_msg}")

                await msg.edit(embed=embed)

            i += 1


def setup(bot: commands.bot):
    log.debug("Suggest module loaded")
    bot.add_cog(Suggest(bot))


def teardown(bot: commands.bot):
    log.debug("Suggest module unloaded")
