import click
from in3 import ClientException
from in3cli.error import EnsNameFormatError, EnsNameNotFoundError
from in3cli.options import name_option
from in3cli.util import get_in3_client


@click.command("hash")
@name_option
def get_hash(name):
    """Convert the ENS name to its hashed version."""
    client = get_in3_client()
    address = _run_with_err_handling(name, lambda: client.ens_namehash(name))
    click.echo(address)


@click.command()
@name_option
def resolve(name):
    """Resolve an ENS name to its address."""
    client = get_in3_client()
    name = _run_with_err_handling(name, lambda: client.ens_address(name))
    click.echo(name)


@click.command()
@name_option
def show_owner(name):
    """Print the owner of the given name."""
    client = get_in3_client()
    name = _run_with_err_handling(name, lambda: client.ens_owner(name))
    click.echo(name)


def _run_with_err_handling(name, func):
    try:
        return func()
    except AssertionError as err:
        if "must end with" in str(err):
            raise EnsNameFormatError(name)
        raise
    except ClientException as err:
        if "resolver not registered" in str(err):
            raise EnsNameNotFoundError(name)
        raise


@click.group()
def ens():
    """Commands for resolving ENS domains."""
    pass


ens.add_command(resolve)
ens.add_command(get_hash)
ens.add_command(show_owner)
# TODO: Support registry option
