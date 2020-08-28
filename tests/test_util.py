from in3cli.util import wei_to_gwei


def test_wei_to_gwei():
    assert wei_to_gwei(1000000000000000000) == 1000000000
