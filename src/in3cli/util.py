import in3
import click


REGISTRY_CONTRACT_ADDRESS = "0x6C095A05764A23156eFD9D603eaDa144a9B1AF33"


def get_in3_client():
    config = in3.ClientConfig(transport_ignore_tls=True)
    return in3.Client(in3_config=config)


def print_dict(d):
    for k, v, in d.items():
        click.echo("{}: {}".format(k, v))
