from in3cli.util import convert_timestamp_to_date_str


def create_block_dict(block):
    """Note that this ignores Logs Bloom and Transactions; use separate commands for that."""
    return {
        "Number": block.number,
        "Hash": block.hash,
        "Parent Hash": block.parentHash,
        "State Root": block.stateRoot,
        "Miner": block.miner,
        "Difficulty": block.difficulty,
        "Total Difficulty": block.totalDifficulty,
        "Extra Date": block.extraData,
        "Size": block.size,
        "Gas Limit": block.gasLimit,
        "Gas Used": block.gasUsed,
        "Timestamp": convert_timestamp_to_date_str(block.timestamp),
        "Uncles": block.uncles,
        "Author": block.author,
    }


def create_transaction_dict(transaction):
    return {
        "Block Hash": transaction.blockHash,
        "From": transaction.From,
        "Transaction Index": transaction.transactionIndex,
        "To": transaction.to,
    }


class FormatOptions:
    DEFAULT = "DEFAULT"
    JSON = "JSON"
