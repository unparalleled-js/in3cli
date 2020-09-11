import os
import keyring
from configparser import ConfigParser

from in3cli import __PRODUCT_NAME__
from in3cli.util import get_user_project_path


def set_secret(address, secret):
    keyring.set_password(__PRODUCT_NAME__, address, secret)


def get_secret(address):
    return keyring.get_password(__PRODUCT_NAME__, address)


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
    ADDRESS_KEY = "address"  # Wallet Address (Public)
    IGNORE_SSL_ERRORS_KEY = "ignore-ssl-errors"
    DEFAULT_account = "default_account"
    _INTERNAL_SECTION = "Internal"

    def __init__(self, parser):
        self.parser = parser
        file_name = "config.cfg"
        self.path = os.path.join(get_user_project_path(), file_name)
        if not os.path.exists(self.path):
            self._create_internal_section()
            self._save()
        else:
            self.parser.read(self.path)

    def get_account(self, name=None):
        """Returns the account with the given name.
        If name is None, returns the default account.
        If the name does not exist or there is no existing account, it will throw an exception.
        """
        name = name or self._default_account_name
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

    def create_account(self, name, username, ignore_ssl_errors):
        """Creates a new account if one does not already exist for that name."""
        try:
            self.get_account(name)
        except NoConfigAccountError as ex:
            if name is not None and name != self.DEFAULT_VALUE:
                self._create_account_section(name)
            else:
                raise ex

        account = self.get_account(name)
        self.update_account(account.name, username, ignore_ssl_errors)
        self._try_complete_setup(account)

    def update_account(self, name, username=None, ignore_ssl_errors=None):
        account = self.get_account(name)
        if username:
            self._set_username(username, account)
        if ignore_ssl_errors is not None:
            self._set_ignore_ssl_errors(ignore_ssl_errors, account)
        self._save()

    def switch_default_account(self, new_default_name):
        """Changes what is marked as the default account in the internal section."""
        if self.get_account(new_default_name) is None:
            raise NoConfigAccountError(new_default_name)
        self._internal[self.DEFAULT_account] = new_default_name
        self._save()

    def delete_account(self, name):
        """Deletes an account."""
        if self.get_account(name) is None:
            raise NoConfigAccountError(name)
        self.parser.remove_section(name)
        if name == self._default_account_name:
            self._internal[self.DEFAULT_account] = self.DEFAULT_VALUE
        self._save()

    def _set_username(self, new_value, account):
        account[self.ADDRESS_KEY] = new_value.strip()

    def _set_ignore_ssl_errors(self, new_value, account):
        account[self.IGNORE_SSL_ERRORS_KEY] = str(new_value)

    def _get_sections(self):
        return self.parser.sections()

    def _get_account(self, name):
        return self.parser[name]

    @property
    def _internal(self):
        return self.parser[self._INTERNAL_SECTION]

    @property
    def _default_account_name(self):
        return self._internal[self.DEFAULT_account]

    def _get_account_names(self):
        names = list(self._get_sections())
        names.remove(self._INTERNAL_SECTION)
        return names

    def _create_internal_section(self):
        self.parser.add_section(self._INTERNAL_SECTION)
        self.parser[self._INTERNAL_SECTION] = {}
        self.parser[self._INTERNAL_SECTION][self.DEFAULT_account] = self.DEFAULT_VALUE

    def _create_account_section(self, name):
        self.parser.add_section(name)
        self.parser[name] = {}
        self.parser[name][self.ADDRESS_KEY] = self.DEFAULT_VALUE
        self.parser[name][self.IGNORE_SSL_ERRORS_KEY] = str(False)

    def _save(self):
        with open(self.path, "w+", encoding="utf-8") as file:
            self.parser.write(file)

    def _try_complete_setup(self, account):
        username = account.get(self.ADDRESS_KEY)
        username_valid = username and username != self.DEFAULT_VALUE
        if not username_valid:
            return

        self._save()

        default_account = self._internal.get(self.DEFAULT_account)
        if default_account is None or default_account == self.DEFAULT_VALUE:
            self.switch_default_account(account.name)


config_accessor = ConfigAccessor(ConfigParser())
