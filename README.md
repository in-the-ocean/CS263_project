# CS263_project

## Usage

run server by `python3 server.py [pid]`

After all servers are up, type `connect` or `c` to servers to connect them through sockets.

Type `exit` or `e` to terminate the program.

### Servers

type `Node(nid)` or `n(nid)` to the server side to create a node with ID `nid`; nodes are accessible from root on creation

type `local_reference(nid1, nid2)` or `l(nid1, nid2)` to connect nodes `nid1` -> `nid2` locally

type `remote_reference(nid1, pid1, nid2)` or `r(nid1, pid1, nid2)` to connect nodes `nid1` -> `nid2` remotely; node `nid2` is on current server, and node `nid1` is on server with `pid1`

type `drop(nid)` to drop root reference to node `nid`

type `cycle_detection(nid)` or `cd(nid)` to start cycle_detection on node `nid`
