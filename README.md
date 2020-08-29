# in3cli:  The Incubed CLI

An Incubed client at your terminal.

## Installation

```bash
python setup.py install
```

Test that it works by doing:

```bash
in3
```

You should see:

```
Usage: in3 [OPTIONS] COMMAND [ARGS]...

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

Options:
  --help  Show this message and exit.

Commands:
  end
  eth
  list-nodes
```

## Help

To find the help text for any command, add `--help` anywhere in the command:

```bash
in3 eth show-block --help
```

## list-nodes

List In3 nodes using 

```bash
in3 list-nodes
```

Include a `--format` (or `-f`) to change the format. The available formats are JSON, CSV, or DEFAULT. DEFAULT is just a 
printed to the terminal.

```bash
in3 list-nodes --format csv
```

Pipe the output to [VisiData](https://www.visidata.org/) to get prettier, more data-viewing friendly output in the terminal.

```bash
in3 list-nodes -f csv | vd
```

You should see something like 

```
Address,Deposit,Register Time,URL,Weight
0x45d45e6Ff99E6c34A235d263965910298985fcFe,1010000000000000000,1576224418,https://in3-v2.slock.it/mainnet/nd-1,2000
0x1Fe2E9bf29aa1938859Af64C413361227d04059a,2010000000000000000,1576224531,https://in3-v2.slock.it/mainnet/nd-2,2000
0x945F75c0408C0026a3CD204d36f5e47745182fd4,5010000000000000000,1576224604,https://in3-v2.slock.it/mainnet/nd-3,2000
...
```

## Ethereum Transactions

List transactions from the block with the latest block number by doing:

```bash
in3 eth list-txs
```

You should see a list of transaction hashes.

Pick any transaction hash and use the `show-tx` command to get more information about the hash:

```bash
in3 eth show-tx -h 0x8f98a2c9064f6b76ef8bfcf8747677715d382ba76c2c1f4890ac4a917097a937
```
