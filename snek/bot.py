import logging

from discord.ext.commands import Bot, Cog

log = logging.getLogger('Snek')


class Snek(Bot):
    """The ultimate multi-purpose Discord bot."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.info('Snek initializing..')

    def add_cog(self, cog: Cog) -> None:
        """Adds a cog to the bot and logs the operation."""
        super().add_cog(cog)
        log.info(f"Cog loaded: {cog.qualified_name}")
