import logging

from discord.ext.commands import Cog

from snek.bot import Snek

log = logging.getLogger(__name__)


class Information(Cog):

    def __init__(self, bot: Snek) -> None:
        self.bot = bot
