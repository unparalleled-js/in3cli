import click

from in3cli import util
from in3cli.eth import eth


@click.command()
def list_nodes():
    node_list = util.get_in3_client().refresh_node_list()

    def gen():
        for node in node_list.nodes:
            yield "url: {}\ndeposit: {}\nweight: {}\nregistered in block: {}\n\n".format(
                node.url, node.deposit, node.weight, node.registerTime
            )
    click.echo_via_pager(gen)


@click.group()
def cli():
    pass


cli.add_command(eth)
cli.add_command(list_nodes)
