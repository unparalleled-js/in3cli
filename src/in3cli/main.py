import signal
import sys

import click

import in3cli.model as model
from in3cli import util
from in3cli.cmds.account import account
from in3cli.cmds.ens.ens import ens
from in3cli.cmds.eth.eth import eth
from in3cli.error import _ErrorHandlingGroup
from in3cli.options import client_options
from in3cli.options import format_option

_BANNER = """\b
            @K!m@
          @K;   :S@@
        @y,  's~  .7Q@
      @y,  'uQ  E~  .z@
    @b,  '}Q      h~  _w@
  @o,  ~6     @    @%^  .zQ
 S,  `X     W< ~X    @m,  .JQ
 K;  `}Q  8=`    ~X  @x.  :w@
  @QL` `|B@y~|Qy,  'nQ#|@@
    @&;  `|B     y,  '6@@
   @ky@&|`  ;q W7q@ !  'nQ@
 @U~  |@@&|`  ~`  f  d,  '}Q@
@7   `Q    #?`  !d    Q~   ;Q@
 @W<` `iQ    QyQ     y`  ~U@
   @8<  `vQ        a,  ~U@
     @X~  `7Q    a,  'X@
      @g=`  ^Di`  ~X@
         @W>`    ~X@
           @g= ~k@
             @Q@
"""


# Handle KeyboardInterrupts by just exiting instead of printing out a stack
def exit_on_interrupt(signal, frame):
    click.echo(err=True)
    sys.exit(1)


signal.signal(signal.SIGINT, exit_on_interrupt)


@click.command()
@format_option
@client_options()
def list_nodes(state, format):
    """Lists In3 node information."""
    _format = format.upper()
    node_list = state.client.refresh_node_list()
    format_func = _get_format_func(_format)

    def gen():
        """Yields full CSV text, else individual formatted nodes."""
        if _format == model.FormatOptions.CSV:
            nodes = [model.create_node_dict(n) for n in node_list.nodes]
            yield util.convert_list_to_csv(nodes)
        else:
            for node in node_list.nodes:
                node_dict = model.create_node_dict(node)
                output = format_func(node_dict)
                yield "{}\n".format(output)
    click.echo_via_pager(gen)


def _get_format_func(format_choice):
    if format_choice == model.FormatOptions.CSV:
        return util.convert_list_to_csv
    elif format_choice == model.FormatOptions.JSON:
        return util.convert_dict_to_json
    return _format_node_table_entry


def _format_node_table_entry(node_dict):
    builder = ""
    for k, v in node_dict.items():
        builder += "{}: {}\n".format(k, v)
    return builder


_CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 200,
}


@click.group(cls=_ErrorHandlingGroup, context_settings=_CONTEXT_SETTINGS, help=_BANNER)
@client_options(hidden=True)
def cli(state):
    pass


cli.add_command(eth)
cli.add_command(list_nodes)
cli.add_command(ens)
cli.add_command(account)
