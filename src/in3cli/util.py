import csv
import datetime
import io
import json
import os
import shutil
import time
from collections import OrderedDict
from os import path

import click
import in3.exception as in3err
from in3cli.error import In3CliChainTimeoutError

_PADDING_SIZE = 3


WEI_PER_ETH = 10000000000000000000.0
WEI_PER_GWEI = 1000000000.0


def wei_to_gwei(wei):
    return wei / WEI_PER_GWEI


def wei_to_eth(wei):
    return wei / WEI_PER_ETH


def eth_to_wei(eth):
    return eth * WEI_PER_ETH


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


def to_bool(val):
    def _error():
        raise ValueError("{} not supported for to_bool() method.".format(type(val)))

    if isinstance(val, bool):
        return val

    elif isinstance(val, int):
        return val == 1

    if not isinstance(val, str):
        _error()

    val = val.lower()
    if val in ["true", "t"]:
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


def find_format_width(record, header, include_header=True):
    """Fetches needed keys/items to be displayed based on header keys.

    Finds the largest string against each column so as to decide the padding size for the column.

    Args:
        record (dict): data to be formatted.
        header (dict): key-value where keys should map to keys of record dict and
          value is the corresponding column name to be displayed on the CLI.
        include_header (bool): include header in output, defaults to True.

    Returns:
        tuple (list of dict, dict): i.e Filtered records, padding size of columns.
    """
    rows = []
    if include_header:
        if not header:
            header = _get_default_header(record)
        rows.append(header)
    # noinspection PyTypeChecker
    max_width_item = dict(header.items())  # Copy
    for record_row in record:
        row = OrderedDict()
        for header_key in header.keys():
            item = record_row.get(header_key)
            row[header_key] = item
            max_width_item[header_key] = max(max_width_item[header_key], str(item), key=len)
        rows.append(row)
    column_size = {key: len(value) for key, value in max_width_item.items()}
    return rows, column_size


def _get_default_header(header_items):
    if not header_items:
        return

    # Creates dict where keys and values are the same for `find_format_width()`.
    header = {}
    for item in header_items:
        keys = item.keys()
        for key in keys:
            if key not in header and isinstance(key, str):
                header[key] = key
    return header


def format_to_table(rows, column_size):
    """Formats given rows into a string of left justified table."""
    lines = []
    for row in rows:
        line = ""
        for key in row.keys():
            line += str(row[key]).ljust(column_size[key] + _PADDING_SIZE)
        lines.append(line)
    return "\n".join(lines)


def format_string_list_to_columns(string_list, max_width=None):
    """Prints a list of strings in justified columns and fits them neatly into specified width."""
    if not string_list:
        return
    if not max_width:
        max_width, _ = shutil.get_terminal_size()
    column_width = len(max(string_list, key=len)) + _PADDING_SIZE
    num_columns = int(max_width / column_width) or 1
    format_string = "{{:<{0}}}".format(column_width) * num_columns
    batches = [string_list[i : i + num_columns] for i in range(0, len(string_list), num_columns)]
    padding = ["" for _ in range(num_columns)]
    for batch in batches:
        click.echo(format_string.format(*batch + padding))
    click.echo()


def run_with_timeout(func):
    res = None
    tries = 0
    max_tries = 5
    while res is None:
        try:
            res = func()
        except in3err.ClientException:
            time.sleep(1)
            tries += 1
            if tries == max_tries:
                raise In3CliChainTimeoutError("block")
            continue
    return res
