import csv
import datetime
import io
import json

import in3
import click


REGISTRY_CONTRACT_ADDRESS = "0x6C095A05764A23156eFD9D603eaDa144a9B1AF33"


def get_in3_client():
    config = in3.ClientConfig(transport_ignore_tls=True)
    return in3.Client(in3_config=config)


def print_dict(d):
    for k, v, in d.items():
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
