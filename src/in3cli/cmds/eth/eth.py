import time

import click
import in3.exception as in3err

import in3cli.model as model
import in3cli.util as util
from in3cli.error import In3CliArgumentError
from in3cli.options import block_num_option
from in3cli.options import client_options
from in3cli.options import format_option
from in3cli.options import hash_arg
from in3cli.options import hash_option


@click.command()
@client_options()
def show_gas_price(state):
    """Prints the current gas price."""
    price = state.client.eth.gas_price()
    click.echo("{} Gwei".format(price))


@click.command()
@hash_option
@block_num_option
@format_option
@client_options()
def show_block(state, hash, block_num, format):
    """Prints a block. If not given any args, will print the latest block."""
    client = state.client.eth
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
@client_options()
def list_txs(state, hash, block_num):
    """Prints the transactions for the given block.
    If the block is not specified, uses the latest block number."""
    client = state.client.eth
    _handle_hash_and_block_num_incompat(hash, block_num)
    if hash is not None:
        block = client.block_by_hash(hash)
    else:
        block_num = block_num or client.block_number()
        block = _get_block_by_num(client, block_num)
    util.print_list(block.transactions)


@click.command()
@hash_arg
@client_options()
def show_tx(state, hash):
    """Prints the transaction for the given hash."""
    client = state.client.eth
    transaction = client.transaction_by_hash(hash)
    trans_dict = model.create_tx_dict(transaction)
    _output_obj(trans_dict, model.FormatOptions.TABLE)


def _handle_hash_and_block_num_incompat(hash, block_num):
    if hash is not None and block_num is not None:
        raise In3CliArgumentError(["--hash", "--block-num"])


def _get_block_by_num(client, block_num):
    """Fixes issue where block is not available from initial call."""
    # TODO: Add timeout
    block = None
    while block is None:
        try:
            block = client.block_by_number(block_num)
        except in3err.ClientException:
            time.sleep(1)
            continue
    return block


def _output_obj(obj, format_choice):
    if format_choice == model.FormatOptions.TABLE:
        util.print_dict(obj)
    elif format_choice == model.FormatOptions.JSON:
        util.print_dict_as_json(obj)
    elif format_choice == model.FormatOptions.CSV:
        util.print_dict_as_csv(obj)


@click.group()
def eth():
    """Commands for interacting with Ethereum."""
    pass


eth.add_command(show_gas_price)
eth.add_command(show_block)
eth.add_command(list_txs)
eth.add_command(show_tx)
