import in3


def create_client(cli_account):
    # TODO: Connect account if needed (like for send)
    config = in3.ClientConfig(
        transport_ignore_tls=cli_account.ignore_ssl_errors
    )
    return in3.Client(chain=cli_account.chain, in3_config=config)


def validate_account(account):
    # TODO
    return True
