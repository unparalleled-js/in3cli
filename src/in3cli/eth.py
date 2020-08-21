import click
import json

import in3cli.util as util
import in3cli.model as model
from in3cli.options import hash_option
from in3cli.options import block_num_option
from in3cli.error import In3CliArgumentError


def _get_client():
    return util.get_in3_client().eth


@click.command()
def show_gas_price():
    client = _get_client()
    price = client.gas_price()
    click.echo(price)


@click.command()
def show_block_num():
    client = _get_client()
    block_num = client.block_number()
    click.echo(block_num)


@click.command()
@hash_option
@block_num_option
def show_block(hash, block_num):
    """Prints the block to th terminal.  If not given any args, will print the latest block."""
    client = _get_client()
    if hash is not None and block_num is not None:
        raise In3CliArgumentError(["--hash", "--block-num"])

    if hash is not None:
        block = client.block_by_hash(hash)
    else:
        block_num = block_num or client.block_number()
        block = client.block_by_number(block_num)
    block_dict = model.create_block_dict(block)
    util.print_dict(block_dict)


@click.group()
def eth():
    pass


eth.add_command(show_gas_price)
eth.add_command(show_block_num)
eth.add_command(show_block)
