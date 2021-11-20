import pickle
import threading

from communication import send
from graph import Graph
from message import Message

class CycleDetection(threading.Thread):
    def __init__(self, gc_message_queue, send_sockets, graph: Graph):
        super().__init__(daemon=True)
        self.gc_message_queue = gc_message_queue
        self.send_sockets = send_sockets
        self.graph = graph

    def start_cycle_detection(self, nid):
        message = Message("cycle detection")
        self.calculate_next_step(nid, message)
    
    def calculate_next_step(self, nid, message):
        if not nid in self.graph.nodes:
            return
        if self.graph.hasReference(nid):
            print(f"node {nid} is accessible from root")
            return
        stubs = self.graph.outsideConnections(nid)
        if not stubs:
            print(f"node {nid} does not lead to stub")
            return
        print("stubs", stubs)
        for s in stubs:
            if (s[0], s[1], s[2]) not in message.stubs:
                scions = self.graph.find_scion(s[3])
                if not scions:
                    print(f"no scions lead to node {nid}")
                    return
                message.scions = message.scions.union(scions)
                message.stubs.add((s[0], s[1], s[2]))
                message.target = s[1]
                message.sender = self.graph.pid
                send(pickle.dumps(message), self.send_sockets[s[0]])
                return
    
    def run(self):
        while True:
            if self.gc_message_queue:
                message = self.gc_message_queue.get()
                print(message.type)
                if message.type == "start":
                    self.start_cycle_detection(message.message)
                elif message.type == "cycle detection":
                    print(f"receive gc message: {message.scions} -> {message.stubs}, target {message.target}")
                    scions_diff = message.scions - message.stubs
                    stubs_diff = message.stubs - message.scions
                    if not scions_diff and not stubs_diff:
                        print(f"cycle detected: {message.scions}")
                        continue
                    self.calculate_next_step(message.target, message)

