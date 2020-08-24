import click
import in3.exception as in3err
import time

import in3cli.util as util
import in3cli.model as model
from in3cli.options import hash_option
from in3cli.options import block_num_option
from in3cli.options import format_option
from in3cli.error import In3CliArgumentError


def _get_client():
    return util.get_in3_client().eth


@click.command()
def show_gas_price():
    """Prints the current gas price."""
    client = _get_client()
    price = client.gas_price()
    click.echo("{} GWei".format(price))


@click.command()
@hash_option
@block_num_option
@format_option
def show_block(hash, block_num, format):
    """Prints a block. If not given any args, will print the latest block."""
    client = _get_client()
    _handle_hash_and_block_num_incompat(hash, block_num)

    if hash is not None:
        block = client.block_by_hash(hash)
    else:
        block_num = block_num or client.block_number()
        block = _get_block_by_num(client, block_num)
    block_dict = model.create_block_dict(block)
    _output_obj(block_dict, format)


@click.command()
@hash_option
@block_num_option
def list_transactions(hash, block_num):
    client = _get_client()
    _handle_hash_and_block_num_incompat(hash, block_num)
    if hash is not None:
        block = client.block_by_hash(hash)
    else:
        block_num = block_num or client.block_number()
        block = _get_block_by_num(client, block_num)
    util.print_list(block.transactions)


# Does not work that great for newer transaction
@click.command()
@hash_option
def show_transaction(hash):
    """Prints the transaction for the given hash."""
    client = _get_client()
    transaction = client.transaction_by_hash(hash)
    trans_dict = model.create_transaction_dict(transaction)
    _output_obj(trans_dict, model.FormatOptions.DEFAULT)


def _handle_hash_and_block_num_incompat(hash, block_num):
    if hash is not None and block_num is not None:
        raise In3CliArgumentError(["--hash", "--block-num"])


def _get_block_by_num(client, block_num):
    """Fixes issue where current block num is not yet available in API."""
    block = None
    while block is None:
        try:
            block = client.block_by_number(block_num)
        except in3err.ClientException:
            time.sleep(1)
            continue
    return block


def _output_obj(obj, format_choice):
    if format_choice == model.FormatOptions.DEFAULT:
        util.print_dict(obj)
    elif format_choice == model.FormatOptions.JSON:
        util.print_dict_as_json(obj)


@click.group()
def eth():
    pass


eth.add_command(show_gas_price)
eth.add_command(show_block)
eth.add_command(list_transactions)
eth.add_command(show_transaction)
