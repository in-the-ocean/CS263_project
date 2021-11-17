import queue

from message import Message
from node import Node

class Graph:
    def __init__(self, pid, message_queue, send_sockets):
        self.pid = pid
        self.message_queue = message_queue
        self.nodes = {}
        self.send_sockets = send_sockets

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
