import logging
import typing as t

from discord.ext.commands import Bot, Cog

from snek.api import APIClient

log = logging.getLogger('Snek')


class Snek(Bot):
    """The ultimate multi-purpose Discord bot."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.info('Snek initializing..')

        self.api_client = APIClient(loop=self.loop)

        # Syncer takes care of this
        self.configs: t.Optional[t.Dict[int, str]] = None

    def add_cog(self, cog: Cog) -> None:
        """Adds a cog to the bot and logs the operation."""
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")

    async def close(self) -> None:
        """Close the Discord and API Client connection."""
        await super().close()
        await self.api_client.close()
