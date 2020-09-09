import click
import keyring
from getpass import getpass

from in3cli import __PRODUCT_NAME__
from in3cli.util import get_in3_client
from in3cli.enums import Chain
from in3cli.options import address_option


class In3CliAccount:
    address = None
    network = Chain.MAINNET

    def get_private_key(self):
        return get_secret(self.address)


@click.command()
@address_option
def add(address):
    """Adds an existing wallet to """
    secret = getpass("Wallet secret: ")
    keyring.set_password(__PRODUCT_NAME__, address, secret)
    client = get_in3_client()


def account():
    client = get_in3_client()
    account = client.account


def get_secret(address):
    return keyring.get_password(__PRODUCT_NAME__, address)
