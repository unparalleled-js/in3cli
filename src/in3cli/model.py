import in3cli.util as util


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
        "Timestamp": util.convert_timestamp_to_date_str(block.timestamp),
        "Uncles": block.uncles,
        "Author": block.author,
    }


def create_tx_dict(tx):
    return {
        "Block Hash": tx.blockHash,
        "From": tx.From,
        "Transaction Index": tx.transactionIndex,
        "To": tx.to,
    }


def create_node_dict(node):
    return {
        "URL": node.url,
        "Deposit": "{} Gwei".format(util.wei_to_gwei(node.deposit)),
        "Address": node.address.address,
        "Weight": node.weight,
        "Registration Time": "{}".format(
            util.convert_timestamp_to_date_str(node.registerTime)
        ),
    }
