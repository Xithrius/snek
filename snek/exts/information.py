from collections import Counter
from datetime import datetime
import logging
import textwrap
import typing as t

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

    @command(name='role', aliases=('roleinfo',))
    async def role_info(self, ctx: Context, *roles: t.Union[discord.Role, str]) -> None:
        """Returns information about role(s)."""
        parsed_roles = list()
        failed_roles = list()

        for role in roles:
            if isinstance(role, discord.Role):
                parsed_roles.append(role)
                continue

            role_obj = discord.utils.find(lambda r: r.name.lower() == role.lower(), ctx.guild.roles)

            if role_obj:
                parsed_roles.append(role_obj)
                continue

            failed_roles.append(role)

        if failed_roles:
            await ctx.send(f'❌ Could not find these roles: {", ".join(failed_roles)}')

        for role in parsed_roles:
            embed = discord.Embed(
                title=f'{role.name} Role',
                color=role.color
            )

            embed.add_field(name='ID', value=role.id, inline=True)
            embed.add_field(name='Color (RGB)', value=f'#{role.color.value:0>6x}', inline=True)
            embed.add_field(name='Permissions Code', value=role.permissions.value, inline=True)
            embed.add_field(name='Member Count', value=len(role.members), inline=True)
            embed.add_field(name='Position', value=role.position, inline=True)
            embed.add_field(name='Creation Date', value=datetime.strftime(role.created_at, r'%B %m, %Y'), inline=True)

            await ctx.send(embed=embed)


def setup(bot: Snek) -> None:
    """Load the `Information` cog."""
    bot.add_cog(Information(bot))
