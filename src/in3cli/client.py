import in3


def get_in3_client(ignore_ssl_errors=False):
    config = in3.ClientConfig(transport_ignore_tls=ignore_ssl_errors)
    return in3.Client(in3_config=config)


def validate_account(account):
    return True
