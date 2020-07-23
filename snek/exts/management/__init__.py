from snek.bot import Snek
from snek.exts.management.extension_manager import ExtensionManager


def setup(bot: Snek) -> None:
    """Load the management cogs."""
    bot.add_cog(ExtensionManager(bot))
