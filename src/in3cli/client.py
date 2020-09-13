import in3

from in3cli.enums import Chain


class CliClient(in3.Client):
    def __init__(self, account, chain=None):
        self.account = account
        if account is None:
            ignore_ssl_errors = False
        else:
            chain = chain or account.chain
            ignore_ssl_errors = account.ignore_ssl_errors
        config = in3.ClientConfig(
            transport_ignore_tls=ignore_ssl_errors
        )
        self.chain = chain or Chain.MAINNET
        super().__init__(chain=chain, in3_config=config)

    def validate(self):
        # TODO: Validate address/key (if set)
        return self.account is not None
