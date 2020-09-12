import click
from in3 import ClientException

from in3cli.cmds.ens.options import name_arg
from in3cli.error import EnsNameFormatError, EnsNameNotFoundError
from in3cli.options import client_options


@click.command("hash")
@name_arg
@client_options()
def get_hash(state, name):
    """Convert the ENS name to its hashed version."""
    name = str(name)
    address = _run_with_err_handling(name, lambda: state.client.ens_namehash(name))
    click.echo(address)


@click.command()
@name_arg
@client_options()
def resolve(state, name):
    """Resolve an ENS name to its address."""
    name = str(name)
    name = _run_with_err_handling(name, lambda: state.client.ens_address(name))
    click.echo(name)


@click.command()
@name_arg
@client_options()
def show_owner(state, name):
    """Print the owner of the given name."""
    name = str(name)
    name = _run_with_err_handling(name, lambda: state.client.ens_owner(name))
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
    except UnicodeDecodeError:
        pass


@click.group()
def ens():
    """Commands for resolving ENS domains."""
    pass


ens.add_command(resolve)
ens.add_command(get_hash)
ens.add_command(show_owner)
# TODO: Support registry option
