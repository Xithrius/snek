from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
import typing as t

import discord
from discord.ext.commands import Cog, Context, command

from snek.bot import Snek


class Infraction(Enum):
    BAN = auto()
    KICK = auto()
    MUTE = auto()
    WATCH = auto()
    FORCE_NICK = auto()
    WARNING = auto()
    NOTE = auto()


InfractionPayloadDict = t.Dict[str, t.Union[str, None, datetime, discord.Member, discord.User, Infraction]]


@dataclass
class InfractionPayload:
    type: Infraction
    reason: t.Optional[str]
    expires_at: t.Optional[datetime]
    user: t.Union[discord.Member, discord.User]
    actor: t.Union[discord.Member, discord.User]

    def to_dict(self) -> InfractionPayloadDict:
        return {
            'type': self.type.name,
            'reason': self.reason,
            'expires_at': self.expires_at.isoformat(),
            'user': self.user.id,
            'actor': self.actor.id
        }


class Infractions(Cog):
    """
    Commands for moderators+ to ban, mute, kick, watch,
    force nick, warn, and note offending members.
    """

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    def apply_infraction(self, ctx: Context, payload: InfractionPayload) -> None:
        """Applies an infraction to an offending member."""

    def pardon_infraction(self, ctx: Context, infr_type: Infraction, user):
        """Pardons an infraction from a user."""

    @command(name='ban')
    def apply_ban(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: t.Optional[str]) -> None:
        """Bans an offending member of a guild."""

    @command(name='mute')
    def apply_mute(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: t.Optional[str]) -> None:
        """Mutes an offending member of a guild."""

    @command(name='kick')
    def apply_kick(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: t.Optional[str]) -> None:
        """Kicks an offending member of a guild."""

    @command(name='watchdog', aliases=('watch',))
    def apply_watch(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: t.Optional[str]) -> None:
        """Watches and relays messages of an offending member of a guild."""

    @command(name='forcenick', aliases=('nick',))
    def apply_nick(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: t.Optional[str]) -> None:
        """Forces a nickanme on an offending member of a guild."""

    @command(name='warn')
    def apply_warn(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: str) -> None:
        """Warns an offending member of a guild."""

    @command(name='note')
    def apply_note(self, ctx: Context, user: t.Union[discord.Member, discord.User], reason: str) -> None:
        """Keeps a note on an offending member of a guild."""

    @command(aliases=('unban',))
    def pardon_ban(self, ctx: Context, user: discord.User, reason: t.Optional[str]) -> None:
        """Pardons a ban."""

    @command(aliases=('unmute',))
    def pardon_mute(self, ctx: Context, user: discord.User, reason: t.Optional[str]) -> None:
        """Pardons a mute."""

    @command(aliases=('unwatch',))
    def pardon_watch(self, ctx: Context, user: discord.User, reason: t.Optional[str]) -> None:
        """Pardons a watch."""

    @command(aliases=('unnick',))
    def pardon_nick(self, ctx: Context, user: discord.User, reason: t.Optional[str]) -> None:
        """Pardons a forced nickname."""
