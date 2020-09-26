import pytest

from in3cli.enums import Chain
from tests.conftest import create_mock_account
from in3cli import __PRODUCT_NAME__
from in3cli.error import In3CliError
from in3cli.main import cli


@pytest.fixture
def user_agreement(mocker):
    mock = mocker.patch("{}.cmds.account.does_user_agree".format(__PRODUCT_NAME__))
    mock.return_value = True
    return mocker


@pytest.fixture
def user_disagreement(mocker):
    mock = mocker.patch("{}.cmds.account.does_user_agree".format(__PRODUCT_NAME__))
    mock.return_value = False
    return mocker


@pytest.fixture
def mock_account_module(mocker):
    return mocker.patch("{}.cmds.account.account_module".format(__PRODUCT_NAME__))


@pytest.fixture(autouse=True)
def mock_getpass(mocker):
    mock = mocker.patch("{}.cmds.account.getpass".format(__PRODUCT_NAME__))
    mock.return_value = "newpassword"


def test_show_outputs_account_info(mocker, runner, mock_account_module, account):
    account = create_mock_account("SecAcct")
    key_mock = mocker.MagicMock()
    key_mock.return_value = "private_key"
    account.get_private_key = key_mock
    mock_account_module.get_account.return_value = account
    result = runner.invoke(cli, ["account", "show"])
    assert account.name in result.output
    assert account.address in result.output
    assert account.chain in result.output
    assert "* Private key is set." in result.output


def test_show_account_when_password_set_outputs_password_note(
    runner, mock_account_module, account
):
    mock_account_module.get_account.return_value = account
    mock_account_module.get_stored_password.return_value = None
    result = runner.invoke(cli, ["account", "show"])
    assert "A password is set" not in result.output


