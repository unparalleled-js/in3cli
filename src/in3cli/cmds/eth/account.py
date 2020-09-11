import click
from getpass import getpass

from in3.exception import PrivateKeyNotFoundException

from in3cli.util import get_in3_client
from in3cli.options import address_option
from in3cli.config import set_secret


def _create_client():
    client = get_in3_client()
    return client.eth.account


@click.command()
@address_option
def add(address):
    """Adds an existing wallet to in3cli."""
    secret = getpass("Private key: ")
    set_secret(address, secret)
    client = _create_client()
    try:
        client.recover(address)
    except PrivateKeyNotFoundException:
        click.echo("Error: Invalid private key.")


@click.command()
def create():
    """Creates a new Ethereum account and saves it in the wallet."""
    client = _create_client()
    account_response = client.create()
    set_secret(str(account_response.address), str(account_response.secret))
    click.echo(account_response.address)


@click.group()
def account():
    """Commands for resolving ENS domains."""
    pass


account.add_command(add)
account.add_command(create)
