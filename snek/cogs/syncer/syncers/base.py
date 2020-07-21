from abc import ABC, abstractmethod
from collections import namedtuple

from snek.bot import Snek

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
