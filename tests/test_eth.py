import pytest

from in3cli.main import cli


@pytest.fixture
def in3_eth_mock(mocker, in3_mock):
    eth_mock = mocker.Mock()
    in3_mock.eth = eth_mock

    # Inject into eth module
    mock_getter = mocker.patch("in3cli.eth._get_client")
    mock_getter.return_value = eth_mock

    return in3_mock


def test_show_gas_price(runner, in3_eth_mock):
    expected_value = 123456789
    in3_eth_mock.eth.gas_price.return_value = expected_value
    res = runner.invoke(cli, "eth show-gas-price")
    assert res.output == "{} GWei\n".format(expected_value)


def test_show_block_errors_when_given_both_num_and_hash(runner, in3_eth_mock):
    res = runner.invoke(cli, "eth show-block --block-num 123 --hash 456")
    assert res.output == "Error: The following arguments cannot be used together: --hash, --block-num.\n"


def test_show_block_uses_given_block_num(runner, in3_eth_mock, mock_block):
    in3_eth_mock.eth.block_by_number.return_value = mock_block
    res = runner.invoke(cli, "eth show-block --block-num 123")
    assert_expected_block(res)


def test_show_block_uses_current_block_num(runner, in3_eth_mock, mock_block):
    in3_eth_mock.eth.block_num = 77777777  # Current block num
    in3_eth_mock.eth.block_by_number.return_value = mock_block
    res = runner.invoke(cli, "eth show-block")
    assert_expected_block(res)


def test_show_block_uses_hash(runner, in3_eth_mock, mock_block):
    in3_eth_mock.eth.block_by_hash.return_value = mock_block
    res = runner.invoke(cli, "eth show-block --hash 456")
    assert_expected_block(res)


def assert_expected_block(res):
    assert "Number: 9" in res.output
    assert "Hash: HASH" in res.output
    assert "Parent Hash: PARENT" in res.output
    assert "State Root: state" in res.output
    assert "Miner: miner" in res.output
    assert "Difficulty: 10" in res.output
    assert "Total Difficulty: 100" in res.output
    assert "Extra Date: 2020" in res.output
    assert "Size: 1000" in res.output
    assert "Gas Limit: 1000000000" in res.output
    assert "Gas Used: 1000000000000" in res.output
    assert "Timestamp: 2009-02-13 23:31:29" in res.output
    assert "Uncles: ['UNCLES']" in res.output
    assert "Author: AUTHOR" in res.output