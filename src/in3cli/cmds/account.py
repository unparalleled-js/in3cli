import click
import in3cli.account as account_module
from click import echo
from in3cli.client import validate
from in3cli.enums import Chain
from in3cli.error import In3CliError
from in3cli.options import address_option
from in3cli.options import yes_option
from in3cli.private_key import get_private_key_from_prompt
from in3cli.util import does_user_agree


@click.group()
def account():
    """For managing In3 wallet settings."""
    pass


set_chain_option = click.option(
    "--chain",
    "-c",
    type=click.Choice(Chain.options(), case_sensitive=False),
    help="The blockchain network to use.",
)


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


@address_option
@private_key_option
@disable_ssl_option
@account.command()
@name_option
@set_chain_option
def create(name, address, private_key, chain, disable_ssl_errors):
    """Create account settings. The first account created will be the default."""
    account_module.create_account(
        name,
        address,
        chain,
        disable_ssl_errors,
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
@set_chain_option
@disable_ssl_option
def update(name, address, private_key, chain, disable_ssl_errors):
    """Update an existing account."""
    in3account = account_module.get_account(name)
    account_module.update_account(
        in3account.name,
        address,
        chain,
        disable_ssl_errors,
    )
    if private_key:
        _set_private_key(name, private_key)
    else:
        _prompt_for_allow_private_key_set(in3account.name)
    echo("Account '{}' has been updated.".format(in3account.name))


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
    message = (
        "\nDeleting this account will also delete any stored private keys. Are you sure? (y/n): "
    )
    if account_module.is_default_account(account_name):
        message = "\n'{}' is currently the default account!\n{}".format(account_name, message)
    if does_user_agree(message):
        account_module.delete_account(account_name)
        echo("Account '{}' has been deleted.".format(account_name))


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
                echo("Account '{}' has been deleted.".format(account_obj.name))
    else:
        echo("\nNo accounts exist. Nothing to delete.")


def _prompt_for_allow_private_key_set(account_name):
    user_ans = does_user_agree(
        "Would you like to store or update your private key in keyring? (y/n): "
    )
    if user_ans:
        private_key = get_private_key_from_prompt()
        _set_private_key(account_name, private_key)


def _set_private_key(account_name, private_key):
    def _error(raised_err):
        raise raised_err

    if len(private_key) == 64 and private_key[1] != "x":
        private_key = "0x{}".format(private_key)
    elif len(private_key) != 66:
        _error(Exception("Invalid private key"))

    in3account = account_module.get_account(account_name)
    try:
        is_valid = validate(in3account, private_key)
        if not is_valid:
            _error(Exception("Invalid client."))
    except Exception as err:
        _error(err)
    account_module.set_private_key(private_key, in3account.name)
