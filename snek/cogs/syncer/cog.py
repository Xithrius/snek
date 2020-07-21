import logging

from discord.ext.commands import Cog

from snek.bot import Snek
from snek.cogs.syncer.syncers import GuildSyncer

log = logging.getLogger(__name__)


class Syncer(Cog):

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

        self.guild_syncer = GuildSyncer(bot)

    async def sync(self) -> None:
        """Synchronise the guilds/roles/users with the database."""
        await self.guild_syncer.sync()

    @Cog.listener()
    async def on_ready(self) -> None:
        """Synchronise on ready."""
        await self.sync()


def setup(self, bot: Snek) -> None:
    """Load the `Syncer` Cog."""
    bot.add_cog(Syncer(bot))
