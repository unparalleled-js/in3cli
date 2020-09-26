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
