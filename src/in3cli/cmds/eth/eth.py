import click
import in3.eth
import in3cli.model as model
from in3cli.enums import BlockNum, Chain
from in3cli.error import In3CliArgumentError
from in3cli.options import block_num_option
from in3cli.options import client_options
from in3cli.options import format_option
from in3cli.options import hash_arg
from in3cli.options import hash_option
from in3cli.options import address_option
from in3cli.output_formats import OutputFormat
from in3cli.output_formats import OutputFormatter
from in3cli.util import run_with_timeout
from in3cli.util import eth_to_wei


to_option = click.option("--to", "-t", help="An Ethereum address to send ether to.", required=True)
value_option = click.option("--value", "-v", help="The value in ether to send.", required=True, type=float)
gas_option = click.option("--gas", "-g", help="The value in wei to put for gas.", type=float)


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
        block_num = _handle_block_num_param(block_num, client)
        block = _get_block_by_num(client, block_num)
    use_subset = format == OutputFormat.TABLE
    block_dict = model.create_block_dict(block, use_subset)
    formatter = OutputFormatter(format)
    formatter.echo([block_dict])


@click.command()
@hash_option
@block_num_option
@client_options()
@format_option
def list_txs(state, hash, block_num, format):
    """Prints the transactions for the given block.
    If the block is not specified, uses the latest block number."""
    client = state.client.eth
    _handle_hash_and_block_num_incompat(hash, block_num)
    if hash is not None:
        block = client.block_by_hash(hash, get_full_block=True)
    else:
        block_num = _handle_block_num_param(block_num, client)
        block = _get_block_by_num(client, block_num)
    formatter = OutputFormatter(format)
    txs = [model.create_tx_dict(tx) for tx in block.transactions]
    formatter.echo(txs)


@click.command()
@hash_arg
@client_options()
@format_option
def show_tx(state, hash, format):
    """Prints the transaction for the given hash."""
    client = state.client.eth
    transaction = client.transaction_by_hash(hash)
    trans_dict = model.create_tx_dict(transaction)
    formatter = OutputFormatter(format)
    formatter.echo([trans_dict])


@click.command()
@address_option
@client_options()
def show_balance(state, address=None):
    """Shows the balance for the given address. If not given address, shows your account balance."""
    client = state.client.eth
    address = address or state.account.address
    balance = client.account.balance(address)
    click.echo(balance)


@click.command()
@to_option
@value_option
@gas_option
@client_options()
def send(state, to, value, gas=None):
    etherscan_link_mask = "https://{}etherscan.io/tx/{}"
    chain = state.chain
    client = state.client.eth.account
    sender = state.client.eth_account
    value = int(eth_to_wei(value))
    tx = in3.eth.NewTransaction(to=to, value=value, gasLimit=gas)
    tx_hash = client.send_transaction(sender, tx)
    chain_prefix = "{}.".format(chain.lower()) if chain != Chain.MAINNET else ""
    click.echo(etherscan_link_mask.format(chain_prefix, tx_hash))


def _handle_block_num_param(param, client):
    if isinstance(param, str):
        if param.isnumeric():
            return int(param)
        options = BlockNum.options()
        if param not in options:
            raise ValueError(
                "'{}' is not a supported block number. Try a numeric value or one of {}.".format(
                    param, options
                )
            )
    elif isinstance(param, int):
        return param
    return client.block_number()


def _handle_hash_and_block_num_incompat(hash, block_num):
    if hash is not None and block_num is not None:
        raise In3CliArgumentError(["--hash", "--block-num"])


def _get_block_by_num(client, block_num):
    """Fixes issue where block is not available from initial call."""
    return run_with_timeout(lambda: client.block_by_number(block_num, get_full_block=True))


@click.group()
def eth():
    """Commands for interacting with Ethereum."""
    pass


eth.add_command(show_gas_price)
eth.add_command(show_block)
eth.add_command(list_txs)
eth.add_command(show_tx)
eth.add_command(show_balance)
eth.add_command(send)
