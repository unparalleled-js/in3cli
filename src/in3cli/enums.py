from in3cli.util import get_attribute_keys_from_class


class Chain:
    MAINNET = "mainnet"
    KOVAN = "kovan"
    EVAN = "evan"
    GOERLI = "goerli"
    IPFS = "ipfs"
    EWC = "ewc"

    @staticmethod
    def options():
        return get_attribute_keys_from_class(Chain)


class BlockNum:
    LATEST = "latest"
    EARLIEST = "earliest"
    PENDING = "pending"

    @staticmethod
    def options():
        return get_attribute_keys_from_class(BlockNum)
