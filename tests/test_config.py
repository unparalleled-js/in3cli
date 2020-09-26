from configparser import ConfigParser

import pytest

from in3cli.enums import Chain
from .conftest import MockSection
from in3cli.config import ConfigAccessor
from in3cli.config import NoConfigAccountError

_TEST_ACCOUNT_NAME = "AccountA"
_TEST_SECOND_ACCOUNT_NAME = "AccountB"
_INTERNAL = "Internal"


@pytest.fixture(autouse=True)
def mock_saver(mocker):
    return mocker.patch("in3cli.config.open")


@pytest.fixture
def mock_config_parser(mocker):
    return mocker.MagicMock(sepc=ConfigParser)


@pytest.fixture
def config_parser_for_multiple_accounts(mock_config_parser):
    mock_config_parser.sections.return_value = [
        _INTERNAL,
        _TEST_ACCOUNT_NAME,
        _TEST_SECOND_ACCOUNT_NAME,
    ]
    mock_account_a = create_mock_account_object(_TEST_ACCOUNT_NAME, "test", "test")
    mock_account_b = create_mock_account_object(
        _TEST_SECOND_ACCOUNT_NAME, "test", "test"
    )

    mock_internal = create_internal_object(True, _TEST_ACCOUNT_NAME)

    def side_effect(item):
        if item == _TEST_ACCOUNT_NAME:
            return mock_account_a
        elif item == _TEST_SECOND_ACCOUNT_NAME:
            return mock_account_b
        elif item == _INTERNAL:
            return mock_internal

    mock_config_parser.__getitem__.side_effect = side_effect
    return mock_config_parser


@pytest.fixture
def config_parser_for_create(mock_config_parser):
    values = [[_INTERNAL], [_INTERNAL, _TEST_ACCOUNT_NAME]]

    def side_effect():
        if len(values) == 2:
            return values.pop(0)
        return values[0]

    mock_config_parser.sections.side_effect = side_effect
    return mock_config_parser


def create_mock_account_object(account_name, address=None, chain=Chain.MAINNET):
    mock_account = MockSection(
        account_name,
        {ConfigAccessor.ADDRESS_KEY: address, ConfigAccessor.CHAIN_KEY: chain},
    )
    return mock_account


def create_internal_object(is_complete, default_account_name=None):
    default_account_name = default_account_name or ConfigAccessor.DEFAULT_VALUE
    internal_dict = {ConfigAccessor.DEFAULT_ACCOUNT_KEY: default_account_name}
    internal_section = MockSection(_INTERNAL, internal_dict)

    def getboolean(*args):
        return is_complete

    internal_section.getboolean = getboolean
    return internal_section


def setup_parser_one_account(account, internal, parser):
    def side_effect(item):
        if item == _TEST_ACCOUNT_NAME:
            return account
        elif item == _INTERNAL:
            return internal

    parser.__getitem__.side_effect = side_effect


