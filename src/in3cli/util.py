import csv
import datetime
import io
import json
import os
from os import path

import click

REGISTRY_CONTRACT_ADDRESS = "0x6C095A05764A23156eFD9D603eaDa144a9B1AF33"


def wei_to_gwei(wei):
    return float(wei) / 1000000000


def print_dict(d):
    for (
        k,
        v,
    ) in d.items():
        if v:
            click.echo("{}: {}".format(k, v))


def convert_dict_to_json(json_dict):
    return json.dumps(json_dict, indent=4)


def print_dict_as_json(json_dict):
    json_str = convert_dict_to_json(json_dict)
    click.echo(json_str)


def convert_dict_to_csv(obj_dict):
    fieldnames = list(obj_dict.keys())
    writer, string_io = _write_csv_header(fieldnames)
    writer.writeheader()
    writer.writerow(obj_dict)
    return string_io.getvalue().strip()


def convert_list_to_csv(obj_list):
    fieldnames = list({k for d in obj_list for k in d.keys()})
    fieldnames.sort()
    writer, string_io = _write_csv_header(fieldnames)
    writer.writerows(obj_list)
    return string_io.getvalue().strip()


def _write_csv_header(fieldnames):
    string_io = io.StringIO()
    writer = csv.DictWriter(string_io, fieldnames=fieldnames)
    writer.writeheader()
    return writer, string_io


def print_dict_as_csv(obj_dict):
    output = convert_dict_to_csv(obj_dict)
    click.echo(output)


def print_list(items):
    def gen():
        for item in items:
            yield "{}\n".format(item)

    click.echo_via_pager(gen)


def convert_timestamp_to_date_str(timestamp):
    date = datetime.datetime.utcfromtimestamp(timestamp)
    return date.strftime("%Y-%m-%d %H:%M:%S")


def does_user_agree(prompt):
    """Prompts the user and checks if they said yes. If command has the `yes_option` flag, and
    `-y/--yes` is passed, this will always return `True`.
    """
    ctx = click.get_current_context()
    if ctx.obj.assume_yes:
        return True
    ans = input(prompt)
    ans = ans.strip().lower()
    return ans == "y"


def get_user_project_path(*subdirs):
    """The path on your user dir to /.in3cli/[subdir]."""
    package_name = __name__.split(".")[0]
    home = path.expanduser("~")
    hidden_package_name = ".{}".format(package_name)
    user_project_path = path.join(home, hidden_package_name)
    result_path = path.join(user_project_path, *subdirs)
    if not path.exists(result_path):
        os.makedirs(result_path)
    return result_path


def str_to_bool(val):
    def _error():
        raise ValueError("val must be either 't', 'true', 'f', or 'false'. Not {}.".format(val))

    val = val.lower()
    if not isinstance(val, str):
        _error()
    elif val in ["true", "t"]:
        return True
    elif val in ["false", "f"]:
        return False
    _error()


def get_attribute_keys_from_class(cls):
    """Returns attribute names for the given class.
    Args:
        cls (class): The class to obtain attributes from.
    Returns:
        (list): A list containing the attribute names of the given class.
    """
    return [
        cls().__getattribute__(attr)
        for attr in dir(cls)
        if not callable(cls().__getattribute__(attr)) and not attr.startswith(u"_")
    ]
