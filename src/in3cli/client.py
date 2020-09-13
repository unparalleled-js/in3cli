import in3

from in3cli.enums import Chain


class CliClient(in3.Client):
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
        super().__init__(chain=chain, in3_config=config)

    def validate(self):
        return True