class TestConfigAccessor:
    def test_internal_creates_if_not_exists(self, mock_config_parser):
        mock_config_parser.sections.return_value = []
        accessor = ConfigAccessor(mock_config_parser)
        internal_section = accessor._internal
        assert mock_config_parser.sections.contains(internal_section)

    def test_get_account_when_account_does_not_exist_raises(self, mock_config_parser):
        mock_config_parser.sections.return_value = [_INTERNAL]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(NoConfigAccountError):
            accessor.get_account("Account Name that does not exist")

    def test_get_account_when_account_has_default_name_raises(self, mock_config_parser):
        mock_config_parser.sections.return_value = [_INTERNAL]
        accessor = ConfigAccessor(mock_config_parser)
        with pytest.raises(NoConfigAccountError):
            accessor.get_account(ConfigAccessor.DEFAULT_VALUE)

    def test_get_account_returns_expected_account(self, mock_config_parser):
        mock_config_parser.sections.return_value = [_INTERNAL, _TEST_ACCOUNT_NAME]
        accessor = ConfigAccessor(mock_config_parser)
        accessor.get_account(_TEST_ACCOUNT_NAME)
        assert mock_config_parser.__getitem__.call_args[0][0] == _TEST_ACCOUNT_NAME

    def test_get_all_accounts_excludes_internal_section(self, mock_config_parser):
        mock_config_parser.sections.return_value = [
            _TEST_ACCOUNT_NAME,
            _INTERNAL,
            _TEST_SECOND_ACCOUNT_NAME,
        ]
        accessor = ConfigAccessor(mock_config_parser)
        accounts = accessor.get_all_accounts()
        for a in accounts:
            if a.name == _INTERNAL:
                raise AssertionError()

    def test_get_all_accounts_returns_accounts_with_expected_values(
        self, config_parser_for_multiple_accounts
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_accounts)
        accounts = accessor.get_all_accounts()
        assert accounts[0].name == _TEST_ACCOUNT_NAME
        assert accounts[1].name == _TEST_SECOND_ACCOUNT_NAME

    def test_switch_default_account_switches_internal_value(
        self, config_parser_for_multiple_accounts
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_accounts)
        accessor.switch_default_account(_TEST_SECOND_ACCOUNT_NAME)
        assert (
            config_parser_for_multiple_accounts[_INTERNAL][
                ConfigAccessor.DEFAULT_ACCOUNT_KEY
            ]
            == _TEST_SECOND_ACCOUNT_NAME
        )

    def test_switch_default_account_saves(
        self, config_parser_for_multiple_accounts, mock_saver
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_accounts)
        accessor.switch_default_account(_TEST_SECOND_ACCOUNT_NAME)
        assert mock_saver.call_count

    def test_create_account_when_given_default_name_does_not_create(
        self, config_parser_for_create
    ):
        accessor = ConfigAccessor(config_parser_for_create)
        with pytest.raises(Exception):
            accessor.create_account(ConfigAccessor.DEFAULT_VALUE, "foo", "bar", False)

    def test_create_account_when_no_default_account_sets_default(
        self, mocker, config_parser_for_create, mock_saver
    ):
        create_mock_account_object(_TEST_ACCOUNT_NAME, None, None)
        mock_internal = create_internal_object(False)
        setup_parser_one_account(mock_internal, mock_internal, config_parser_for_create)
        accessor = ConfigAccessor(config_parser_for_create)
        mock = mocker.MagicMock()
        accessor.switch_default_account = mock

        accessor.create_account(_TEST_ACCOUNT_NAME, "example.com", "bar", False)
        assert mock.call_count == 1

    def test_create_account_when_has_default_account_does_not_set_default(
        self, mocker, config_parser_for_create, mock_saver
    ):
        create_mock_account_object(_TEST_ACCOUNT_NAME, None, None)
        mock_internal = create_internal_object(True, _TEST_ACCOUNT_NAME)
        setup_parser_one_account(mock_internal, mock_internal, config_parser_for_create)
        accessor = ConfigAccessor(config_parser_for_create)
        mock = mocker.MagicMock()
        accessor.switch_default_account = mock

        accessor.create_account(_TEST_ACCOUNT_NAME, "example.com", "bar", False)
        assert not mock.call_count

    def test_create_account_when_not_existing_saves(
        self, config_parser_for_create, mock_saver
    ):
        create_mock_account_object(_TEST_ACCOUNT_NAME, None, None)
        mock_internal = create_internal_object(False)
        setup_parser_one_account(mock_internal, mock_internal, config_parser_for_create)
        accessor = ConfigAccessor(config_parser_for_create)

        accessor.create_account(_TEST_ACCOUNT_NAME, "example.com", "bar", False)
        assert mock_saver.call_count

    def test_update_account_when_no_account_exists_raises_exception(
        self, config_parser_for_multiple_accounts
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_accounts)
        with pytest.raises(Exception):
            accessor.update_account("Non-existent Account")

    def test_update_account_updates_account(self, config_parser_for_multiple_accounts):
        accessor = ConfigAccessor(config_parser_for_multiple_accounts)
        address = "NEW ADDRESS"
        chain = Chain.GOERLI

        accessor.update_account(_TEST_ACCOUNT_NAME, address, chain, True)
        assert (
            accessor.get_account(_TEST_ACCOUNT_NAME)[ConfigAccessor.ADDRESS_KEY]
            == address
        )
        assert (
            accessor.get_account(_TEST_ACCOUNT_NAME)[ConfigAccessor.CHAIN_KEY] == chain
        )
        assert accessor.get_account(_TEST_ACCOUNT_NAME)[
            ConfigAccessor.IGNORE_SSL_ERRORS_KEY
        ]

    def test_update_account_does_not_update_when_given_none(
        self, config_parser_for_multiple_accounts
    ):
        accessor = ConfigAccessor(config_parser_for_multiple_accounts)

        # First, make sure they're not None
        address = "NOT NONE"
        chain = Chain.MAINNET
        accessor.update_account(_TEST_ACCOUNT_NAME, address, chain, True)

        accessor.update_account(_TEST_ACCOUNT_NAME, None, None, None)
        assert (
            accessor.get_account(_TEST_ACCOUNT_NAME)[ConfigAccessor.ADDRESS_KEY]
            == address
        )
        assert (
            accessor.get_account(_TEST_ACCOUNT_NAME)[ConfigAccessor.CHAIN_KEY] == chain
        )
        assert accessor.get_account(_TEST_ACCOUNT_NAME)[
            ConfigAccessor.IGNORE_SSL_ERRORS_KEY
        ]
