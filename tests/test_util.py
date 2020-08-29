import json

from in3cli.model import create_node_dict
from in3cli.util import convert_dict_to_json
from in3cli.util import wei_to_gwei

import tests.conftest as tconf


def test_wei_to_gwei():
    assert wei_to_gwei(1000000000000000000) == 1000000000


def test_convert_dict_to_json_works_for_nodes():
    node = tconf.create_test_node()
    node_dict = create_node_dict(node)
    json_dict = convert_dict_to_json(node_dict)
    assert json.loads(json_dict)
