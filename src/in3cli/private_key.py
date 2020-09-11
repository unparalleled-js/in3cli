from getpass import getpass

import keyring

from in3cli import __PRODUCT_NAME__
from in3cli.util import does_user_agree


def get_stored_private_key(profile):
    """Gets your currently stored password for the given profile name."""
    service_name = _get_keyring_service_name(profile.name)
    return keyring.get_password(service_name, profile.username)


def get_private_key_from_prompt():
    """Prompts you and returns what you input."""
    return getpass()


def set_private_key(profile, new_password):
    """Sets your password for the given profile name."""
    service_name = _get_keyring_service_name(profile.name)
    uses_file_storage = keyring.get_keyring().priority < 1
    if uses_file_storage and not _prompt_for_alternative_store():
        return

    keyring.set_password(service_name, profile.username, new_password)


def delete_private_key(profile):
    """Deletes the private key for the given profile name."""
    service_name = _get_keyring_service_name(profile.name)
    keyring.delete_password(service_name, profile.username)


def _get_keyring_service_name(profile_name):
    return "{}::{}".format(__PRODUCT_NAME__, profile_name)


def _prompt_for_alternative_store():
    prompt = (
        "keyring is unavailable. Would you like to store in secure flat file? (y/n): "
    )
    return does_user_agree(prompt)
