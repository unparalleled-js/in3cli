from collections import OrderedDict

import in3cli.util as util


def _ordered_dict(_dict):
    return OrderedDict(sorted(_dict.items()))


def create_block_dict(block, use_subset):
    """Note that this ignores Logs Bloom and Transactions; use separate commands for that."""
    _dict = {
        "Number": block.number,
        "Hash": block.hash,
        "Difficulty": block.difficulty,
        "Size": block.size,
        "Author": block.author,
    }
    if not use_subset:
        return _ordered_dict(
            dict(
                _dict,
                **{
                    "Parent Hash": block.parentHash,
                    "State Root": block.stateRoot,
                    "Miner": block.miner,
                    "Total Difficulty": block.totalDifficulty,
                    "Extra Date": block.extraData,
                    "Gas Limit": block.gasLimit,
                    "Gas Used": block.gasUsed,
                    "Timestamp": util.convert_timestamp_to_date_str(block.timestamp),
                }
            )
        )
    return _dict


def create_tx_dict(tx):
    return _ordered_dict(
        {
            "Block Hash": tx.blockHash,
            "From": tx.From,
            "Amount": "{} Eth".format(util.wei_to_eth(tx.value)),
            "To": tx.to,
        }
    )


def create_node_dict(node):
    return _ordered_dict(
        {
            "URL": node.url,
            "Deposit": "{} Gwei".format(util.wei_to_gwei(node.deposit)),
            "Address": node.address.address,
            "Weight": node.weight,
            "Registration Time": "{}".format(
                util.convert_timestamp_to_date_str(node.registerTime)
            ),
        }
    )


def create_resolved_ens_domain_name_dict(hashed_name, address, owner, resolver):
    return _ordered_dict(
        {"Hash": hashed_name, "Address": address, "Owner": owner, "Resolver": resolver}
    )