def test_create_account_if_user_sets_password_is_created(
    runner, user_agreement, mock_account_module
):
    mock_account_module.account_exists.return_value = False
    runner.invoke(
        cli,
        [
            "account",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_account_module.create_account.assert_called_once_with(
        "foo", "bar", "baz", True
    )


def test_create_account_if_user_does_not_set_password_is_created(
    runner, user_disagreement, mock_verify, mock_account_module
):
    mock_account_module.account_exists.return_value = False
    runner.invoke(
        cli,
        [
            "account",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_account_module.create_account.assert_called_once_with(
        "foo", "bar", "baz", True
    )


def test_create_account_if_user_does_not_agree_does_not_save_password(
    runner, user_disagreement, mock_verify, mock_account_module
):
    mock_account_module.account_exists.return_value = False
    runner.invoke(
        cli,
        [
            "account",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert not mock_account_module.set_password.call_count


def test_create_account_if_credentials_invalid_password_not_saved(
    runner, user_agreement, mock_account_module, cli_state
):
    cli_state.client.validate.return_value = False
    mock_account_module.account_exists.return_value = False
    result = runner.invoke(
        cli,
        ["account", "create", "-n", "foo", "-a", "bar", "-c", Chain.MAINNET, "--private-key", "key"],
    )
    assert "Private key not stored!" in result.output
    assert not mock_account_module.set_private_key.call_count


def test_create_account_with_password_option_if_credentials_invalid_password_not_saved(
    runner, cli_state, mock_account_module
):
    cli_state.client.validate.return_value = False
    private_key = "test_key"
    mock_account_module.account_exists.return_value = False
    result = runner.invoke(
        cli,
        [
            "account",
            "create",
            "-n",
            "foo",
            "-a",
            "bar",
            "-c",
            "goerli",
            "--private-key",
            private_key,
        ],
    )
    assert "Private key not stored!" in result.output
    assert not mock_account_module.set_password.call_count
    assert "Would you like to set a private key?" not in result.output


def test_create_account_if_credentials_valid_password_saved(
    runner, mocker, user_agreement, valid_connection, mock_account_module
):
    mock_account_module.account_exists.return_value = False
    runner.invoke(cli, ["account", "create", "-n", "foo", "-s", "bar", "-u", "baz"])
    mock_account_module.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )


def test_create_account_with_password_option_if_credentials_valid_password_saved(
    runner, mocker, valid_connection, mock_account_module
):
    password = "test_pass"
    mock_account_module.account_exists.return_value = False
    result = runner.invoke(
        cli,
        [
            "account",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--password",
            password,
        ],
    )
    mock_account_module.set_password.assert_called_once_with(password, mocker.ANY)
    assert "Would you like to set a password?" not in result.output


def test_create_account_outputs_confirmation(
    runner, user_agreement, valid_connection, mock_account_module
):
    mock_account_module.account_exists.return_value = False
    result = runner.invoke(
        cli,
        [
            "account",
            "create",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert "Successfully created account 'foo'." in result.output


def test_update_account_updates_existing_account(
    runner, mock_account_module, user_agreement, valid_connection, account
):
    name = "foo"
    account.name = name
    mock_account_module.get_account.return_value = account
    runner.invoke(
        cli,
        [
            "account",
            "update",
            "-n",
            name,
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_account_module.update_account.assert_called_once_with(
        name, "bar", "baz", True
    )


def test_update_account_if_user_does_not_agree_does_not_save_password(
    runner, mock_account_module, user_disagreement, invalid_connection, account
):
    name = "foo"
    account.name = name
    mock_account_module.get_account.return_value = account
    runner.invoke(
        cli,
        [
            "account",
            "update",
            "-n",
            name,
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert not mock_account_module.set_password.call_count


def test_update_account_if_credentials_invalid_password_not_saved(
    runner, user_agreement, invalid_connection, mock_account_module, account
):
    name = "foo"
    account.name = name
    mock_account_module.get_account.return_value = account

    result = runner.invoke(
        cli,
        [
            "account",
            "update",
            "-n",
            "foo",
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    assert not mock_account_module.set_password.call_count
    assert "Password not stored!" in result.output


def test_update_account_if_user_agrees_and_valid_connection_sets_password(
    runner, mocker, user_agreement, valid_connection, mock_account_module, account
):
    name = "foo"
    account.name = name
    mock_account_module.get_account.return_value = account
    runner.invoke(
        cli,
        [
            "account",
            "update",
            "-n",
            name,
            "-s",
            "bar",
            "-u",
            "baz",
            "--disable-ssl-errors",
        ],
    )
    mock_account_module.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )


def test_delete_account_warns_if_deleting_default(runner, mock_account_module):
    mock_account_module.is_default_account.return_value = True
    result = runner.invoke(cli, ["account", "delete", "mockdefault"])
    assert "'mockdefault' is currently the default account!" in result.output


def test_delete_account_does_nothing_if_user_doesnt_agree(
    runner, user_disagreement, mock_account_module
):
    runner.invoke(cli, ["account", "delete", "mockdefault"])
    assert mock_account_module.delete_account.call_count == 0


def test_delete_account_outputs_success(
    runner, mock_account_module, user_agreement
):
    result = runner.invoke(cli, ["account", "delete", "mockdefault"])
    assert "account 'mockdefault' has been deleted." in result.output


def test_delete_all_warns_if_accounts_exist(runner, mock_account_module):
    mock_account_module.get_all_accounts.return_value = [
        create_mock_account("test1"),
        create_mock_account("test2"),
    ]
    result = runner.invoke(cli, ["account", "delete-all"])
    assert "Are you sure you want to delete the following accounts?" in result.output
    assert "test1" in result.output
    assert "test2" in result.output


def test_delete_all_does_not_warn_if_assume_yes_flag(runner, mock_account_module):
    mock_account_module.get_all_accounts.return_value = [
        create_mock_account("test1"),
        create_mock_account("test2"),
    ]
    result = runner.invoke(cli, ["account", "delete-all", "-y"])
    assert (
        "Are you sure you want to delete the following accounts?" not in result.output
    )
    assert "Account '{}' has been deleted.".format("test1") in result.output
    assert "Account '{}' has been deleted.".format("test2") in result.output


def test_delete_all_accounts_does_nothing_if_user_doesnt_agree(
    runner, user_disagreement, mock_account_module
):
    runner.invoke(cli, ["account", "delete-all"])
    assert mock_account_module.delete_account.call_count == 0


def test_delete_all_deletes_all_existing_accounts(
    runner, user_agreement, mock_account_module
):
    mock_account_module.get_all_accounts.return_value = [
        create_mock_account("test1"),
        create_mock_account("test2"),
    ]
    runner.invoke(cli, ["account", "delete-all"])
    mock_account_module.delete_account.assert_any_call("test1")
    mock_account_module.delete_account.assert_any_call("test2")


def test_reset_pw_if_credentials_valid_password_saved(
    runner, mocker, user_agreement, mock_verify, mock_account_module
):
    mock_verify.return_value = True
    mock_account_module.account_exists.return_value = False
    runner.invoke(cli, ["account", "reset-pw"])
    mock_account_module.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )


def test_reset_pw_if_credentials_invalid_password_not_saved(
    runner, user_agreement, mock_verify, mock_account_module
):
    mock_verify.side_effect = In3CliError("Invalid credentials for user")
    mock_account_module.account_exists.return_value = False
    runner.invoke(cli, ["account", "reset-pw"])
    assert not mock_account_module.set_password.call_count


def test_reset_pw_uses_default_account_when_not_given_one(
    runner, mocker, user_agreement, mock_verify, mock_account_module
):
    mock_verify.return_value = True
    mock_account_module.account_exists.return_value = False
    mock_account = create_mock_account("one")
    mock_account_module.get_account.return_value = mock_account
    res = runner.invoke(cli, ["account", "reset-pw"])
    mock_account_module.set_password.assert_called_once_with(
        "newpassword", mocker.ANY
    )
    assert "Password updated for account 'one'." in res.output


def test_list_accounts(runner, mock_account_module):
    accounts = [
        create_mock_account("one"),
        create_mock_account("two"),
        create_mock_account("three"),
    ]
    mock_account_module.get_all_accounts.return_value = accounts
    result = runner.invoke(cli, ["account", "list"])
    assert "one" in result.output
    assert "two" in result.output
    assert "three" in result.output


def test_list_accounts_when_no_accounts_outputs_no_accounts_message(
    runner, mock_account_module
):
    mock_account_module.get_all_accounts.return_value = []
    result = runner.invoke(cli, ["account", "list"])
    assert "No existing account." in result.output


def test_use_account(runner, mock_account_module, account):
    result = runner.invoke(cli, ["account", "use", account.name])
    mock_account_module.switch_default_account.assert_called_once_with(
        account.name
    )
    assert (
        "{} has been set as the default account.".format(account.name) in result.output
    )
