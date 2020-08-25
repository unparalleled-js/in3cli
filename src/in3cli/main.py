import click

from in3cli import util
from in3cli.eth import eth
from in3cli.options import format_option
import in3cli.model as model

_BANNER = """\b
            @K!m@
          @K;   :S@@
        @y,  's~  .7Q@
      @y,  'uQ  E~  .z@
    @b,  '}Q      h~  _w@
  @o,  ~6     @    @%^  .zQ
 S,  `X     W< ~X    @m,  .JQ
 K;  `}Q  8=`    ~X  @x.  :w@
  @QL` `|B@y~\Qy,  'nQ#|@@
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


@click.command()
@format_option
def list_nodes(format):
    format = format.upper()
    node_list = util.get_in3_client().refresh_node_list()
    format_func = _get_format_func(format)

    def gen():
        """Yields full CSV text, else individual formatted nodes."""
        if format == model.FormatOptions.CSV:
            nodes = [model.create_node_dict(n) for n in node_list.nodes]
            yield util.convert_list_to_csv(nodes)
        else:
            for node in node_list.nodes:
                node_dict = model.create_node_dict(node)
                yield "{}\n".format(format_func(node_dict))

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


@click.group(help=_BANNER)
def cli():
    pass


cli.add_command(eth)
cli.add_command(list_nodes)
# TODO: Add ENS command group
