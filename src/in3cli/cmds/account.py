from getpass import getpass

import click
from click import echo
from click import secho

import in3cli.account as cli_account
from in3cli.client import validate_account
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
    in3account = cli_account.get_account(account_name)
    echo("{}:".format(in3account.name))
    echo("\tAddress: {}".format(in3account.address))
    echo("\tChain: {}".format(in3account.chain))
    echo("\tIgnore SSL Errors: {}".format(in3account.ignore_ssl_errors))
    if cli_account.get_stored_private_key(in3account.name) is not None:
        echo("\t* Private key is set.")


@account.command()
@name_option
@address_option
@private_key_option
@disable_ssl_option
def create(name, address, private_key, disable_ssl_errors):
    """Create account settings. The first account created will be the default."""
    cli_account.create_account(name, address, disable_ssl_errors)
    if private_key:
        _set_private_key(name, private_key)
    else:
        _prompt_for_allow_private_key_set(name)
    echo("Successfully created account '{}'.".format(name))


@account.command()
@name_option
@address_option
@private_key_option
@disable_ssl_option
@chain_option
def update(name, address, private_key, disable_ssl_errors):
    """Update an existing account."""
    in3account = cli_account.get_account(name)
    cli_account.update_account(in3account.name, address, disable_ssl_errors)
    if private_key:
        _set_private_key(name, private_key)
    else:
        _prompt_for_allow_private_key_set(in3account.name)
    echo("account '{}' has been updated.".format(in3account.name))


@account.command()
@account_name_arg
def reset_private_key(account_name):
    """\b
    Change the stored password for an account. Only affects what's stored in the local account,
    does not make any changes to the in3 user account."""
    password = getpass()
    _set_private_key(account_name, password)
    echo("Password updated for account '{}'".format(account_name))


@account.command("list")
def _list():
    """Show all existing stored accounts."""
    accounts = cli_account.get_all_accounts()
    if not accounts:
        raise In3CliError("No existing account.")
    for in3account in accounts:
        echo(str(in3account))


@account.command()
@account_name_arg
def use(account_name):
    """Set an account as the default."""
    cli_account.switch_default_account(account_name)
    echo("{} has been set as the default account.".format(account_name))


@account.command()
@yes_option
@account_name_arg
def delete(account_name):
    """Deletes an account and its stored password (if any)."""
    message = "\nDeleting this account will also delete any stored passwords and checkpoints. Are you sure? (y/n): "
    if cli_account.is_default_account(account_name):
        message = "\n'{}' is currently the default account!\n{}".format(
            account_name, message
        )
    if does_user_agree(message):
        cli_account.delete_account(account_name)
        echo("account '{}' has been deleted.".format(account_name))


@account.command()
@yes_option
def delete_all():
    """Deletes all accounts and saved passwords (if any)."""
    existing_accounts = cli_account.get_all_accounts()
    if existing_accounts:
        message = (
            "\nAre you sure you want to delete the following accounts?\n\t{}"
            "\n\nThis will also delete any stored passwords and checkpoints. (y/n): "
        ).format("\n\t".join([in3account.name for in3account in existing_accounts]))
        if does_user_agree(message):
            for account_obj in existing_accounts:
                cli_account.delete_account(account_obj.name)
                echo("account '{}' has been deleted.".format(account_obj.name))
    else:
        echo("\nNo accounts exist. Nothing to delete.")


def _prompt_for_allow_private_key_set(account_name):
    if does_user_agree("Would you like to store or update your private key in keyring? (y/n): "):
        private_key = get_private_key_from_prompt()
        _set_private_key(account_name, private_key)


def _set_private_key(account_name, private_key):
    in3account = cli_account.get_account(account_name)
    try:
        validate_account(in3account)
    except Exception:
        secho("Password not stored!", bold=True)
        raise
    cli_account.set_private_key(private_key, in3account.name)
