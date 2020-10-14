import in3cli.private_key as private_key
from click import style
from in3cli.config import ConfigAccessor
from in3cli.config import NoConfigAccountError
from in3cli.config import config_accessor
from in3cli.error import In3CliError
from in3cli.util import to_bool


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
    def chain(self):
        return self._account[ConfigAccessor.CHAIN_KEY]

    @property
    def ignore_ssl_errors(self):
        stored_value = self._account[ConfigAccessor.IGNORE_SSL_ERRORS_KEY]
        return to_bool(stored_value)

    @property
    def has_stored_private_key(self):
        key = self._get_stored_key()
        return key is not None and key != ""

    def get_private_key(self, prompt=True):
        key = self._get_stored_key()
        if not key and prompt:
            return private_key.get_private_key_from_prompt()
        return key

    def _get_stored_key(self):
        return private_key.get_stored_private_key(self) or None

    def __str__(self):
        return "{}: Address={}, Chain={}.".format(self.name, self.address, self.chain)


def _get_account(account_name=None):
    """Returns the account for the given name."""
    config_account = config_accessor.get_account(account_name)
    return In3Account(config_account)


def get_account(account_name=None):
    if account_name is None:
        validate_default_account()
    try:
        return _get_account(account_name)
    except NoConfigAccountError as ex:
        raise In3CliError(str(ex))


def default_account_exists():
    try:
        account = _get_account()
        return account.name and account.name != ConfigAccessor.DEFAULT_VALUE
    except NoConfigAccountError:
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
        raise In3CliError("No default account set.")


def account_exists(account_name=None):
    try:
        _get_account(account_name)
        return True
    except NoConfigAccountError:
        return False


def switch_default_account(account_name):
    account = get_account(account_name)  # Handles if account does not exist.
    config_accessor.switch_default_account(account.name)


def create_account(name, address, chain, ignore_ssl_errors):
    if account_exists(name):
        raise In3CliError("An account named '{}' already exists.".format(name))
    config_accessor.create_account(
        name,
        address,
        chain,
        ignore_ssl_errors,
    )


def delete_account(account_name):
    account = _get_account(account_name)
    if private_key.get_stored_private_key(account) is not None:
        private_key.delete_private_key(account)
    config_accessor.delete_account(account_name)


def update_account(name, address, chain, ignore_ssl_errors):
    config_accessor.update_account(
        name=name,
        address=address,
        chain=chain,
        ignore_ssl_errors=ignore_ssl_errors,
    )


def get_all_accounts():
    accounts = [In3Account(account) for account in config_accessor.get_all_accounts()]
    return accounts


def get_stored_private_key(account_name=None):
    account = get_account(account_name)
    return private_key.get_stored_private_key(account)


def set_private_key(new_private_key, account_name=None):
    account = get_account(account_name)
    private_key.set_private_key(account, new_private_key)


CREATE_ACCOUNT_HELP = "\nTo add an account, use:\n{}".format(
    style(
        "\tin3 account create --name <account-name> --address <address>\n",
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
