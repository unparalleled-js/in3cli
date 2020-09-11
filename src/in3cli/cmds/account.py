from getpass import getpass

import click
from click import echo
from click import secho

import in3cli.account as cli_account
from in3cli.error import In3CliError
from in3cli.options import yes_option
from in3cli.client import validate_account
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
server_option = click.option(
    "-s",
    "--server",
    required=True,
    help="The URL you use to sign into in3.",
)

username_option = click.option(
    "-u",
    "--username",
    required=True,
    help="The username of the in3 API user.",
)

private_key_option = click.option(
    "--private-key",
    help="The private key for the wallet to use. It is not recommended to use this option. "
         "If this option is omitted, interactive prompts will be used to obtain the password.",
)

disable_ssl_option = click.option(
    "--disable-ssl-errors",
    is_flag=True,
    help="For development purposes, do not validate the SSL certificates of in3 servers. "
    "This is not recommended, except for specific scenarios like testing.",
)


@account.command()
@account_name_arg
def show(account_name):
    """Print the details of an account."""
    c42account = cli_account.get_account(account_name)
    echo("\n{}:".format(c42account.name))
    echo("\t* address = {}".format(c42account.username))
    echo("\t* ignore-ssl-errors = {}".format(c42account.ignore_ssl_errors))
    if cli_account.get_stored_private_key(c42account.name) is not None:
        echo("\t* Private key is set.")
    echo("")
    echo("")


@account.command()
@name_option
@server_option
@username_option
@private_key_option
@disable_ssl_option
def create(name, server, username, private_key, disable_ssl_errors):
    """Create account settings. The first account created will be the default."""
    cli_account.create_account(name, server, username, disable_ssl_errors)
    if private_key:
        _set_private_key(name, private_key)
    else:
        _prompt_for_allow_private_key_set(name)
    echo("Successfully created account '{}'.".format(name))


@account.command()
@name_option
@server_option
@username_option
@private_key_option
@disable_ssl_option
def update(name, server, username, password, disable_ssl_errors):
    """Update an existing account."""
    c42account = cli_account.get_account(name)
    cli_account.update_account(c42account.name, server, username, disable_ssl_errors)
    if password:
        _set_private_key(name, password)
    else:
        _prompt_for_allow_private_key_set(c42account.name)
    echo("account '{}' has been updated.".format(c42account.name))


@account.command()
@account_name_arg
def reset_private_key(account_name):
    """\b
    Change the stored password for a account. Only affects what's stored in the local account,
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
    for c42account in accounts:
        echo(str(c42account))


@account.command()
@account_name_arg
def use(account_name):
    """Set a account as the default."""
    cli_account.switch_default_account(account_name)
    echo("{} has been set as the default account.".format(account_name))


@account.command()
@yes_option
@account_name_arg
def delete(account_name):
    """Deletes a account and its stored password (if any)."""
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
        ).format("\n\t".join([c42account.name for c42account in existing_accounts]))
        if does_user_agree(message):
            for account_obj in existing_accounts:
                cli_account.delete_account(account_obj.name)
                echo("account '{}' has been deleted.".format(account_obj.name))
    else:
        echo("\nNo accounts exist. Nothing to delete.")


def _prompt_for_allow_private_key_set(account_name):
    if does_user_agree("Would you like to set a password? (y/n): "):
        password = getpass()
        _set_private_key(account_name, password)


def _set_private_key(account_name, password):
    c42account = cli_account.get_account(account_name)
    try:
        validate_account(c42account)
    except Exception:
        secho("Password not stored!", bold=True)
        raise
    cli_account.set_private_key(password, c42account.name)
