import pytest
from in3 import NodeList
from in3cli.main import cli

import tests.conftest as tconf


@pytest.fixture
def mock_main_in3_client(mocker, in3_mock):
    mock = mocker.patch("in3cli.main.create_client")
    mock.return_value = in3_mock
    return in3_mock


def test_list_nodes_csv_output(mocker, runner, mock_main_in3_client):
    node_1 = tconf.create_test_node(tconf.TEST_URL_1)
    node_2 = tconf.create_test_node(tconf.TEST_URL_2)
    node_list = NodeList([node_1, node_2], tconf.TEST_ACCOUNT, "reg_id", 999, 14)
    mock_main_in3_client.refresh_node_list = mocker.Mock()
    mock_main_in3_client.refresh_node_list.return_value = node_list
    res = runner.invoke(cli, "list-nodes --format CSV")
    expected_header = "Address,Deposit,Registration Time,URL,Weight"
    expected_row = "{},{},{},{},{}".format(
        tconf.TEST_ACCOUNT.address,
        "{} Gwei".format(str(tconf.TEST_DEPOSIT_GWEI)),
        tconf.TEST_REGISTER_TIME_STR,
        tconf.TEST_URL_1,
        tconf.TEST_WEIGHT,
    )
    assert expected_header in res.output
    assert expected_row in res.output
    expected_row = expected_row.replace(tconf.TEST_URL_1, tconf.TEST_URL_2)
    assert expected_row in res.output
