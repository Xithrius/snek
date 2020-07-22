import logging

import discord
from discord.ext.commands import Cog

from snek.api import ResponseCodeError
from snek.bot import Snek
from snek.cogs.syncer.syncers import GuildSyncer, RoleSyncer, UserSyncer

log = logging.getLogger(__name__)


class Syncer(Cog):

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

        self.guild_syncer = GuildSyncer(bot)
        self.role_syncer = RoleSyncer(bot)
        self.user_syncer = UserSyncer(bot)

    async def sync(self) -> None:
        """Synchronise the guilds/roles/users with the database."""
        await self.guild_syncer.sync()
        await self.role_syncer.sync()
        await self.user_syncer.sync()

    @Cog.listener()
    async def on_ready(self) -> None:
        """Synchronise on ready."""
        await self.sync()

    @Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Adds the joined guild into the database through the Snek API."""
        payload = {
            'id': guild.id,
            'name': guild.name,
            'icon_url': str(guild.icon_url)
        }

        log.info(f'Joined guild {guild.name} ({guild.id})')

        try:
            await self.bot.api_client.put(f'guilds/{guild.id}', json=payload)

        except ResponseCodeError as err:
            if err.response.status != 404:
                raise

            # If we got a 404, that means the guild is new.
            await self.bot.api_client.post('guilds/', json=payload)

        await self.sync()

    @Cog.listener()
    async def on_guild_update(self, before: discord.Guild, after: discord.Guild) -> None:
        """Adds the updated guild information into the database through the Snek API."""
        attrs = ('name', 'icon_url')

        payload = dict()
        for attr in attrs:
            if getattr(before, attr) != (new_value := getattr(after, attr)):
                payload[attr] = new_value

        if payload:
            log.trace(f'Updated guild {after.name} ({after.id})')
            await self.bot.api_client.patch(f'guilds/{after.id}', json=payload)

    @Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        """Adds the newly created role to the database through the API."""
        log.trace(f'New role {role.name} ({role.id}) created in guild {role.guild.name} ({role.guild.id})')
        await self.bot.api_client.post(
            'roles/',
            json={
                'id': role.id,
                'color': role.color.value,
                'name': role.name,
                'permissions': role.permissions.value,
                'position': role.position,
                'guild': role.guild.id
            }
        )

    @Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role) -> None:
        """Adds the updated role information into the database through the Snek API."""
        attrs = ('name', 'color', 'permissions', 'position')

        payload = dict()
        for attr in attrs:
            if getattr(before, attr) != (new_value := getattr(after, attr)):
                if attr in ('color', 'permissions'):
                    payload[attr] = new_value.value
                else:
                    payload[attr] = new_value

        if payload:
            log.trace(f'Updated role {after.name} ({after.id}) for guild {after.guild.name} ({after.guild.id})')
            await self.bot.api_client.patch(f'roles/{after.id}', json=payload)

    @Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        """Deletes the role from the database when deleted from a guild."""
        log.trace(f'Deleted role {role.name} ({role.id}) from guild {role.guild.name} ({role.guild.id})')
        await self.bot.api_client.delete(f'roles/{role.id}')

    @Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Adds a new user or updates an existing user to the database when a member joins a guild.

        If the joining member is a user that is already know to the database (e.g. a user who
        previously left), it will update the user's information. If the user is not yet known,
        the user is added.
        """
        payload = {
            'id': member.id,
            'name': member.name,
            'discriminator': member.discriminator,
            'avatar_url': str(member.avatar_url),
            'roles': sorted(role.id for role in member.roles),
            'guilds': [guild.id for guild in self.bot.guilds if guild.get_member(member.id) is not None]
        }

        log.trace(f'User {member.name} ({member.id}) joined guild {member.guild.name} ({member.guild.id})')

        try:
            await self.bot.api_client.put(f'users/{member.id}', json=payload)

        except ResponseCodeError as err:
            if err.response.status != 404:
                raise

            # If we got a 404, that means the user is new.
            await self.bot.api_client.post('users/', json=payload)

    @Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        """Update the roles of the member in the database if a change is detected."""
        if before.roles != after.roles:
            log.trace(
                f'Updated roles for user {after.name} ({after.id}) in guild {after.guild.name} ({after.guild.id})'
            )

            await self.bot.api_client.patch(
                f'users/{after.id}',
                json={'roles': sorted(role.id for role in after.roles)}
            )

    @Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Remove guild from the user's data in the database."""
        log.trace(f'User {member.name} ({member.id}) left guild {member.guild} ({member.guild.id})')

        member_info = await self.bot.api_client.get(f'users/{member.id}')

        await self.bot.api_client.patch(
            f'users/{member.id}',
            json={
                'guilds': list(set(member_info['guilds']) - {member.guild.id}),
                'roles': list(set(member_info['roles']) - {role.id for role in member.guild.roles})
            }
        )

    @Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User) -> None:
        """Update the user information in the database if a relevant change is detected."""
        attrs = ('name', 'discriminator', 'avatar_url')

        payload = dict()
        for attr in attrs:
            if getattr(before, attr) != (new_value := getattr(after, attr)):
                if attr == 'avatar_url':
                    payload[attr] = str(new_value)
                else:
                    payload[attr] = new_value

        if payload:
            log.trace(
                f'Updated user info for {after.name} ({after.id})'
            )
            await self.bot.api_client.patch(f'users/{after.id}', json=payload)


def setup(self, bot: Snek) -> None:
    """Load the `Syncer` Cog."""
    bot.add_cog(Syncer(bot))
