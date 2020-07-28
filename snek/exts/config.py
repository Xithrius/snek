import logging
import typing as t

from discord.ext.commands import Cog, Context, group, RoleConverter

from snek.bot import Snek

log = logging.getLogger(__name__)

CONFIG_KEYS = ('mod_role', 'admin_role', 'command_prefix')


async def convert_config_value(ctx: Context, key: str, value: str) -> t.Any:
    """Converts a config value according to its key."""
    if key not in CONFIG_KEYS:
        raise ValueError('❌ There is no such config key.')

    if key in ('mod_role', 'admin_role'):
        role_converter = RoleConverter()
        return (await role_converter.convert(ctx, value)).id

    return value


class Config(Cog):
    """Commands to manage a guild's config."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @group(name='config', aliases=('conf',), invoke_without_command=True)
    async def config_group(self, ctx: Context) -> None:
        """Get, set, and reset the values in a guild's config."""
        await ctx.send_help(ctx.command)

    @config_group.command(name='set', aliases=('s',))
    async def set_command(self, ctx: Context, key: str, value: str) -> None:
        """Set a value for `key` in for a guild's config."""
        try:
            value = await convert_config_value(ctx, key, value)
        except ValueError as err:
            await ctx.send(str(err))
            return
        else:
            await self.bot.api_client.patch(
                f'guild_configs/{ctx.guild.id}',
                json={key: value}
            )
            await ctx.send(f'✅ Config key `{key}` successfully updated.')

    @config_group.command(name='get', aliases=('g',))
    async def get_command(self, ctx: Context, key: str) -> None:
        """Get the value of `key` from a guild's config."""
        if key not in CONFIG_KEYS:
            await ctx.send('❌ There is no such config key.')
            return

        config = await self.bot.api_client.get(f'guild_configs/{ctx.guild.id}')
        await ctx.send(f'The value of `{key}` is `{config[key]}`.')

    @config_group.command(name='reset', aliases=('r',))
    async def reset_command(self, ctx: Context, key: str) -> None:
        """Reset the value of `key` in a guild's config."""
        if key not in CONFIG_KEYS:
            await ctx.send('❌ There is no such config key.')
            return

        await self.bot.api_client.patch(
            f'guild_configs/{ctx.guild.id}',
            json={key: None}
        )
        await ctx.send(f'✅ Config key `{key}` was sucessfully reset.')

    def cog_check(self, ctx: Context) -> bool:
        return ctx.author.permissions_in(ctx.channel).administrator


def setup(bot: Snek) -> None:
    """Load the `Config` cog."""
    bot.add_cog(Config(bot))
