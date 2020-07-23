import logging
from pkgutil import iter_modules

from discord.ext import commands
from discord.ext.commands import Context

log = logging.getLogger(__name__)

UNLOAD_BLACKLIST = {'snek.exts.management'}
EXTENSIONS = frozenset(
    ext.name for ext in iter_modules(('snek/exts',), 'snek.exts.')
)


class Extension(commands.Converter):
    """
    Ensure the extension exists and return the full extension path.

    The `*` symbol represents all extensions.
    """

    async def convert(self, ctx: Context, argument: str) -> str:
        """Ensure the extension exists and return the full extension path."""
        if argument == '*':
            return argument

        argument = argument.lower()

        if '.' not in argument:
            argument = f'snek.exts.{argument}'

        if argument in EXTENSIONS:
            return argument

        raise commands.BadArgument(f'❌ Could not find the extension `{argument}`.')


class ExtensionManager(commands.Cog):
    """Extension management commands."""
