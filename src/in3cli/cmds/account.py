from getpass import getpass

import click
from click import echo
from click import secho

import in3cli.account as account_module
from in3cli.client import CliClient
from in3cli.error import In3CliError
from in3cli.options import address_option
from in3cli.options import chain_option
from in3cli.options import yes_option
from in3cli.private_key import get_private_key_from_prompt
from in3cli.util import does_user_agree


@click.group()
def account():
    """For managing In3 wallet settings."""
    pass


account_name_arg = click.argument("account_name", required=False)
name_option = click.option(
    "-n",
    "--name",
    required=True,
    help="The name of the in3 CLI account to use when executing this command.",
)
private_key_option = click.option(
    "--private-key",
    help="The private key for the wallet to use. It is not recommended to use this option. "
         "If this option is omitted, interactive prompts will be used to obtain the private key.",
)
disable_ssl_option = click.option(
    "--disable-ssl-errors",
    is_flag=True,
    help="For development purposes, do not validate the SSL certifications for network requests. "
    "This is not recommended, except for specific scenarios like testing.",
)


@account.command()
@account_name_arg
def show(account_name):
    """Print the details of an account."""
    in3account = account_module.get_account(account_name)
    echo("{}:".format(in3account.name))
    echo("\tAddress: {}".format(in3account.address))
    echo("\tChain: {}".format(in3account.chain))
    echo("\tIgnore SSL Errors: {}".format(in3account.ignore_ssl_errors))
    if account_module.get_stored_private_key(in3account.name) is not None:
        echo("\t* Private key is set.")


@account.command()
@name_option
@address_option
@private_key_option
@chain_option()
@disable_ssl_option
def create(name, address, private_key, chain, disable_ssl_errors):
    """Create account settings. The first account created will be the default."""
    account_module.create_account(
        name=name,
        address=address,
        chain=chain,
        ignore_ssl_errors=disable_ssl_errors,
    )
    if private_key:
        _set_private_key(name, private_key)
    else:
        _prompt_for_allow_private_key_set(name)
    echo("Successfully created account '{}'.".format(name))


@account.command()
@name_option
@address_option
@private_key_option
@chain_option()
@disable_ssl_option
def update(name, address, private_key, chain, disable_ssl_errors):
    """Update an existing account."""
    in3account = account_module.get_account(name)
    account_module.update_account(
        name=in3account.name,
        address=address,
        chain=chain,
        ignore_ssl_errors=disable_ssl_errors
    )
    if private_key:
        _set_private_key(name, private_key)
    else:
        _prompt_for_allow_private_key_set(in3account.name)
    echo("account '{}' has been updated.".format(in3account.name))


@account.command()
@account_name_arg
def reset_private_key(account_name):
    """\b
    Change the stored private key for an account."""
    key = getpass()
    _set_private_key(account_name, key)
    echo("Private key updated for account '{}'".format(account_name))


@account.command("list")
def _list():
    """Show all existing stored accounts."""
    accounts = account_module.get_all_accounts()
    if not accounts:
        raise In3CliError("No existing account.")
    for in3account in accounts:
        echo(str(in3account))


@account.command()
@account_name_arg
def use(account_name):
    """Set an account as the default."""
    account_module.switch_default_account(account_name)
    echo("{} has been set as the default account.".format(account_name))


@account.command()
@yes_option
@account_name_arg
def delete(account_name):
    """Deletes an account and its stored private key (if any)."""
    message = "\nDeleting this account will also delete any stored private keys. Are you sure? (y/n): "
    if account_module.is_default_account(account_name):
        message = "\n'{}' is currently the default account!\n{}".format(
            account_name, message
        )
    if does_user_agree(message):
        account_module.delete_account(account_name)
        echo("account '{}' has been deleted.".format(account_name))


@account.command()
@yes_option
def delete_all():
    """Deletes all accounts and saved private keys (if any)."""
    existing_accounts = account_module.get_all_accounts()
    if existing_accounts:
        message = (
            "\nAre you sure you want to delete the following accounts?\n\t{}"
            "\n\nThis will also delete any stored private keys. (y/n): "
        ).format("\n\t".join([in3account.name for in3account in existing_accounts]))
        if does_user_agree(message):
            for account_obj in existing_accounts:
                account_module.delete_account(account_obj.name)
                echo("account '{}' has been deleted.".format(account_obj.name))
    else:
        echo("\nNo accounts exist. Nothing to delete.")


def _prompt_for_allow_private_key_set(account_name):
    if does_user_agree("Would you like to store or update your private key in keyring? (y/n): "):
        private_key = get_private_key_from_prompt()
        _set_private_key(account_name, private_key)


def _set_private_key(account_name, private_key):
    in3account = account_module.get_account(account_name)
    try:
        CliClient(in3account).validate()
    except Exception:
        secho("Private key not stored!", bold=True)
        raise
    account_module.set_private_key(private_key, in3account.name)
