import queue

from message import Message
from node import Node

class Graph:
    def __init__(self, pid, message_queue):
        self.pid = pid
        self.message_queue = message_queue
        self.nodes = {}

    def run(self):
        while True:
            if self.message_queue:
                message = self.message_queue.get()
                if message.type == "Node":
                    node_id = message.message
                    self.nodes[node_id] = Node(self.pid, node_id)
                elif message.type == "local_reference":
                    if not message.message[0] in self.nodes or not message.message[1] in self.nodes:
                        print("connect local nodes fail: invalid ID")
                        continue
                    self.nodes[message.message[0]].connect(self.pid, message.message[1])
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
            
        

