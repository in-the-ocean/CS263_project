import pickle
import queue
import threading

from communication import send
from message import Message
from node import Node

import time

class Graph(threading.Thread):
    def __init__(self, pid, graph_message, send_sockets):
        super().__init__(daemon=True)
        self.pid = pid
        self.graph_message = graph_message
        self.nodes = {}
        self.referenced = {}
        self.send_sockets = send_sockets
        self.DFS_cycle_response = []
        self.inDFSCycleDetection = False
    
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

    def remote_reference(self, nid1, server1, nid2):
        if not nid2 in self.nodes:
            print(f"connect remote nodes fail: invalid local node ID {nid2}")
            return 
        self.nodes[nid2].remote_copy += 1
        self.referenced[(nid2, self.nodes[nid2].remote_copy)] = 1
        message = Message("remote_connect", message=(nid1, nid2), sender=self.pid)
        message.reference_id = self.nodes[nid2].remote_copy
        send(pickle.dumps(message), self.send_sockets[server1])
        print(f"connect remote node: {nid1}")

    def remote_connect(self, connection, server, rid):
        if not connection[0] in self.nodes:
            print(f"remote reference failed: node {connection[0]} invalid")
            return
        self.nodes[connection[0]].connect(server, connection[1], rid)
        print(f"neighbors of {connection[0]}: ", self.nodes[connection[0]].neighbours())
        print(f"remote connect node {connection[0]} and {connection[1]}")
    
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
                if message.type == "Node":
                    self.new_node(message.message)
                elif message.type == "local_reference":
                    self.local_reference(message.message[0], message.message[1])
                elif message.type == "remote_reference":
                    self.remote_reference(message.message[0], message.message[1], message.message[2])
                elif message.type == "remote_connect":
                    self.remote_connect(message.message, message.sender, message.reference_id)
                elif message.type == "drop":
                    self.drop(message.message)
                elif message.type == "DFS_abort" :
                    self.DFS_cycle_response.append(False)
                elif message.type == "DFS_cycle_find":
                    self.DFS_cycle_response.append(True)
                elif message.type == "DFS_cycle_detection":
                    self.DFS_cycle_detection( (message.sender,message.message[0]), (message.message[1],message.message[2]), message.visited)
                    self.inDFSCycleDetection = True
                elif message.type == "DFS_remove":
                    self.remove((message.sender,message.message[0]), (message.message[1],message.message[2]), message.visited)


    def find_scion(self, nid):
        scions = set()
        for node, rid in self.referenced:
            if self.is_linked(node, nid):
                scions.add((self.pid, node, rid))
        return scions

    def is_linked(self, nid1, nid2):
        visited = set()
        arr = [self.nodes[nid1]]
        visited.add(nid1)
        while len(arr):
            node = arr.pop()
            if node.id == nid2:
                return True
            for (pid, nid, _) in node.neighbours():
                if pid != self.pid or nid in visited:
                    continue
                visited.add(nid)
                arr.append(self.nodes[nid])                
        return False

    def hasReference(self, nid):
        visited = set()
        arr = [self.nodes[nid]]
        visited.add(nid)
        while len(arr):
            node = arr.pop()
            if node.isConnected():
                return True
            for (pid, nid, _) in node.neighbours():
                if pid != self.pid or nid in visited:
                    continue
                visited.add(nid)
                arr.append(self.nodes[nid])                
        return False

    def outsideConnections(self, nid):
        connections = []
        visited = set()
        arr = [self.nodes[nid]]
        visited.add(nid)
        while len(arr):
            node = arr.pop()
            for (pid, nid, rid) in node.neighbours():
                if nid in visited:
                    continue
                if pid != self.pid:
                    connections.append((pid, nid, rid, node.id))
                else:
                    visited.add(nid)
                    arr.append(self.nodes[nid])                
        return connections # (serveriID, nodeID, referenceID, localNodeID)


    # dfs approach
    def DFS_cycle_detection(self, sids, rids, visited):
        #print("sender:", sids, "receiver:", rids)
        assert(rids[0] == self.pid)
        if self.hasReference(rids[1]):
            # send False to sender, as a local reference is found
            message = Message("DFS_abort", message=(), sender=self.pid)
            if sids[0] != None:
                send(pickle.dumps(message), self.send_sockets[sids[0]])
            # abort
            self.inDFSCycleDetection = False
            return
        if rids in visited:
            # send True to sender, as a cycle is found
            message = Message("DFS_cycle_find", message=(), sender=self.pid)
            if sids[0] != None:
                send(pickle.dumps(message), self.send_sockets[sids[0]])
            return
        visited.add(rids)
        response = 0
        for (pid, nid, rid, localNodeID) in self.outsideConnections(rids[1]):
            message = Message("DFS_cycle_detection", message=(localNodeID, pid, nid), sender=self.pid, visited = visited)
            send(pickle.dumps(message), self.send_sockets[pid])
            response+=1

        # after waiting for all senders
        while(len(self.DFS_cycle_response) != response): 
            print(self.DFS_cycle_response, response)
            time.sleep(1)
        if False in self.DFS_cycle_response:
            message = Message("DFS_abort", message=(), sender=self.pid)
            if sids[0] != None:
                send(pickle.dumps(message), self.send_sockets[sids[0]])
            self.DFS_cycle_response = []
            # abort
            self.inDFSCycleDetection = False
            return
        else:
            message = Message("DFS_cycle_find", message=(), sender=self.pid)
            if sids[0] != None:
                send(pickle.dumps(message), self.send_sockets[sids[0]])
            self.DFS_cycle_response = []
        
        # this is the cycle detection starter
        if sids[0] == None:
            self.remove((None,None), rids)
        self.inDFSCycleDetection = False
        return
    
    def remove(self, sids, rids, visited=set()):
        # inform other sever to do GC
        print("---------REMOVE----------")
        print(sids, rids, visited) 
        print("-------------------------")
        if rids not in visited:
            visited.add(rids)
            for (pid, nid, referenceID, localNodeID) in self.outsideConnections(rids[1]):
                message = Message("DFS_remove", message=(rids[1], pid, nid), sender=self.pid, visited = visited)
                send(pickle.dumps(message), self.send_sockets[pid])
        # perform local GC
        arr = [rids[1]]
        seen = set()
        seen.add(rids[1])
        while len(arr)!=0:
            id = arr.pop()
            if id not in self.nodes:
                continue
            for (pid, nid, _) in self.nodes[id].neighbours():
                if pid == self.pid and nid not in seen:
                    arr.append(nid) 
                    seen.add(nid)
            del self.nodes[id]               
        return
            
        

