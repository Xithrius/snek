import logging
from pkgutil import iter_modules
import typing as t

import discord
from discord.ext import commands
from discord.ext.commands import Context, group

from snek.bot import Snek
from snek.utils import PaginatedEmbed

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

    @group(name='extensions', aliases=('ext', 'exts', 'c', 'cog', 'cogs'), invoke_without_command=True)
    async def extensions_group(self, ctx: Context) -> None:
        """Load, reload, unload, and list extensions."""
        await ctx.send_help(ctx.command)

    @extensions_group.command(name='load', aliases=('l',))
    async def load_command(self, ctx: Context, *extensions: Extension) -> None:
        """
        Load extensions given their name or full path.

        If `*` is given, all unloaded extensions will be loaded.
        """
        if not extensions:
            await ctx.send_help(ctx.command)
            return

        if '*' in extensions:
            extensions = EXTENSIONS - set(self.bot.extensions)

        msg = self.multi_manage('LOAD', *extensions)
        await ctx.send(msg)

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
        if not extensions:
            await ctx.send_help(ctx.command)
            return

        blacklisted = '\n'.join(UNLOAD_BLACKLIST & set(extensions))

        if blacklisted:
            msg = f'❌ The following extensions cannot be unloaded:\n```{blacklisted}```'
        else:
            if '*' in extensions:
                extensions = set(self.bot.extensions) - UNLOAD_BLACKLIST

            msg = self.multi_manage('UNLOAD', *extensions)

        await ctx.send(msg)

    @extensions_group.command(name='list', aliases=('all',))
    async def list_command(self, ctx: Context) -> None:
        """
        Lists all extensions and their statuses.

        Red indicates that the extension is unloaded.
        Green indicates that the extension is loaded.
        """
        lines = list()

        # Alphabetical order
        for ext in sorted(EXTENSIONS):
            status = '🟢' if ext in self.bot.extensions else '🔴'
            ext_name = ext.rsplit('.', maxsplit=1)[1]
            lines.append(f'{status} {ext_name}')

        embed = PaginatedEmbed.from_lines(lines, max_lines=12)
        embed.color = discord.Color.blurple()
        embed.set_author(name='Extensions List', icon_url=str(self.bot.user.avatar_url))

        log.trace(f'{ctx.author} requested a list of all extensions.')
        await embed.paginate(ctx)

    def multi_manage(self, action: str, *extensions: str) -> str:
        """Apply an action to multiple extensions and return the results."""
        if len(extensions) == 1:
            msg, _ = self.manage(action, extensions[0])
            return msg

        verb = action.lower()
        failures = dict()

        for ext in extensions:
            _, error = self.manage(action, ext)
            if error is not None:
                failures[ext] = error

        msg = f'{"❌" if failures else "✅"} {len(extensions) - len(failures)} / {len(extensions)} extensions {verb}ed.'

        if failures:
            failures = '\n'.join(f'{ext}:\n    {err}' for ext, err in failures.items())
            msg += f'\nFailures:\n```{failures}```'

        log.debug(f'{verb.capitalize()}ed {len(extensions)} extensions.')
        return msg

    def manage(self, action: str, extension: str) -> t.Tuple[str, t.Optional[str]]:
        """
        Apply an action to an extension.

        Returns the status message and any error message.
        """
        verb = action.lower()
        error_msg = None

        try:
            self.actions[action](extension)
        except (commands.ExtensionAlreadyLoaded, commands.ExtensionNotLoaded):
            msg = f'❌ Extension `{extension}` is already {verb}ed.'
            log.debug(msg[2:])

        except Exception as err:
            if hasattr(err, 'original'):
                err = err.original

            log.exception(f'Extension {extension} failed to {verb}.')

            error_msg = f'{type(err).__name__}: {err}'
            msg = f'❌ Failed to {verb} extension `{extension}`:\n```{error_msg}```'
        else:
            msg = f'✅ Extension successfully {verb}ed: `{extension}`.'
            log.debug(msg[2:])

        return msg, error_msg

    async def cog_check(self, ctx: Context) -> bool:
        """Only allow the owner of the bot to invoke the commands in this cog."""
        return await self.bot.is_owner(ctx.author)
