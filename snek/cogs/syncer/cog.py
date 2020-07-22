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
            self.bot.api_client.put(f'guilds/{guild.id}', json=payload)

        except ResponseCodeError as err:
            if err.response.status != 404:
                raise

            # If we got a 404, that means the guild is new.
            await self.bot.api_client.post('guilds/', json=payload)

        # TODO: Add roles and users on guild join.


def setup(self, bot: Snek) -> None:
    """Load the `Syncer` Cog."""
    bot.add_cog(Syncer(bot))
