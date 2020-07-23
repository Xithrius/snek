from snek.bot import Snek
from snek.exts.core.error_handler import ErrorHandler
from snek.exts.core.help_command import Help


def setup(bot: Snek) -> None:
    """Load the core cogs."""
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(Help(bot))
