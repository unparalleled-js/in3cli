import pytest

import in3cli.private_key as private_key
from in3cli import __PRODUCT_NAME__

_USERNAME = "test.username"


@pytest.fixture
def keyring_private_key_getter(mocker):
    return mocker.patch("keyring.get_password")


@pytest.fixture(autouse=True)
def keyring_private_key_setter(mocker):
    return mocker.patch("keyring.set_password")


@pytest.fixture(autouse=True)
def get_keyring(mocker):
    mock = mocker.patch("keyring.get_keyring")
    mock.return_value.priority = 10
    return mock


@pytest.fixture
def getpass_function(mocker):
    return mocker.patch("{}.private_key.getpass".format(__PRODUCT_NAME__))


@pytest.fixture
def user_agreement(mocker):
    mock = mocker.patch("{}.private_key.does_user_agree".format(__PRODUCT_NAME__))
    mock.return_value = True
    return mocker


@pytest.fixture
def user_disagreement(mocker):
    mock = mocker.patch("{}.private_key.does_user_agree".format(__PRODUCT_NAME__))
    mock.return_value = False
    return mocker


def test_get_stored_private_key_when_given_account_name_gets_account_for_that_name(
    account, keyring_private_key_getter
):
    account.name = "account name"
    account.address = "0x123456"
    private_key.get_stored_private_key(account)
    expected_service_name = "{}::{}".format(__PRODUCT_NAME__, account.name)
    keyring_private_key_getter.assert_called_once_with(
        expected_service_name, account.address
    )


def test_get_stored_private_key_returns_expected_private_key(
    account, keyring_private_key_getter, keyring_private_key_setter
):
    keyring_private_key_getter.return_value = "already stored private_key 123"
    assert (
        private_key.get_stored_private_key(account) == "already stored private_key 123"
    )


def test_set_private_key_uses_expected_service_name_username_and_private_key(
    account, keyring_private_key_setter, keyring_private_key_getter
):
    keyring_private_key_getter.return_value = "test_private_key"
    account.name = "NAME!"
    account.address = "0x98765"
    private_key.set_private_key(account, "test_private_key")
    expected_service_name = "{}::{}".format(__PRODUCT_NAME__, account.name)
    keyring_private_key_setter.assert_called_once_with(
        expected_service_name, account.address, "test_private_key"
    )


def test_set_private_key_when_using_file_fallback_and_user_accepts_saves_private_key(
    account,
    keyring_private_key_setter,
    keyring_private_key_getter,
    get_keyring,
    user_agreement,
):
    keyring_private_key_getter.return_value = "test_private_key"
    account.name = "a_name"
    account.address = "0x000111222"
    private_key.set_private_key(account, "test_private_key")
    expected_service_name = "{}::{}".format(__PRODUCT_NAME__, account.name)
    keyring_private_key_setter.assert_called_once_with(
        expected_service_name, account.address, "test_private_key"
    )


def test_set_private_key_when_using_file_fallback_and_user_rejects_does_not_saves_private_key(
    account, keyring_private_key_setter, get_keyring, user_disagreement
):
    get_keyring.return_value.priority = 0.5
    keyring_private_key_getter.return_value = "test_private_key"
    account.name = "account_name"
    account.username = "test.username"
    private_key.set_private_key(account, "test_private_key")
    assert not keyring_private_key_setter.call_count


def test_prompt_for_private_key_calls_getpass(getpass_function):
    private_key.get_private_key_from_prompt()
    assert getpass_function.call_count
