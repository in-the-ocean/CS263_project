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

    def local_reference(self, node1, node2):
        if not node1 in self.nodes or not node2 in self.nodes:
            print("connect local nodes fail: invalid ID")
            return 
        self.nodes[node1].connect(self.pid, node2)
        print(f"connected local nodes {node1} {node2}")

    def remote_reference(self, node1, node2, server2):
        if not node1 in self.nodes:
            print(f"connect remote nodes fail: invalid local node ID {node1}")
            return 
        self.nodes[node1].connect(server2, node2)
        message = Message("remote_connect", message=node2, sender=self.pid)
        send(pickle.dumps(message), self.send_sockets[server2])
        print(f"connect remote node: {node1}")

    def referenced_by(self, node, server):
        if not node in self.nodes:
            print(f"remote reference failed: node {node} invalid")
            return
        self.referenced[node] = 1
        print(f"remote reference node {node} ")

    
    def drop(self, node):
        if not node in self.nodes:
            print(f"node {node} does not exist")
            return
        self.nodes[node].connected = False 

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

    def hasReference(self, nid):
        visited = {}
        arr = [self.nodes(nid)]
        visited.add(nid)
        while len(arr)!=0:
            node = arr.pop()
            if node.isConnected():
                return True
            for (pid, nid) in node.neighbours:
                if pid != self.pid or nid in visited:
                    continue
                visited.add(nid)
                arr.append(self.nodes(nid))                
        return False

    def outsideConnections(self, nid):
        connections = []
        visited = {}
        arr = [self.nodes(nid)]
        visited.add(nid)
        while len(arr)!=0:
            node = arr.pop()
            for (pid, nid) in node.neighbours:
                if nid in visited:
                    continue
                if pid != self.pid:
                    connections.append((pid, nid))
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
            
        

