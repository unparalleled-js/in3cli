import click


class In3CliError(click.ClickException):
    """Base in3cli error."""


class In3CliArgumentError(In3CliError):
    """An error to raise when the arguments are invalid."""

    def __init__(self, args):
        args_str = ", ".join(args)
        err_text = "The following arguments cannot be used together: {}.".format(args_str)
        self.message = err_text
