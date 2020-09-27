import pytest

import in3cli.account as cliaccount

from in3cli.enums import Chain
from .conftest import create_mock_account, TEST_ACCOUNT_NAME, TEST_ADDRESS
from .conftest import MockSection
from in3cli import __PRODUCT_NAME__
from in3cli.config import ConfigAccessor
from in3cli.config import NoConfigAccountError
from in3cli.error import In3CliError


@pytest.fixture
def config_accessor(mocker):
    mock = mocker.MagicMock(spec=ConfigAccessor, name="Config Accessor")
    attr = mocker.patch("{}.account.config_accessor".format(__PRODUCT_NAME__), mock)
    return attr


@pytest.fixture
def private_key_setter(mocker):
    return mocker.patch("{}.private_key.set_private_key".format(__PRODUCT_NAME__))


@pytest.fixture
def private_key_getter(mocker):
    return mocker.patch(
        "{}.private_key.get_stored_private_key".format(__PRODUCT_NAME__)
    )


@pytest.fixture
def private_key_deleter(mocker):
    return mocker.patch("in3cli.private_key.delete_private_key")


_TEST_KEY = "test key"


class TestIn3Account:
    def test_get_private_key_when_is_none_returns_private_key_from_getpass(
        self, mocker, private_key_getter
    ):
        private_key_getter.return_value = None
        mock_getpass = mocker.patch(
            "{}.private_key.get_private_key_from_prompt".format(__PRODUCT_NAME__)
        )
        mock_getpass.return_value = _TEST_KEY
        actual = create_mock_account().get_private_key()
        assert actual == _TEST_KEY

    def test_get_private_key_return_private_key_from_private_key_get_private_key(
        self, private_key_getter
    ):
        private_key_getter.return_value = _TEST_KEY
        actual = create_mock_account().get_private_key()
        assert actual == _TEST_KEY

    def test_chain_returns_expected_value(self):
        mock_account = create_mock_account()
        assert mock_account.chain == Chain.MAINNET

    def test_name_returns_expected_value(self):
        mock_account = create_mock_account()
        assert mock_account.name == TEST_ACCOUNT_NAME

    def test_address_returns_expected_value(self):
        mock_account = create_mock_account()
        assert mock_account.address == TEST_ADDRESS

    def test_ignore_ssl_errors_returns_expected_value(self):
        mock_account = create_mock_account()
        assert mock_account.ignore_ssl_errors


def test_get_account_returns_expected_account(config_accessor):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    account = cliaccount.get_account("testaccountname")
    assert account.name == "testaccountname"


def test_get_account_when_config_accessor_raises_cli_error(config_accessor):
    config_accessor.get_account.side_effect = NoConfigAccountError()
    with pytest.raises(In3CliError):
        cliaccount.get_account("testaccountname")


def test_default_account_exists_when_exists_returns_true(config_accessor):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    assert cliaccount.default_account_exists()


def test_default_account_exists_when_not_exists_returns_false(config_accessor):
    mock_section = MockSection(ConfigAccessor.DEFAULT_VALUE, {})
    config_accessor.get_account.return_value = mock_section
    assert not cliaccount.default_account_exists()


def test_validate_default_account_prints_set_default_help_when_no_valid_default_but_another_account_exists(
    capsys, config_accessor
):
    config_accessor.get_account.side_effect = NoConfigAccountError()
    config_accessor.get_all_accounts.return_value = [
        MockSection("thisaccountxists", {})
    ]
    with pytest.raises(In3CliError):
        cliaccount.validate_default_account()
        capture = capsys.readouterr()
        assert "No default account set." in capture.out


def test_validate_default_account_prints_create_account_help_when_no_valid_default_and_no_other_accounts_exists(
    capsys, config_accessor
):
    config_accessor.get_account.side_effect = NoConfigAccountError()
    config_accessor.get_all_accounts.return_value = []
    with pytest.raises(In3CliError):
        cliaccount.validate_default_account()
        capture = capsys.readouterr()
        assert "No existing account." in capture.out


def test_account_exists_when_exists_returns_true(config_accessor):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    assert cliaccount.account_exists("testaccountname")


def test_account_exists_when_not_exists_returns_false(config_accessor):
    config_accessor.get_account.side_effect = NoConfigAccountError()
    assert not cliaccount.account_exists("idontexist")


def test_switch_default_account_switches_to_expected_account(config_accessor):
    mock_section = MockSection("switchtome", {})
    config_accessor.get_account.return_value = mock_section
    cliaccount.switch_default_account("switchtome")
    config_accessor.switch_default_account.assert_called_once_with("switchtome")


def test_create_account_uses_expected_account_values(config_accessor):
    config_accessor.get_account.side_effect = NoConfigAccountError()
    account_name = "accountname"
    address = "0x99999"
    chain = Chain.EWC
    ssl_errors_disabled = True
    cliaccount.create_account(account_name, address, chain, ssl_errors_disabled)
    config_accessor.create_account.assert_called_once_with(
        account_name, address, chain, ssl_errors_disabled
    )


def test_create_account_if_account_exists_exits(
    mocker, cli_state, caplog, config_accessor
):
    config_accessor.get_account.return_value = mocker.MagicMock()
    with pytest.raises(In3CliError):
        cliaccount.create_account("foo", "bar", "baz", True)


def test_get_all_accounts_returns_expected_account_list(config_accessor):
    config_accessor.get_all_accounts.return_value = [
        create_mock_account("one"),
        create_mock_account("two"),
    ]
    accounts = cliaccount.get_all_accounts()
    assert len(accounts) == 2
    assert accounts[0].name == "one"
    assert accounts[1].name == "two"


def test_get_stored_private_key_returns_expected_private_key(
    config_accessor, private_key_getter
):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    private_key_getter.return_value = "testprivate_key"
    assert cliaccount.get_stored_private_key("testaccountname") == "testprivate_key"


def test_get_stored_private_key_uses_expected_account_name(
    config_accessor, private_key_getter
):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    test_account = "testaccountname"
    private_key_getter.return_value = "testprivate_key"
    cliaccount.get_stored_private_key(test_account)
    assert private_key_getter.call_args[0][0].name == test_account


def test_set_private_key_uses_expected_account_name(
    config_accessor, private_key_setter
):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    test_account = "testaccountname"
    cliaccount.set_private_key("newprivate_key", test_account)
    assert private_key_setter.call_args[0][0].name == test_account


def test_set_private_key_uses_expected_private_key(config_accessor, private_key_setter):
    mock_section = MockSection("testaccountname", {})
    config_accessor.get_account.return_value = mock_section
    test_account = "testaccountname"
    cliaccount.set_private_key("newprivate_key", test_account)
    assert private_key_setter.call_args[0][1] == "newprivate_key"


def test_delete_account_deletes_private_key_if_exists(
    config_accessor, mocker, private_key_getter, private_key_deleter
):
    account = create_mock_account("deleteme")
    mock_get_account = mocker.patch("in3cli.account._get_account")
    mock_get_account.return_value = account
    private_key_getter.return_value = "i_exist"
    cliaccount.delete_account("deleteme")
    private_key_deleter.assert_called_once_with(account)
