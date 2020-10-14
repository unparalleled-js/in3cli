from in3cli.enums import Chain
from in3cli.main import cli
from tests.conftest import TEST_BLOCK


def test_show_gas_price(runner, cli_state):
    expected_value = 123456789
    cli_state.client.eth.gas_price.return_value = expected_value
    res = runner.invoke(cli, "eth show-gas-price", obj=cli_state)
    assert res.output == "{} Gwei\n".format(expected_value)


def test_show_block_errors_when_given_both_num_and_hash(runner, cli_state):
    res = runner.invoke(cli, "eth show-block --block-num 123 --hash 456")
    assert (
        res.output
        == "Error: The following arguments cannot be used together: --hash, --block-num.\n"
    )


def test_show_block_uses_given_block_num(runner, cli_state, mock_block):
    cli_state.client.eth.block_by_number.return_value = mock_block
    res = runner.invoke(cli, "eth show-block --block-num 123", obj=cli_state)
    assert_expected_block(res)


def test_show_block_uses_current_block_num(runner, cli_state, mock_block):
    cli_state.client.eth.block_num = 77777777  # Current block num
    cli_state.client.eth.block_by_number.return_value = mock_block
    res = runner.invoke(cli, "eth show-block", obj=cli_state)
    assert_expected_block(res)


def test_show_block_uses_hash(runner, cli_state, mock_block):
    cli_state.client.eth.block_by_hash.return_value = mock_block
    res = runner.invoke(cli, "eth show-block --hash 456", obj=cli_state)
    assert_expected_block(res)


def test_show_balance_uses_given_address(runner, cli_state):
    expected_balance = 1098
    expected_address = "0x999888"

    def side_effect(address, *args, **kwargs):
        if address == expected_address:
            return expected_balance

    cli_state.client.eth.account.balance.side_effect = side_effect
    res = runner.invoke(cli, "eth show-balance -a {}".format(expected_address), obj=cli_state)
    assert str(expected_balance) in res.output


def test_show_balance_when_not_given_address_uses_account_address(runner, cli_state):
    expected_balance = 1098
    expected_address = "0x999888"

    def side_effect(address, *args, **kwargs):
        if address == expected_address:
            return expected_balance

    cli_state.client.eth.account.balance.side_effect = side_effect
    cli_state.account.address = expected_address
    res = runner.invoke(cli, "eth show-balance".format(expected_address), obj=cli_state)
    assert str(expected_balance) in res.output


def test_send_sends_expected_transaction(runner, cli_state):
    value_eth = 0.000123
    expected_value = int(value_eth * 10000000000000000000.0)
    to_address = "0x45666"
    runner.invoke(cli, "eth send -t {} -v {}".format(to_address, value_eth), obj=cli_state)
    tx = cli_state.client.eth.account.send_transaction.call_args[0][1]
    assert tx.value == expected_value
    assert tx.to == to_address


def test_send_when_not_using_mainnet_returns_etherscan_link_with_chain(runner, cli_state):
    value_eth = 0.000123
    to_address = "0x45666"
    tx_address = "0x99999999999"
    cli_state.chain = Chain.KOVAN
    cli_state.client.eth.account.send_transaction.return_value = tx_address
    res = runner.invoke(cli, "eth send -t {} -v {}".format(to_address, value_eth), obj=cli_state)
    expected_url = "https://kovan.etherscan.io/tx/{}".format(tx_address)
    assert expected_url in res.output


def test_send_when_using_mainnet_returns_etherscan_link_without_chain(runner, cli_state):
    value_eth = 0.000123
    to_address = "0x45666"
    tx_address = "0x99999999999"
    cli_state.chain = Chain.MAINNET
    cli_state.client.eth.account.send_transaction.return_value = tx_address
    res = runner.invoke(cli, "eth send -t {} -v {}".format(to_address, value_eth), obj=cli_state)
    expected_url = "https://etherscan.io/tx/{}".format(tx_address)
    assert expected_url in res.output



def assert_expected_block(res):
    assert "Number" in res.output
    assert str(TEST_BLOCK.number) in res.output
    assert "Hash" in res.output
    assert str(TEST_BLOCK.hash) in res.output
    assert "Difficulty" in res.output
    assert str(TEST_BLOCK.difficulty) in res.output
    assert "Size" in res.output
    assert str(TEST_BLOCK.size) in res.output
    assert "Author" in res.output
    assert str(TEST_BLOCK.author) in res.output
