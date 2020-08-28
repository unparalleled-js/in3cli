import click
from in3cli.error import EnsDomainNameFormatError
from in3cli.options import name_option
from in3cli.util import get_in3_client


@click.command("hash")
@name_option
def get_hash(name):
    """Convert the ENS name to its hashed version."""
    client = get_in3_client()
    address = _run_with_domain_format_check(lambda: client.ens_namehash(name))
    click.echo(address)


@click.command()
@name_option
def resolve(name):
    """Resolve an ENS name to its address."""
    client = get_in3_client()
    name = _run_with_domain_format_check(lambda: client.ens_address(name))
    click.echo(name)


@click.command()
@name_option
def show_owner(name):
    """Print the owner of the given name."""
    client = get_in3_client()
    name = _run_with_domain_format_check(lambda: client.ens_owner(name))
    click.echo(name)


def _run_with_domain_format_check(func):
    try:
        return func()
    except AssertionError as err:
        if "must end with" in str(err):
            raise EnsDomainNameFormatError()
        raise


@click.group()
def ens():
    pass


ens.add_command(resolve)
ens.add_command(get_hash)
ens.add_command(show_owner)
# TODO: Support registry option
