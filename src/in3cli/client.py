import in3
from in3cli.enums import Chain


def create_client(cli_account):
    if cli_account is None:
        chain = Chain.MAINNET
        ignore_ssl_errors = False
    else:
        chain = cli_account.chain
        ignore_ssl_errors = cli_account.ignore_ssl_errors
    config = in3.ClientConfig(
        transport_ignore_tls=ignore_ssl_errors
    )
    return in3.Client(chain=chain, in3_config=config)


def validate_account(account):
    # TODO
    return True
