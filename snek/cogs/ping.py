import discord
from discord.ext.commands import Cog, command, Context

from snek.bot import Snek


class Ping(Cog):
    """A simple ping cog."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @command()
    async def ping(self, ctx: Context) -> None:
        """Pong! Returns websocket latency."""
        embed = discord.Embed(
            title="Pong!",
            description=f"**Latency:** {self.bot.ws.latency * 1000:.4f} ms",
            color=discord.Colour.blurple(),
        )
        await ctx.send(embed=embed)


def setup(bot: Snek) -> None:
    """Load the `Ping` cog."""
    bot.add_cog(Ping(bot))
