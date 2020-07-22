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

        # TODO: Add roles and users on guild join.

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


def setup(self, bot: Snek) -> None:
    """Load the `Syncer` Cog."""
    bot.add_cog(Syncer(bot))
