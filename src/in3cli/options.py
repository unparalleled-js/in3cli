import click

from in3cli.model import FormatOptions


hash_option = click.option("--hash", help="A block hash.")


block_num_option = click.option("--block-num", help="A block number.")


format_option = click.option(
    "--format",
    type=click.Choice(
        [FormatOptions.DEFAULT, FormatOptions.DEFAULT, FormatOptions.CSV], case_sensitive=False
    ),
    help="Either JSON, CSV, or DEFAULT. DEFAULT just prints line separated values that exist.",
    default=FormatOptions.DEFAULT,
)
