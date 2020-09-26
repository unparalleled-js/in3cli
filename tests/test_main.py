from in3 import NodeList
from in3cli.main import cli

import tests.conftest as tconf


def test_list_nodes_csv_output(mocker, runner, cli_state):
    node_1 = tconf.create_test_node(tconf.TEST_URL_1)
    node_2 = tconf.create_test_node(tconf.TEST_URL_2)
    node_list = NodeList([node_1, node_2], tconf.TEST_ACCOUNT, "reg_id", 999, 14)
    cli_state.client.refresh_node_list = mocker.Mock()
    cli_state.client.refresh_node_list.return_value = node_list
    res = runner.invoke(cli, "list-nodes --format CSV", obj=cli_state)
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
