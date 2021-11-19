import pickle
import queue
import threading

from communication import send
from message import Message
from node import Node

class Graph(threading.Thread):
    def __init__(self, pid, graph_message, send_sockets):
        super().__init__(daemon=True)
        self.pid = pid
        self.graph_message = graph_message
        self.nodes = {}
        self.referenced = {}
        self.send_sockets = send_sockets
    
    def new_node(self, node_id):
        if not node_id in self.nodes:
            self.nodes[node_id] = Node(self.pid, node_id)
            print(f"Node {node_id} created")
            print("self.nodes: ", self.nodes)
        else:
            print(f"Node {node_id} already present!")

    def local_reference(self, nid1, nid2):
        if not nid1 in self.nodes or not nid2 in self.nodes:
            print("connect local nodes fail: invalid ID")
            return 
        self.nodes[nid1].connect(self.pid, nid2)
        print(f"connected local nodes {nid1} {nid2}")

    def remote_reference(self, nid1, nid2, server2):
        if not nid1 in self.nodes:
            print(f"connect remote nodes fail: invalid local node ID {nid1}")
            return 
        self.nodes[nid1].connect(server2, nid2)
        message = Message("remote_connect", message=nid2, sender=self.pid)
        send(pickle.dumps(message), self.send_sockets[server2])
        print(f"connect remote node: {nid1}")

    def referenced_by(self, nid, server):
        if not nid in self.nodes:
            print(f"remote reference failed: node {nid} invalid")
            return
        self.referenced[nid] = 1
        print(f"remote reference node {nid} ")
    
    def drop(self, nid):
        if not nid in self.nodes:
            print(f"node {nid} does not exist")
            return
        self.nodes[nid].root = False 
        print(f"dropped node {nid} ")

    def run(self):
        while True:
            if self.graph_message:
                message = self.graph_message.get()
                print(message.type)
                if message.type == "Node":
                    self.new_node(message.message)
                elif message.type == "local_reference":
                    self.local_reference(message.message[0], message.message[1])
                elif message.type == "remote_reference":
                    self.remote_reference(message.message[0], message.message[1], message.message[2])
                elif message.type == "remote_connect":
                    self.referenced_by(message.message, message.sender)
                elif message.type == "drop":
                    self.drop(message.message)

    def find_scion(self, nid):
        scions = set()
        for s in self.referenced:
            if self.is_linked(s, nid):
                scions.add((self.pid, s))
        return scions

    def is_linked(self, nid1, nid2):
        visited = set()
        arr = [self.nodes[nid1]]
        visited.add(nid1)
        while len(arr):
            node = arr.pop()
            if node.id == nid2:
                return True
            for (pid, nid) in node.neighbours():
                if pid != self.pid or nid in visited:
                    continue
                visited.add(nid)
                arr.append(self.nodes(nid))                
        return False

    def hasReference(self, nid):
        visited = set()
        arr = [self.nodes[nid]]
        visited.add(nid)
        while len(arr):
            node = arr.pop()
            if node.isConnected():
                return True
            for (pid, nid) in node.neighbours():
                if pid != self.pid or nid in visited:
                    continue
                visited.add(nid)
                arr.append(self.nodes(nid))                
        return False

    def outsideConnections(self, nid):
        connections = []
        visited = set()
        arr = [self.nodes[nid]]
        visited.add(nid)
        while len(arr):
            node = arr.pop()
            for (pid, nid) in node.neighbours():
                if nid in visited:
                    continue
                if pid != self.pid:
                    connections.append((pid, nid, node.id))
                else:
                    visited.add(nid)
                    arr.append(self.nodes(nid))                
        return connections 

    def cycle_detection(self, sids, rids, visited):
        assert(rids[0] == self.pid)
        receiver = self.nodes[rids[0]]
        if self.hasReference(receiver):
            # send False to sender, as a local reference is found
            send(sids, False)
            # abort
            return
        if receiver in visited:
            # send True to sender, as a cycle is found
            send(sids, True)
        visited.add(rids)
        
        for (pid, nid) in receiver.outsideConnections():
            send((pid, nid), "cycle detection", visited)
            if recv((pid, nid)) == False:
                send(sids, False)
                # abort
                return
        # after waiting for all senders
        send(sids, True)
        
        # this is the cycle detection starter
        if not sids:
            self.remove(rids)
        return
    
    def remove(self, sids, rids, visited):
        # inform other sever to do GC
        if rids not in visited:
            visited.add(rids)
            for (pid, nid) in self.nodes[rids[1]].outsideConnections():
                send((pid, nid), "remove", visited)
                visited = {}
        # perform local GC
        arr = [rids[0]]
        while len(arr)!=0:
            id = arr.pop()
            if id not in self.nodes:
                continue
            for (pid, nid) in self.nodes[nid].neighbours:
                if pid == self.pid:
                    arr.append(nid) 
                del self.nodes[id]               
        return
            
        

