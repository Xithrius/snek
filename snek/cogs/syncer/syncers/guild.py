from collections import namedtuple
import logging

from snek.cogs.syncer.syncers.base import Diff, ObjectSyncerABC

log = logging.getLogger(__name__)

Guild = namedtuple('Guild', ('id', 'name', 'icon_url'))


class GuildSyncer(ObjectSyncerABC):
    """Synchronise the database with guilds in the cache."""
    name = 'guild'

    async def get_diff(self) -> Diff:
        """Return the difference between the cache of guilds and the database."""
        log.trace('Getting the diff for guilds..')
        guilds = await self.bot.api_client.get('guilds')

        db_guilds = {Guild(**guild) for guild in guilds}
        cache_guilds = {
            Guild(
                id=guild.id,
                name=guild.name,
                icon_url=str(guild.icon_url)
            )
            for guild in self.bot.guilds
        }

        db_guild_ids = {guild.id for guild in db_guilds}
        cache_guild_ids = {guild.id for guild in cache_guilds}

        new_guild_ids = cache_guild_ids - db_guild_ids
        deleted_guild_ids = db_guilds - cache_guild_ids

        guilds_to_create = {guild for guild in cache_guilds if guild.id in new_guild_ids}
        guilds_to_update = cache_guilds - db_guilds - guilds_to_create
        guilds_to_delete = {guild for guild in db_guilds if guild.id in deleted_guild_ids}

        return Diff(guilds_to_create, guilds_to_update, guilds_to_delete)

    async def sync_diff(self, diff: Diff) -> None:
        """Synchronise the database with the guilds in the cache."""
        log.trace('Syncing created guilds..')
        for guild in diff.created:
            await self.bot.api_client.post('guilds', json=guild._asdict())

        log.trace('Syncing updated guilds..')
        for guild in diff.updated:
            await self.bot.api_client.put(f'guilds/{guild.id}', json=guild._asdict())

        log.trace('Syncing deleted guilds..')
        for guild in diff.deleted:
            await self.bot.api_client.delete(f'guilds/{guild.id}')
