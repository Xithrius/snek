import logging
from pkgutil import iter_modules

from discord.ext import commands
from discord.ext.commands import Context, group

from snek.bot import Snek

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

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

        self.actions = {
            'LOAD': self.bot.load_extension,
            'RELOAD': self.bot.reload_extension,
            'UNLOAD': self.bot.unload_extension
        }

    @group(name='extensions', aliases=('ext', 'exts', 'c', 'cog', 'cogs'), invoke_with_command=True)
    async def extensions_group(self, ctx: Context) -> None:
        """Load, reload, unload, and list extensions."""
        await ctx.send_help(ctx.command)

    @extensions_group.command(name='load', aliases=('l',))
    async def load_command(self, ctx: Context, *extensions: Extension) -> None:
        """
        Load extensions given their name or full path.

        If `*` is given, all unloaded extensions will be loaded.
        """

    @extensions_group.command(name='reload', aliases=('r',))
    async def reload_command(self, ctx: Context, *extensions: Extension) -> None:
        """
        Reload extensions given their name or full path.

        If `*` is given, all loaded extensions will be reloaded.
        """

    @extensions_group.command(name='unload', aliases=('ul',))
    async def unload_command(self, ctx: Context, *extensions: Extension) -> None:
        """
        Unload extensions given their name or full path.

        If `*` is given, all loaded extensions will be unloaded.
        """
