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
