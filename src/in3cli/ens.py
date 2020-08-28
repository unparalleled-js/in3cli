import click

from in3cli.options import name_option
from in3cli.util import get_in3_client
from in3cli.error import TopLevelDomainNotPresentError


@click.command()
@name_option
def resolve(name):
    client = get_in3_client()
    try:
        name_hash = client.ens_namehash(name)
        click.echo(name_hash)
    except AssertionError as err:
        if "must end with" in str(err):
            raise TopLevelDomainNotPresentError()
        raise


@click.group()
def ens():
    pass


ens.add_command(resolve)
