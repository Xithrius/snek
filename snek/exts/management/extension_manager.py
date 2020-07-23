import logging
from pkgutil import iter_modules

from discord.ext import commands

log = logging.getLogger(__name__)

UNLOAD_BLACKLIST = {'snek.exts.management'}
EXTENSIONS = frozenset(
    ext.name for ext in iter_modules(('snek/exts',), 'snek.exts.')
)


class ExtensionManager(commands.Cog):
    """Extension management commands."""
