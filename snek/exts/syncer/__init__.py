from snek.bot import Snek
from snek.exts.syncer.cog import Syncer


def setup(bot: Snek) -> None:
    """Load the `Syncer` cog."""
    bot.add_cog(Syncer(bot))
