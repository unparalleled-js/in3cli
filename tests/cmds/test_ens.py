from in3 import ClientException
from in3.exception import EnsDomainFormatException

from in3cli.error import EnsNameFormatError
from in3cli.error import EnsNameNotFoundError
from in3cli.main import cli

from tests.conftest import TEST_ADDRESS, TempSideEffect

TEST_DOMAIN_NAME = "test.eth"


def test_hash_returns_expected_address(runner, cli_state):
    cli_state.client.ens_namehash.return_value = TEST_ADDRESS
    res = runner.invoke(cli, "ens hash {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert TEST_ADDRESS in res.output


def test_hash_prints_format_error_when_not_given_top_level_domain(runner, cli_state):
    def side_effect(*args, **kwargs):
        raise EnsDomainFormatException()

    cli_state.client.ens_namehash.side_effect = side_effect
    res = runner.invoke(cli, "ens hash TEST", obj=cli_state)
    assert str(EnsNameFormatError("TEST")) in res.output


def test_hash_prints_not_found_error_when_not_given_top_level_domain(runner, cli_state):
    err_text = "resolver not registered"

    def side_effect(*args, **kwargs):
        raise ClientException(err_text)

    cli_state.client.ens_namehash.side_effect = side_effect
    res = runner.invoke(cli, "ens hash {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert str(EnsNameNotFoundError(TEST_DOMAIN_NAME)) in res.output


def test_address_returns_expected_address(runner, cli_state):
    cli_state.client.ens_address.return_value = TEST_ADDRESS
    res = runner.invoke(cli, "ens address {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert TEST_ADDRESS in res.output


def test_address_prints_error_when_not_given_top_level_domain(runner, cli_state):
    def side_effect(*args, **kwargs):
        raise EnsDomainFormatException()

    cli_state.client.ens_address.side_effect = side_effect
    res = runner.invoke(cli, "ens address {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert str(EnsNameFormatError(TEST_DOMAIN_NAME)) in res.output


def test_address_prints_not_found_error_when_not_given_top_level_domain(
    runner, cli_state
):
    err_text = "resolver not registered"

    def side_effect(*args, **kwargs):
        raise ClientException(err_text)

    cli_state.client.ens_address.side_effect = side_effect
    res = runner.invoke(cli, "ens address {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert str(EnsNameNotFoundError(TEST_DOMAIN_NAME)) in res.output


def test_show_owner_returns_expected_address(runner, cli_state):
    cli_state.client.ens_owner.return_value = TEST_ADDRESS
    res = runner.invoke(
        cli, "ens show-owner {}".format(TEST_DOMAIN_NAME), obj=cli_state
    )
    assert TEST_ADDRESS in res.output


def test_show_owner_prints_error_when_not_given_top_level_domain(runner, cli_state):
    def side_effect(*args, **kwargs):
        raise EnsDomainFormatException()

    cli_state.client.ens_owner.side_effect = side_effect
    res = runner.invoke(
        cli, "ens show-owner {}".format(TEST_DOMAIN_NAME), obj=cli_state
    )
    assert str(EnsNameFormatError(TEST_DOMAIN_NAME)) in res.output


def test_show_owner_prints_not_found_error_when_not_given_top_level_domain(
    runner, cli_state
):
    def side_effect(*args, **kwargs):
        raise ClientException("resolver not registered")

    cli_state.client.ens_owner.side_effect = side_effect
    res = runner.invoke(
        cli, "ens show-owner {}".format(TEST_DOMAIN_NAME), obj=cli_state
    )
    assert str(EnsNameNotFoundError(TEST_DOMAIN_NAME)) in res.output


def test_resolver_returns_expected_address(runner, cli_state):
    cli_state.client.ens_resolver.return_value = TEST_ADDRESS
    res = runner.invoke(cli, "ens resolver {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert TEST_ADDRESS in res.output


def test_resolver_prints_error_when_not_given_top_level_domain(runner, cli_state):
    def side_effect(*args, **kwargs):
        raise EnsDomainFormatException()

    cli_state.client.ens_resolver.side_effect = side_effect
    res = runner.invoke(cli, "ens resolver {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert str(EnsNameFormatError(TEST_DOMAIN_NAME)) in res.output


def test_resolver_prints_not_found_error_when_not_given_top_level_domain(
    runner, cli_state
):
    def side_effect(*args, **kwargs):
        raise ClientException("resolver not registered")

    cli_state.client.ens_resolver.side_effect = side_effect
    res = runner.invoke(cli, "ens resolver {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert str(EnsNameNotFoundError(TEST_DOMAIN_NAME)) in res.output


def test_resolve_returns_expected_values(runner, cli_state):
    cli_state.client.ens_resolver.return_value = "resolver"
    cli_state.client.ens_namehash.return_value = "hash"
    cli_state.client.ens_owner.return_value = "owner"
    cli_state.client.ens_address.return_value = "address"
    res = runner.invoke(cli, "ens resolve {}".format(TEST_DOMAIN_NAME), obj=cli_state)
    assert "resolver" in res.output
    assert "hash" in res.output
    assert "owner" in res.output
    assert "address" in res.output


def test_resolve_prints_error_when_not_given_top_level_domain(runner, cli_state):
    def side_effect(*args, **kwargs):
        raise EnsDomainFormatException()

    def run_test():
        res = runner.invoke(
            cli, "ens resolve {}".format(TEST_DOMAIN_NAME), obj=cli_state
        )
        assert str(EnsNameFormatError(TEST_DOMAIN_NAME)) in res.output

    _run_resolve_error_tests(cli_state, side_effect, run_test)


def test_resolve_prints_not_found_error_when_not_given_top_level_domain(
    runner, cli_state
):
    def side_effect(*args, **kwargs):
        raise ClientException("resolver not registered")

    def run_test():
        res = runner.invoke(
            cli, "ens resolve {}".format(TEST_DOMAIN_NAME), obj=cli_state
        )
        assert str(EnsNameNotFoundError(TEST_DOMAIN_NAME)) in res.output

    _run_resolve_error_tests(cli_state, side_effect, run_test)


def _run_resolve_error_tests(cli_state, side_effect, run_test):
    def success(*args, **kwargs):
        return TEST_ADDRESS

    with TempSideEffect(cli_state.client.ens_resolver, side_effect, success):
        run_test()

    with TempSideEffect(cli_state.client.ens_address, side_effect, success()):
        run_test()

    with TempSideEffect(cli_state.client.ens_owner, side_effect, success()):
        run_test()

    with TempSideEffect(cli_state.client.ens_namehash, side_effect, success()):
        run_test()
