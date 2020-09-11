import difflib
import re

import click
from in3.exception import IN3BaseException

_DIFFLIB_CUT_OFF = 0.6


class In3CliError(click.ClickException):
    """Base in3cli error."""


class In3CliArgumentError(In3CliError):
    """An error to raise when the arguments are invalid."""

    def __init__(self, args):
        args_str = ", ".join(args)
        err_text = "The following arguments cannot be used together: {}.".format(
            args_str
        )
        self.message = err_text


class EnsNameFormatError(In3CliError):
    def __init__(self, name):
        msg = "Missing top-level domain. Try '{}.eth'.".format(name)
        super().__init__(msg)


class EnsNameNotFoundError(In3CliError):
    def __init__(self, name):
        msg = "ENS name '{}' not found.".format(name)
        super().__init__(msg)


class _ErrorHandlingGroup(click.Group):
    """Custom click.Group subclass to add custom exception handling."""

    _original_args = None

    def make_context(self, info_name, args, parent=None, **extra):
        # grab the original command line arguments for logging purposes
        self._original_args = " ".join(args)
        return super().make_context(info_name, args, parent=parent, **extra)

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except click.UsageError as err:
            self._suggest_cmd(err)
        except (In3CliError, IN3BaseException) as err:
            click.echo("Error: {}".format(str(err)), err=True)
        except click.ClickException:
            raise
        except click.exceptions.Exit:
            raise
        except OSError:
            raise

    @staticmethod
    def _suggest_cmd(usage_err):
        """Handles fuzzy suggestion of commands that are close to the bad command entered."""
        if usage_err.message is not None:
            match = re.match("No such command '(.*)'.", usage_err.message)
            if match:
                bad_arg = match.groups()[0]
                available_commands = list(usage_err.ctx.command.commands.keys())
                suggested_commands = difflib.get_close_matches(
                    bad_arg, available_commands, cutoff=_DIFFLIB_CUT_OFF
                )
                if not suggested_commands:
                    raise usage_err
                usage_err.message = "No such command '{}'. Did you mean {}?".format(
                    bad_arg, " or ".join(suggested_commands)
                )
        raise usage_err
