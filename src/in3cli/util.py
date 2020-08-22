import datetime
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


def print_dict_as_json(json_dict):
    json_str = json.dumps(json_dict, indent=4)
    click.echo(json_str)


def print_list(items):
    def gen():
        for item in items:
            yield "{}\n".format(item)
    click.echo_via_pager(gen)


def convert_timestamp_to_date_str(timestamp):
    date = datetime.datetime.utcfromtimestamp(timestamp)
    return date.strftime('%Y-%m-%d %H:%M:%S')
