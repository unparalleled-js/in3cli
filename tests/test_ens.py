import pytest
from in3cli.error import EnsDomainNameFormatError
from in3cli.main import cli

from tests.conftest import TEST_ADDRESS

TEST_DOMAIN_NAME = "test.eth"


@pytest.fixture
def mock_main_in3_client(mocker, in3_mock):
    mock = mocker.patch("in3cli.ens.get_in3_client")
    mock.return_value = in3_mock
    return in3_mock


def test_hash_returns_expected_address(mocker, runner, mock_main_in3_client):
    mock_main_in3_client.ens_namehash = mocker.MagicMock()
    mock_main_in3_client.ens_namehash.return_value = TEST_ADDRESS
    res = runner.invoke(cli, "ens hash -n {}".format(TEST_DOMAIN_NAME))
    assert TEST_ADDRESS in res.output


def test_hash_prints_error_when_not_given_top_level_domain(
    mocker, runner, mock_main_in3_client
):
    err_text = "Name must end with .eth"

    def side_effect(*args, **kwargs):
        raise AssertionError(err_text)

    mock_main_in3_client.ens_namehash = mocker.MagicMock()
    mock_main_in3_client.ens_namehash.side_effect = side_effect
    res = runner.invoke(cli, "ens hash -n {}".format(TEST_DOMAIN_NAME))
    assert str(EnsDomainNameFormatError()) in res.output


def test_resolve_returns_expected_address(mocker, runner, mock_main_in3_client):
    mock_main_in3_client.ens_address = mocker.MagicMock()
    mock_main_in3_client.ens_address.return_value = TEST_ADDRESS
    res = runner.invoke(cli, "ens resolve -n {}".format(TEST_DOMAIN_NAME))
    assert TEST_ADDRESS in res.output


def test_resolve_prints_error_when_not_given_top_level_domain(
    mocker, runner, mock_main_in3_client
):
    err_text = "Name must end with .eth"

    def side_effect(*args, **kwargs):
        raise AssertionError(err_text)

    mock_main_in3_client.ens_address = mocker.MagicMock()
    mock_main_in3_client.ens_address.side_effect = side_effect
    res = runner.invoke(cli, "ens resolve -n {}".format(TEST_DOMAIN_NAME))
    assert str(EnsDomainNameFormatError()) in res.output


def test_owner_returns_expected_address(mocker, runner, mock_main_in3_client):
    mock_main_in3_client.ens_owner = mocker.MagicMock()
    mock_main_in3_client.ens_owner.return_value = TEST_ADDRESS
    res = runner.invoke(cli, "ens whois -n {}".format(TEST_DOMAIN_NAME))
    assert TEST_ADDRESS in res.output


def test_owner_prints_error_when_not_given_top_level_domain(
    mocker, runner, mock_main_in3_client
):
    err_text = "Name must end with .eth"

    def side_effect(*args, **kwargs):
        raise AssertionError(err_text)

    mock_main_in3_client.ens_owner = mocker.MagicMock()
    mock_main_in3_client.ens_owner.side_effect = side_effect
    res = runner.invoke(cli, "ens whois -n {}".format(TEST_DOMAIN_NAME))
    assert str(EnsDomainNameFormatError()) in res.output
