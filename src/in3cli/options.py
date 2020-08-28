import click

from in3cli.model import FormatOptions


hash_option = click.option("--hash", "-h", help="A block hash.")


block_num_option = click.option("--block-num", "-b", help="A block number.")


format_option = click.option(
    "--format",
    "-f",
    type=click.Choice(
        [FormatOptions.DEFAULT, FormatOptions.JSON, FormatOptions.CSV],
        case_sensitive=False,
    ),
    help="Either JSON, CSV, or DEFAULT. DEFAULT just prints line separated values that exist.",
    default=FormatOptions.DEFAULT,
)


name_option = click.option("--name", "-n", help="An ENS domain name.")


address_option = click.option("--address", "-a", help="An Ethereum address.")
