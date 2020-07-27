from collections import Counter
from datetime import datetime
import textwrap
import typing as t

import arrow
import dateutil.parser
from dateutil.relativedelta import relativedelta
import discord
from discord.ext.commands import Cog, Context, command
import humanize

from snek import start_time, LOC
from snek.bot import Snek
from snek.utils import PaginatedEmbed


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
        created_at = datetime.strftime(ctx.guild.created_at, r'%B %d, %Y')

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
            embed.add_field(name='Creation Date', value=datetime.strftime(role.created_at, r'%B %d, %Y'), inline=True)

            await ctx.send(embed=embed)

    @command(name='roles')
    async def role_list(self, ctx: Context) -> None:
        """Returns a list of all roles in the guild."""
        # Sort roles alphabetically and skip @everyone
        roles = sorted(ctx.guild.roles[1:], key=lambda role: role.name)
        role_list = [f'`{role.id}` - {role.mention}' for role in roles]

        embed = PaginatedEmbed.from_lines(
            role_list,
            max_lines=8,
            title=f'Roles ({len(roles)} total)',
            color=discord.Color.blurple()
        )

        await embed.paginate(ctx)

    @command(name='user', aliases=('userinfo', 'member', 'memberinfo'))
    async def user_info(self, ctx: Context, user: t.Optional[t.Union[discord.Member, discord.User, int, str]]) -> None:
        """Returns information about a user."""
        if user is None:
            user = ctx.author

        embed = None
        if isinstance(user, discord.Member):
            embed = await self.create_member_embed(ctx, user)
        elif isinstance(user, (discord.User, int, str)):
            embed = await self.create_user_embed(ctx, user)

        await ctx.send(embed=embed)

    async def create_member_embed(self, ctx: Context, user: discord.Member) -> discord.Embed:
        """Creates an embed containing information about a member of the guild."""
        created_delta = humanize.precisedelta(user.created_at, minimum_unit='days', format=r'%0.0f')
        created_at = datetime.strftime(user.created_at, r'%B %d, %Y')

        activity = ''
        activity_obj = user.activity

        if activity_obj is not None:

            if activity_obj.type is discord.ActivityType.custom:
                if (emoji := activity_obj.emoji) is not None:
                    activity += f'{emoji} '

                activity += activity_obj.name

            elif activity_obj.type is discord.ActivityType.streaming:
                activity = f'Streaming [{activity_obj.name}]({activity_obj.url}) on {activity_obj.platform}'

            elif activity_obj.type is discord.ActivityType.playing:
                activity = f'Playing {activity_obj.name}'

            elif activity_obj.type is discord.ActivityType.listening:
                BAR_LENGTH = 30

                total_length = int((activity_obj.end - activity_obj.start).total_seconds())

                # This is not always 100% accurate
                # If the user skips forward/backwards in the song, this will be incorrect
                # This is the best we can do for now
                duration_played = int((datetime.utcnow() - activity_obj.created_at).total_seconds())

                left = int(BAR_LENGTH * duration_played // total_length)
                right = BAR_LENGTH - left

                activity = (
                    f'<:spotify:736739861674852464> Listening to [{activity_obj.title}]'
                    f'(https://open.spotify.com/track/{activity_obj.track_id})'
                    f' by {", ".join(activity_obj.artists)}\n'
                    f'`{"▬" * left}🔘{"▬" * right}`'
                )

            else:
                # Shouldn't get here, but just in case
                activity = str(activity_obj)

        title = str(user)
        if user.nick:
            title = f'{user.nick} ({title})'

        joined_delta = humanize.precisedelta(user.joined_at, minimum_unit='days', format=r'%0.0f')
        joined_at = datetime.strftime(user.joined_at, r'%B %d, %Y')

        # Skip @everyone
        roles = ', '.join(role.mention for role in user.roles[1:])

        description = ''

        if activity:
            description += f'{activity}\n'

        description += textwrap.dedent(f"""
            **User Information**
            Created: {created_delta} ago ({created_at})
            Profile: {user.mention}
            ID: {user.id}

            **Member Information**
            Joined: {joined_delta} ago ({joined_at})
            Roles: {roles or None}
        """)

        embed = discord.Embed(
            title=title,
            description=description,
            color=user.top_role.color
        )

        embed.set_thumbnail(url=str(user.avatar_url))
        return embed

    async def create_user_embed(self, ctx: Context, user: t.Union[discord.User, int, str]) -> discord.Embed:
        """Creates an embed containing information saved in the database about a user."""
        if isinstance(user, (int, str)):

            if isinstance(user, int):
                user = await self.bot.api_client.get(f'users/{user}')

            else:
                if '#' in user:
                    name, discrim = user.rsplit('#', maxsplit=1)
                    users = await self.bot.api_client.get(
                        'users',
                        params={'name': name, 'discriminator': discrim}
                    )

                else:
                    users = await self.bot.api_client.get(
                        'users',
                        params={'name': user}
                    )

                if not users:
                    raise discord.ext.commands.BadArgument

                user = users[0]

            created = dateutil.parser.isoparse(user['created_at']).replace(tzinfo=None)

            username = f'{user["name"]}#{user["discriminator"]}'

            created_delta = humanize.precisedelta(created, minimum_unit='days', format=r'%0.0f', )
            created_at = datetime.strftime(created, r'%B %d, %Y')
            mention = f'<@{user["id"]}>'
            user_id = user['id']

            avatar_url = user['avatar_url']

        else:
            username = str(user)

            created_delta = humanize.precisedelta(user.created_at, minimum_unit='days', format=r'%0.0f')
            created_at = datetime.strftime(user.created_at, r'%B %d, %Y')
            mention = user.mention
            user_id = user.id

            avatar_url = str(user.avatar_url)

        description = textwrap.dedent(f"""
            **User Information**
            Created: {created_delta} ago ({created_at})
            Profile: {mention}
            ID: {user_id}
        """)

        embed = discord.Embed(
            title=username,
            description=description
        )

        embed.set_thumbnail(url=avatar_url)
        return embed

    @command(name='bot', aliases=('botinfo', 'invite', 'uptime'))
    async def info_bot(self, ctx: Context) -> None:
        """Returns information about this bot."""
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(
            name='Snek',
            url='https://sneknetwork.com',
            icon_url=str(self.bot.user.avatar_url)
        )

        source = 'https://github.com/Snek-Network/snek'
        invite = f'https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot'

        embed.add_field(name='Source Code', value=f'[GitHub Link]({source})')
        embed.add_field(name='Bot Invite', value=f'[Invite Link]({invite})', inline=False)

        difference = relativedelta(start_time - arrow.utcnow())
        uptime = start_time.shift(
            seconds=-difference.seconds,
            minutes=-difference.minutes,
            hours=-difference.hours,
            days=-difference.days
        ).humanize()

        embed.add_field(name='Uptime', value=uptime)
        embed.add_field(name='LoC', value=f'{LOC:,} lines')

        embed.set_thumbnail(url=str(self.bot.user.avatar_url))

        await ctx.send(embed=embed)

    @command(name='site', aliases=('siteinfo', 'dash', 'dashboard'))
    async def site_info(self, ctx: Context) -> None:
        """Returns information about the Snek Site."""
        embed = discord.Embed(color=discord.Color.blurple())
        embed.set_author(
            name='Snek Site',
            url='https://sneknetwork.com',
            icon_url=str(self.bot.user.avatar_url)
        )

        site = 'https://sneknetwork.com'
        source = 'https://github.com/Snek-Network/snek-site'

        embed.add_field(name='Source Code', value=f'[GitHub Link]({source})')
        embed.add_field(name='Snek Site', value=f'[Site Link]({site})', inline=False)

        embed.set_thumbnail(url=str(self.bot.user.avatar_url))

        await ctx.send(embed=embed)


def setup(bot: Snek) -> None:
    """Load the `Information` cog."""
    bot.add_cog(Information(bot))
