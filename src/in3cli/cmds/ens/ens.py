import click
from in3 import ClientException
from in3.exception import EnsDomainFormatException
from in3cli.cmds.ens.options import name_arg
from in3cli.error import EnsNameFormatError
from in3cli.error import EnsNameNotFoundError
from in3cli.model import create_resolved_ens_domain_name_dict
from in3cli.options import client_options
from in3cli.options import format_option
from in3cli.output_formats import OutputFormatter


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
def address(state, name):
    """Resolve an ENS name to its address."""
    name = str(name)
    name = _run_with_err_handling(name, lambda: state.client.ens_address(name))
    click.echo(name)


@click.command()
@name_arg
@client_options()
def resolver(state, name):
    """Resolve an ENS name to the address of its smart contract resolver."""
    name = str(name)
    name = _run_with_err_handling(name, lambda: state.client.ens_resolver(name))
    click.echo(name)


@click.command()
@name_arg
@client_options()
@format_option
def resolve(state, name, format):
    """Resolve an ENS name to its address, owner, hash, and resolver."""
    name = str(name)
    hashed_name = _run_with_err_handling(name, lambda: state.client.ens_namehash(name))
    _address = _run_with_err_handling(name, lambda: state.client.ens_address(name))
    owner = _run_with_err_handling(name, lambda: state.client.ens_owner(name))
    _resolver = _run_with_err_handling(name, lambda: state.client.ens_resolver(name))
    formatter = OutputFormatter(format)
    formatted_resolution = create_resolved_ens_domain_name_dict(
        hashed_name, _address, owner, _resolver
    )
    formatter.echo([formatted_resolution])


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
    except EnsDomainFormatException:
        raise EnsNameFormatError(name)
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


ens.add_command(address)
ens.add_command(get_hash)
ens.add_command(show_owner)
ens.add_command(resolver)
ens.add_command(resolve)
