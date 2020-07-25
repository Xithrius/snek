from collections import Counter
from datetime import datetime
import logging
import textwrap

import discord
from discord.ext.commands import Cog, Context, command
import humanize

from snek.bot import Snek

log = logging.getLogger(__name__)


class Information(Cog):

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @command(name='guild', aliases=('guildinfo', 'server', 'serverinfo'))
    async def guild_info(self, ctx: Context) -> None:
        """Returns information about the guild."""
        embed = discord.Embed()

        embed.color = discord.Color.blurple()
        embed.set_author(name=ctx.guild.name, icon_url=str(ctx.guild.icon_url))
        embed.set_thumbnail(url=str(ctx.guild.icon_url))

        created_delta = humanize.precisedelta(ctx.guild.created_at, minimum_unit='days', format=r'%0.0f')
        created_at = datetime.strftime(ctx.guild.created_at, r'%B %m, %Y')

        members = ctx.guild.member_count
        roles = len(ctx.guild.roles)
        channels = len(ctx.guild.channels)

        statuses = Counter(member.status for member in ctx.guild.members)

        embed.description = textwrap.dedent(f"""
            **Guild Information**
            Created: {created_delta} ago ({created_at})
            ID: {ctx.guild.id}

            **Statistics**
            Members: {members}
            Roles: {roles}
            Channels: {channels}

            **Member Statuses**
            <:status_online:736459107363455016> {statuses[discord.Status.online]}
            <:status_idle:736459129790660689> {statuses[discord.Status.idle]}
            <:status_dnd:736459149600358522> {statuses[discord.Status.dnd]}
            <:status_offline:736459166775771156> {statuses[discord.Status.offline]}
        """)

        await ctx.send(embed=embed)


def setup(bot: Snek) -> None:
    """Load the `Information` cog."""
    bot.add_cog(Information(bot))
