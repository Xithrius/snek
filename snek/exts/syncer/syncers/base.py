from abc import ABC, abstractmethod
from collections import namedtuple
import logging
import typing as t

from discord.ext.commands import Context

from snek.api import ResponseCodeError
from snek.bot import Snek

log = logging.getLogger(__name__)

Diff = namedtuple('Diff', ('created', 'updated', 'deleted'))


class ObjectSyncerABC(ABC):
    """Base class for synchronising the database with Discord objects in the cache."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the syncer."""

    @abstractmethod
    async def get_diff(self) -> None:
        """Return the difference between the cache and the database."""

    @abstractmethod
    async def sync_diff(self, diff: Diff) -> None:
        """Perform the API calls for synchronisation."""

    async def sync(self, ctx: t.Optional[Context] = None) -> None:
        """Perform the synchronisation."""
        log.info(f'Starting the {self.name} syncer..')

        msg = mention = ''
        if ctx:
            msg = await ctx.send(f'📊 Synchronising {self.name}s..')
            mention = ctx.author.mention

        try:
            await self.sync_diff(await self.get_diff())
        except ResponseCodeError as err:
            log.exception(f'{self.name.capitalize()} syncer failed!')

            results = f'Status {err.status}\n```{err.response_json or "See log output for details."}```'
            status = f'❌ {mention} {self.name.capitalize()} synchronisation failed: {results}'

        else:
            log.info(f'The {self.name} syncer is finished.')
            status = f'✅ Synchronisation of {self.name}s is complete.'

        if msg:
            await msg.edit(content=status)
