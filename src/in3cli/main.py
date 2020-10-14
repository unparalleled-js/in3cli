import signal
import sys

import click
from in3cli.cmds.account import account
from in3cli.cmds.ens.ens import ens
from in3cli.cmds.eth.eth import eth
from in3cli.error import _ErrorHandlingGroup
from in3cli.model import create_node_dict
from in3cli.options import client_options
from in3cli.options import format_option
from in3cli.output_formats import OutputFormatter


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    click.echo(err=True)
    sys.exit(1)


signal.signal(signal.SIGINT, exit_on_interrupt)


@click.command()
@format_option
@client_options()
def list_nodes(state, format):
    """Lists In3 node information."""
    _format = format.upper()
    node_list = state.client.refresh_node_list()
    node_dicts = [create_node_dict(n) for n in node_list.nodes]
    formatter = OutputFormatter(_format)
    formatter.echo(node_dicts)


_CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 200,
}


@click.group(cls=_ErrorHandlingGroup, context_settings=_CONTEXT_SETTINGS)
@client_options(hidden=True)
def cli(state):
    pass


cli.add_command(eth)
cli.add_command(list_nodes)
cli.add_command(ens)
cli.add_command(account)
