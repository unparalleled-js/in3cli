import click

from in3cli import util
from in3cli.eth import eth


@click.command()
def show_registry():
    node_list = util.get_in3_client().refresh_node_list()
    click.echo("\nIncubed Registry:")
    click.echo("\ttotal servers: {}".format(node_list.totalServers))
    click.echo("\tlast updated in block: {}".format(node_list.lastBlockNumber))
    click.echo("\tregistry ID: {}".format(node_list.registryId))
    click.echo("\tcontract address: {}".format(node_list.contract))


@click.command()
def show_nodes():
    node_list = util.get_in3_client().refresh_node_list()
    click.echo("\nNodes Registered:\n")
    for node in node_list.nodes:
        click.echo("\turl: {}".format(node.url))
        click.echo("\tdeposit: {}".format(node.deposit))
        click.echo("\tweight: {}".format(node.weight))
        click.echo("\tregistered in block: {}".format(node.registerTime))



@click.group()
def cli():
    pass


cli.add_command(eth)
cli.add_command(show_registry)
cli.add_command(show_nodes)
