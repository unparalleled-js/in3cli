import pytest

from in3 import NodeList
from in3.eth.model import Account
from in3.model import In3Node
from in3cli.main import cli


_TEST_URL_1 = "www.example.com"
_TEST_URL_2 = "www.test.example.com"
_TEST_INDEX = 555
_TEST_DEPOSIT = 10000000
_TEST_PROPS = 100
_TEST_TIMEOUT = 123456789
_TEST_REGISTER_TIME = 987654321
_TEST_WEIGHT = 1000
_TEST_ACCOUNT = Account("0x123", 0, None, None)


def _create_test_node(url):
    return In3Node(
        url,
        _TEST_ACCOUNT,
        _TEST_INDEX,
        _TEST_DEPOSIT,
        _TEST_PROPS,
        _TEST_TIMEOUT,
        _TEST_REGISTER_TIME,
        _TEST_WEIGHT,
    )


@pytest.fixture
def mock_main_in3_client(mocker, in3_mock):
    mock = mocker.patch("in3cli.main.util.get_in3_client")
    mock.return_value = in3_mock
    return in3_mock


def test_list_nodes_csv_output(mocker, runner, mock_main_in3_client):
    node_1 = _create_test_node(_TEST_URL_1)
    node_2 = _create_test_node(_TEST_URL_2)
    node_list = NodeList([node_1, node_2], _TEST_ACCOUNT, "reg_id", 999, 14)
    mock_main_in3_client.refresh_node_list = mocker.Mock()
    mock_main_in3_client.refresh_node_list.return_value = node_list
    res = runner.invoke(cli, "list-nodes --format CSV")
    expected_header = "Address,Deposit,Register Time,URL,Weight"
    expected_row = "{},{},{},{},{}".format(
        _TEST_ACCOUNT.address,
        _TEST_DEPOSIT,
        _TEST_REGISTER_TIME,
        _TEST_URL_1,
        _TEST_WEIGHT,
    )
    assert expected_header in res.output
    assert expected_row in res.output
    expected_row = expected_row.replace(_TEST_URL_1, _TEST_URL_2)
    assert expected_row in res.output
