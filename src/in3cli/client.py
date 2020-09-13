import in3

from in3cli.enums import Chain


class ClientWrapper:
    def __init__(self, account):
        self.account = account
        if account is None:
            chain = Chain.MAINNET
            ignore_ssl_errors = False
        else:
            chain = account.chain
            ignore_ssl_errors = account.ignore_ssl_errors
        config = in3.ClientConfig(
            transport_ignore_tls=ignore_ssl_errors
        )
        self.client = in3.Client(chain=chain, in3_config=config)

    @property
    def eth(self):
        return self.client.eth

    def validate(self):
        return self.client is not None
