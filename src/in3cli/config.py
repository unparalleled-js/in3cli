import os
from configparser import ConfigParser

from in3cli.enums import Chain
from in3cli.util import get_user_project_path


class NoConfigAccountError(Exception):
    def __init__(self, account_arg_name=None):
        message = (
            "account '{}' does not exist.".format(account_arg_name)
            if account_arg_name
            else "account does not exist."
        )
        super().__init__(message)


class ConfigAccessor:
    DEFAULT_VALUE = "__DEFAULT__"

    # Internal keys
    _INTERNAL_SECTION = "Internal"
    DEFAULT_ACCOUNT_KEY = "default_account"

    # Keys
    ADDRESS_KEY = "address"  # Wallet Address (Public)
    IGNORE_SSL_ERRORS_KEY = "ignore-ssl-errors"
    CHAIN_KEY = "chain"

    def __init__(self, parser):
        self.parser = parser
        file_name = "config.cfg"
        self.path = os.path.join(get_user_project_path(), file_name)
        if not os.path.exists(self.path):
            self._create_internal_section()
            self._save()
        else:
            self.parser.read(self.path)

    @property
    def _internal(self):
        try:
            return self.parser[self._INTERNAL_SECTION]
        except KeyError:
            self._create_internal_section()
            return self.parser[self._INTERNAL_SECTION]

    @property
    def default_account(self):
        return self._internal[self.DEFAULT_ACCOUNT_KEY]

    @default_account.setter
    def default_account(self, value):
        self._internal[self.DEFAULT_ACCOUNT_KEY] = value

    def get_account(self, name=None):
        """Returns the account with the given name.
        If name is None, returns the default account.
        If the name does not exist or there is no existing account, it will throw an exception.
        """
        name = name or self.default_account
        if name not in self._get_sections() or name == self.DEFAULT_VALUE:
            name = name if name != self.DEFAULT_VALUE else None
            raise NoConfigAccountError(name)
        return self._get_account(name)

    def get_all_accounts(self):
        """Returns all the available accounts."""
        accounts = []
        names = self._get_account_names()
        for name in names:
            accounts.append(self.get_account(name))
        return accounts

    def create_account(self, name, address, chain, ignore_ssl_errors):
        """Creates a new account if one does not already exist for that name."""
        try:
            self.get_account(name)
        except NoConfigAccountError as ex:
            if name is not None and name != self.DEFAULT_VALUE:
                self._create_account_section(name)
            else:
                raise ex

        account = self.get_account(name)
        self.update_account(
            name=account.name,
            address=address,
            chain=chain,
            ignore_ssl_errors=ignore_ssl_errors,
        )
        self._try_complete_setup(account)

    def update_account(self, name, address=None, chain=None, ignore_ssl_errors=None):
        account = self.get_account(name)
        if address:
            self._set_address(address, account)
        if chain:
            self._set_chain(chain, account)
        if ignore_ssl_errors is not None:
            self._set_ignore_ssl_errors(ignore_ssl_errors, account)
        self._save()

    def switch_default_account(self, new_default_name):
        """Changes what is marked as the default account in the internal section."""
        if self.get_account(new_default_name) is None:
            raise NoConfigAccountError(new_default_name)
        self.default_account = new_default_name
        self._save()

    def delete_account(self, name):
        """Deletes an account."""
        if self.get_account(name) is None:
            raise NoConfigAccountError(name)
        self.parser.remove_section(name)
        if name == self.default_account:
            self._internal[self.DEFAULT_ACCOUNT_KEY] = self.DEFAULT_VALUE
        self._save()

    def _set_address(self, new_value, account):
        account[self.ADDRESS_KEY] = new_value.strip()

    def _set_chain(self, new_value, account):
        account[self.CHAIN_KEY] = new_value

    def _set_ignore_ssl_errors(self, new_value, account):
        account[self.IGNORE_SSL_ERRORS_KEY] = str(new_value)

    def _get_sections(self):
        return self.parser.sections()

    def _get_account(self, name):
        return self.parser[name]

    def _get_account_names(self):
        names = list(self._get_sections())
        names.remove(self._INTERNAL_SECTION)
        return names

    def _create_internal_section(self):
        self.parser.add_section(self._INTERNAL_SECTION)
        self.parser[self._INTERNAL_SECTION] = {}
        self.parser[self._INTERNAL_SECTION][self.DEFAULT_ACCOUNT_KEY] = self.DEFAULT_VALUE

    def _create_account_section(self, name):
        account = {
            self.ADDRESS_KEY: self.DEFAULT_VALUE,
            self.IGNORE_SSL_ERRORS_KEY: str(False),
            self.CHAIN_KEY: Chain.MAINNET,
        }
        self.parser.add_section(name)
        self.parser[name] = account

    def _save(self):
        with open(self.path, "w+", encoding="utf-8") as file:
            self.parser.write(file)

    def _try_complete_setup(self, account):
        address = account.get(self.ADDRESS_KEY)
        if not address or address == self.DEFAULT_VALUE:
            return
        self._save()
        default_account = self._internal.get(self.DEFAULT_ACCOUNT_KEY)
        if not default_account or default_account == self.DEFAULT_VALUE:
            self.switch_default_account(account.name)


config_accessor = ConfigAccessor(ConfigParser())
