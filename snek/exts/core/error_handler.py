import logging
import typing as t

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

    @staticmethod
    def get_help_command(ctx: Context) -> t.Coroutine:
        """Return a `help` command invocation coroutine."""
        if ctx.command:
            return ctx.send_help(ctx.command)

        return ctx.send_help()

    async def handle_user_input_error(self, ctx: Context, error: errors.UserInputError) -> None:
        """
        Send an error message in `ctx.channel` for UserInputError.

        - MissingRequiredArgument: send an error message with arg name and the help command
        - TooManyArguments: send an error message and the help command
        - BadArgument: send an error message and the help command
        - BadUnionArgument: send an error message including the error produced by the last converter
        - ArgumentParsingError: send an error message
        - Other: send an error message and the help command
        """
        help_command = self.get_help_command(ctx)

        if isinstance(error, errors.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: `{error.param.name}`.")
            await help_command

        elif isinstance(error, errors.TooManyArguments):
            await ctx.send("Too many arguments provided.")
            await help_command

        elif isinstance(error, errors.BadArgument):
            await ctx.send("Bad argument: Please double-check your input arguments and try again.")
            await help_command

        elif isinstance(error, errors.BadUnionArgument):
            await ctx.send(f"Bad argument: {error}\n```{error.errors[-1]}```")

        elif isinstance(error, errors.ArgumentParsingError):
            await ctx.send(f"Argument parsing error: {error}")

        else:
            await ctx.send("Something about your input seems off.")
            await help_command

    async def handle_check_failure(self, ctx: Context, error: errors.CheckFailure) -> None:
        """
        Send an error message in `ctx.channel` for certain types of CheckFailure.

        The following errors are handled:
        * BotMissingPermissions
        * BotMissingRole
        * BotMissingAnyRole
        * NoPrivateMessage
        * InWhitelistCheckFailure
        """
        bot_missing_errors = (
            errors.BotMissingPermissions,
            errors.BotMissingRole,
            errors.BotMissingAnyRole
        )

        if isinstance(error, bot_missing_errors):
            await ctx.send(
                "Sorry, it looks like I don't have the permissions or roles I need to do that."
            )

    async def handle_snek_api_error(self, ctx: Context, error: ResponseCodeError) -> None:
        """Send an error message in `ctx.channel` for ResponseCodeError and log it."""
        if error.status == 404:
            log.debug(f"API responded with 404 for command {ctx.command}")
            await ctx.send("There does not seem to be anything matching your query.")

        elif error.status == 400:
            log.debug(f"API responded with 400 for command {ctx.command}: {error.response_json!r}")
            await ctx.send("According to the API, your request is malformed.")

        elif 500 <= error.status < 600:
            log.warning(f"API responded with {error.status} for command {ctx.command}")
            await ctx.send("Sorry, there seems to be an internal issue with the API.")

        else:
            log.warning(f"Unexpected API response for command {ctx.command}: {error.status}")
            await ctx.send(f"Received an unexpected status code from the API: `{error.status}`.")

    async def handle_unexpected_error(self, ctx: Context, error: errors.CommandError) -> None:
        pass
