import click

from in3cli.account import get_account
from in3cli.client import CliClient
from in3cli.enums import Chain
from in3cli.error import In3CliError
from in3cli.output_formats import OutputFormat

yes_option = click.option(
    "-y",
    "--assume-yes",
    is_flag=True,
    expose_value=False,
    callback=lambda ctx, param, value: ctx.obj.set_assume_yes(value),
    help='Assume "yes" as the answer to all prompts and run non-interactively.',
)
hash_option = click.option("--hash", "-h", help="A block hash.")
hash_arg = click.argument("hash")
block_num_option = click.option("--block-num", "-b", help="A block number.")
format_option = click.option(
    "--format",
    "-f",
    type=click.Choice(OutputFormat.choices(), case_sensitive=False),
    help="The format which to display the output.",
    default=OutputFormat.TABLE,
)
address_option = click.option("--address", "-a", help="An Ethereum address.")


class CliState:
    def __init__(self):
        try:
            self._account = get_account()
        except In3CliError:
            self._account = None
        self._client = None
        self.search_filters = []
        self.assume_yes = False
        self._chain = self._account.chain

    def __call__(self, *args, **kwargs):
        return self.client

    @property
    def chain(self):
        return self._chain

    @chain.setter
    def chain(self, value):
        if value and isinstance(value, str):
            self._chain = value.lower()
            self._client = None

    @property
    def account(self):
        if self._account is None:
            self._account = get_account()
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def client(self):
        if self._client is None:
            self._client = CliClient(self._account, self.chain)
        return self._client

    def set_assume_yes(self, param):
        self.assume_yes = param


def set_account(ctx, param, value):
    """Sets the account on the global state object when --account <name> is passed to commands
    decorated with @global_options."""
    if value:
        ctx.ensure_object(CliState).account = get_account(value)


def account_option(hidden=False):
    return click.option(
        "--account",
        expose_value=False,
        callback=set_account,
        hidden=hidden,
        help="The name of the In3 Cli account to use when executing this command.",
    )


def _set_chain(ctx, chain):
    if chain and ctx.obj:
        ctx.obj.chain = chain


chain_option = click.option(
    "--chain",
    "-c",
    expose_value=False,
    type=click.Choice(Chain.options(), case_sensitive=False),
    hidden=False,
    callback=lambda ctx, param, value: _set_chain(ctx, value),
    help="The blockchain network to use.",
)


pass_state = click.make_pass_decorator(CliState, ensure=True)


def client_options(hidden=False):
    def decorator(f):
        f = account_option(hidden)(f)
        f = chain_option(f)
        f = pass_state(f)
        return f

    return decorator


def incompatible_with(incompatible_opts):
    if isinstance(incompatible_opts, str):
        incompatible_opts = [incompatible_opts]

    class IncompatibleOption(click.Option):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def handle_parse_result(self, ctx, opts, args):
            # if None it means we're in autocomplete mode and don't want to validate
            if ctx.obj is not None:
                found_incompatible = ", ".join(
                    [
                        "--{}".format(opt.replace("_", "-"))
                        for opt in opts
                        if opt in incompatible_opts
                    ]
                )
                if self.name in opts and found_incompatible:
                    name = self.name.replace("_", "-")
                    raise click.BadOptionUsage(
                        option_name=self.name,
                        message="--{} can't be used with: {}".format(name, found_incompatible),
                    )
            return super().handle_parse_result(ctx, opts, args)

    return IncompatibleOption
