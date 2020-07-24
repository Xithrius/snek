import logging

from discord.ext.commands import Cog, Context, group

from snek.bot import Snek

log = logging.getLogger(__name__)


class Config(Cog):
    """Commands to manage a guild's config."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @group(name='config', invoke_without_command=True)
    async def config_group(self, ctx: Context) -> None:
        """Get, set, and reset the values in a guild's config."""
        await ctx.send_help(ctx.command)

    @config_group.command(name='set', aliases=('s',))
    async def set_command(self, ctx: Context, key: str, value: str) -> None:
        """Set a value for `key` in for a guild's config."""

    @config_group.command(name='get', aliases=('g',))
    async def get_command(self, ctx: Context, key: str, value: str) -> None:
        """Get the value of `key` from a guild's config."""

    @config_group.command(name='reset', aliases=('r',))
    async def reset_command(self, ctx: Context, key: str) -> None:
        """Reset the value of `key` in a guild's config."""


def setup(bot: Snek) -> None:
    """Load the `Config` cog."""
    bot.add_cog(Config(bot))
