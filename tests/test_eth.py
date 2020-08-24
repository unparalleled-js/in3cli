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
