import click

from in3cli import util
from in3cli.eth import eth

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
def list_nodes():
    node_list = util.get_in3_client().refresh_node_list()

    def gen():
        for node in node_list.nodes:
            yield "URL: {}\nAddress: {}\nDeposit: {}\nWeight: {}\nRegistered in block: {}\n\n".format(
                node.url, node.address, node.deposit, node.weight, node.registerTime
            )

    click.echo_via_pager(gen)


@click.group(help=_BANNER)
def cli():
    pass


cli.add_command(eth)
cli.add_command(list_nodes)
# TODO: Add ENS command group
