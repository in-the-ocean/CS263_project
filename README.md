# CS263_project

## Usage

run server by `python3 server.py [pid]`. It currently support pid 1 to 5. If you want to create more than 5 servers, please add port numbers in `config.py`.

After all servers are up, type `connect` or `c` to servers to connect them through sockets.

Type `exit` or `e` to terminate the program.

### Servers

type `Node(nid)` or `n(nid)` to the server side to create a node with ID `nid`; nodes are accessible from root on creation

type `local_reference(nid1, nid2)` or `l(nid1, nid2)` to connect nodes `nid1` -> `nid2` locally

type `remote_reference(nid1, pid1, nid2)` or `r(nid1, pid1, nid2)` to connect nodes `nid1` -> `nid2` remotely; node `nid2` is on current server, and node `nid1` is on server with `pid1`

type `drop(nid)` to drop root reference to node `nid`

type `dfscd(nid)` to start cycle_detection on node `nid` using our proposed algorithm

type `cycle_detection(nid)` or `cd(nid)` to start cycle_detection on node `nid` using Viega and Ferreira’s Algorithm
