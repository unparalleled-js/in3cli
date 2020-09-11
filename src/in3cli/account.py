from click import style

import in3cli.password as password
from in3cli.cmds.search.cursor_store import get_all_cursor_stores_for_account
from in3cli.config import config_accessor
from in3cli.config import ConfigAccessor
from in3cli.config import NoConfigaccountError
from in3cli.error import In3CliError


class In3Account:
    def __init__(self, account):
        self._account = account

    @property
    def name(self):
        return self._account.name

    @property
    def address(self):
        return self._account[ConfigAccessor.ADDRESS_KEY]

    @property
    def ignore_ssl_errors(self):
        return self._account[ConfigAccessor.IGNORE_SSL_ERRORS_KEY]

    @property
    def has_stored_password(self):
        stored_password = password.get_stored_password(self)
        return stored_password is not None and stored_password != ""

    def get_password(self):
        pwd = password.get_stored_password(self)
        if not pwd:
            pwd = password.get_password_from_prompt()
        return pwd

    def __str__(self):
        return "{}: Address={}".format(self.name, self.address)


def _get_account(account_name=None):
    """Returns the account for the given name."""
    config_account = config_accessor.get_account(account_name)
    return In3Account(config_account)


def get_account(account_name=None):
    if account_name is None:
        validate_default_account()
    try:
        return _get_account(account_name)
    except NoConfigaccountError as ex:
        raise in3CLIError(str(ex), help=CREATE_ACCOUNT_HELP)


def default_account_exists():
    try:
        account = _get_account()
        return account.name and account.name != ConfigAccessor.DEFAULT_VALUE
    except NoConfigaccountError:
        return False


def is_default_account(name):
    if default_account_exists():
        default = get_account()
        return name == default.name


def validate_default_account():
    if not default_account_exists():
        existing_accounts = get_all_accounts()
        if not existing_accounts:
            raise In3CliError("No existing account.")
        else:
            raise In3CliError("No default account set.")


def account_exists(account_name=None):
    try:
        _get_account(account_name)
        return True
    except NoConfigaccountError:
        return False


def switch_default_account(account_name):
    account = get_account(account_name)  # Handles if account does not exist.
    config_accessor.switch_default_account(account.name)


def create_account(name, server, username, ignore_ssl_errors):
    if account_exists(name):
        raise In3CliError("an account named '{}' already exists.".format(name))
    config_accessor.create_account(name, server, username, ignore_ssl_errors)


def delete_account(account_name):
    account = _get_account(account_name)
    if password.get_stored_password(account) is not None:
        password.delete_password(account)
    cursor_stores = get_all_cursor_stores_for_account(account_name)
    for store in cursor_stores:
        store.clean()
    config_accessor.delete_account(account_name)


def update_account(name, server, username, ignore_ssl_errors):
    config_accessor.update_account(name, server, username, ignore_ssl_errors)


def get_all_accounts():
    accounts = [In3Account(account) for account in config_accessor.get_all_accounts()]
    return accounts


def get_stored_password(account_name=None):
    account = get_account(account_name)
    return password.get_stored_password(account)


def set_password(new_password, account_name=None):
    account = get_account(account_name)
    password.set_password(account, new_password)


CREATE_ACCOUNT_HELP = "\nTo add an account, use:\n{}".format(
    style(
        "\tin3 account create --name <account-name> --server <authority-URL> --username <username>\n",
        bold=True,
    )
)


def _get_set_default_account_help(existing_accounts):
    existing_accounts = [str(account) for account in existing_accounts]
    accounts_str = "\n\t".join(existing_accounts)
    return """Use the --account flag to specify which account to use.
    To set the default account (used whenever --account argument is not provided), use: {}
    Existing accounts:\t{}""".format(
        style("in3 account use <account-name>", bold=True), accounts_str
    )
