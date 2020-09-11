from getpass import getpass

import click
from click import echo
from click import secho

import in3cli.account as cliaccount
from in3cli.error import in3CLIError
from in3cli.options import yes_option
from in3cli.account import CREATE_account_HELP
from in3cli.util import validate_account
from in3cli.util import does_user_agree


@click.group()
def account():
    """For managing in3 connection settings."""
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

password_option = click.option(
    "--password",
    help="The password for the in3 API user. If this option is omitted, interactive prompts "
    "will be used to obtain the password.",
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
    """Print the details of a account."""
    c42account = cliaccount.get_account(account_name)
    echo("\n{}:".format(c42account.name))
    echo("\t* username = {}".format(c42account.username))
    echo("\t* authority url = {}".format(c42account.authority_url))
    echo("\t* ignore-ssl-errors = {}".format(c42account.ignore_ssl_errors))
    if cliaccount.get_stored_password(c42account.name) is not None:
        echo("\t* A password is set.")
    echo("")
    echo("")


@account.command()
@name_option
@server_option
@username_option
@password_option
@disable_ssl_option
def create(name, server, username, password, disable_ssl_errors):
    """Create account settings. The first account created will be the default."""
    cliaccount.create_account(name, server, username, disable_ssl_errors)
    if password:
        _set_pw(name, password)
    else:
        _prompt_for_allow_password_set(name)
    echo("Successfully created account '{}'.".format(name))


@account.command()
@name_option
@server_option
@username_option
@password_option
@disable_ssl_option
def update(name, server, username, password, disable_ssl_errors):
    """Update an existing account."""
    c42account = cliaccount.get_account(name)
    cliaccount.update_account(c42account.name, server, username, disable_ssl_errors)
    if password:
        _set_pw(name, password)
    else:
        _prompt_for_allow_password_set(c42account.name)
    echo("account '{}' has been updated.".format(c42account.name))


@account.command()
@account_name_arg
def reset_pw(account_name):
    """\b
    Change the stored password for a account. Only affects what's stored in the local account,
    does not make any changes to the in3 user account."""
    password = getpass()
    _set_pw(account_name, password)
    echo("Password updated for account '{}'".format(account_name))


@account.command("list")
def _list():
    """Show all existing stored accounts."""
    accounts = cliaccount.get_all_accounts()
    if not accounts:
        raise in3CLIError("No existing account.", help=CREATE_account_HELP)
    for c42account in accounts:
        echo(str(c42account))


@account.command()
@account_name_arg
def use(account_name):
    """Set a account as the default."""
    cliaccount.switch_default_account(account_name)
    echo("{} has been set as the default account.".format(account_name))


@account.command()
@yes_option
@account_name_arg
def delete(account_name):
    """Deletes a account and its stored password (if any)."""
    message = "\nDeleting this account will also delete any stored passwords and checkpoints. Are you sure? (y/n): "
    if cliaccount.is_default_account(account_name):
        message = "\n'{}' is currently the default account!\n{}".format(
            account_name, message
        )
    if does_user_agree(message):
        cliaccount.delete_account(account_name)
        echo("account '{}' has been deleted.".format(account_name))


@account.command()
@yes_option
def delete_all():
    """Deletes all accounts and saved passwords (if any)."""
    existing_accounts = cliaccount.get_all_accounts()
    if existing_accounts:
        message = (
            "\nAre you sure you want to delete the following accounts?\n\t{}"
            "\n\nThis will also delete any stored passwords and checkpoints. (y/n): "
        ).format("\n\t".join([c42account.name for c42account in existing_accounts]))
        if does_user_agree(message):
            for account_obj in existing_accounts:
                cliaccount.delete_account(account_obj.name)
                echo("account '{}' has been deleted.".format(account_obj.name))
    else:
        echo("\nNo accounts exist. Nothing to delete.")


def _prompt_for_allow_password_set(account_name):
    if does_user_agree("Would you like to set a password? (y/n): "):
        password = getpass()
        _set_pw(account_name, password)


def _set_pw(account_name, password):
    c42account = cliaccount.get_account(account_name)
    try:
        validate_connection(c42account.authority_url, c42account.username, password)
    except Exception:
        secho("Password not stored!", bold=True)
        raise
    cliaccount.set_password(password, c42account.name)
