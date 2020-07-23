import logging

from discord.ext.commands import Cog, Context, errors

from snek.api import ResponseCodeError
from snek.bot import Snek

log = logging.getLogger(__name__)


class ErrorHandler(Cog):
    """Handles errors from commands."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: errors.CommandError) -> None:
        """
        Provides command error handling.

        Error handling is deferred to any local error handler, if present. This is done by
        checking for the presence of a `handled` attribute on the error.
        """
        if hasattr(errors, 'handled'):
            log.trace(f'Error from command {ctx.command} was handled locally; ignoring.')
            return

        if isinstance(error, errors.UserInputError):
            await self.handle_user_input_error(ctx, error)

        elif isinstance(error, errors.CheckFailure):
            await self.handle_check_failure(ctx, error)

        elif isinstance(error, errors.CommandOnCooldown):
            await ctx.send(error)

        elif isinstance(error, errors.CommandInvokeError):
            if isinstance(error.original, ResponseCodeError):
                await self.handle_snek_api_error(ctx, error.original)
            else:
                await self.handle_unexpected_error(ctx, error.original)
            return  # Return early to avoid logging

        elif not isinstance(error, errors.DisabledCommand):
            await self.handle_unexpected_error(ctx, error)
            return  # Return early to avoid logging

        log.debug(
            f'Command {ctx.command} invoked by {ctx.message.author} with error {type(error).__name__}: {error}'
        )

    async def handle_user_input_error(self, ctx: Context, error: errors.UserInputError) -> None:
        pass

    async def handle_check_failure(self, ctx: Context, error: errors.CheckFailure) -> None:
        pass

    async def handle_snek_api_error(self, ctx: Context, error: ResponseCodeError) -> None:
        pass

    async def handle_unexpected_error(self, ctx: Context, error: errors.CommandError) -> None:
        pass
