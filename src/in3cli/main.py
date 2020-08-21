import click

from in3cli.eth import eth


@click.group()
def cli():
    pass


cli.add_command(eth)
