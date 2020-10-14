import in3


class CliClient(in3.Client):
    def __init__(self, account, chain=None):
        self.account = account
        if account is None:
            ignore_ssl_errors = False
        else:
            chain = chain or account.chain
            ignore_ssl_errors = account.ignore_ssl_errors
        config = in3.ClientConfig(transport_ignore_tls=ignore_ssl_errors)
        self.chain = chain or account.chain
        super().__init__(chain=chain, in3_config=config)

    @property
    def eth_account(self):
        pkey = self.account.get_private_key()
        recovered_account = self.recover_eth_account(pkey)
        return recovered_account

    def recover_eth_account(self, private_key):
        return self.eth.account.recover(private_key)


def validate(client, private_key):
    client = CliClient(client)
    if client.account is None:
        raise Exception("Missing account.")
    validation_result = client.recover_eth_account(private_key)
    return validation_result is not None
