import sys
import queue
import threading
import socket
import pickle

import config
from graph import Graph
from message import *
from communication import *


class Server:
    def __init__(self, pid):
        self.pid = pid
        self.gc_message_queue = queue.Queue()
        self.graph_message_queue = queue.Queue()

        self.conn_socket = None
        self.send_sockets = {}
        self.pre_connect()
        self.conn_server = ConnServer(self.conn_socket, self.pid, self.gc_message_queue, self.graph_message_queue)
        self.conn_server.start()

        self.graph = Graph(self.pid, self.graph_message_queue, self.send_sockets)
        self.graph.start()

    def pre_connect(self):
        self.conn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_socket.bind(("127.0.0.1", config.servers[self.pid]))
        self.conn_socket.listen()

    def connect(self):
        for pid, port in config.servers.items():
            if pid == self.pid:
                continue
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(("127.0.0.1", port))
                message = Message("pid", message=self.pid)
                send(pickle.dumps(message), sock)
                self.send_sockets[pid] = sock
            except (InterruptedError, ConnectionRefusedError):
                continue

    def start(self):
        while True:
            line = sys.stdin.readline().strip().split("(")
            if not line:
                continue
            if line[0] == "exit" or line[0] == "e":
                message = Message("exit")
                # self.message_queue.put(message)
                # self.join()
                sys.exit()
            elif line[0] == "connect" or line[0] == "c":
                self.connect()
            elif line[0] == "Node": # Node(id)
                node_id = eval(line[1][:len(line[1]) - 1])
                message = Message("Node", message=node_id)
                self.graph_message_queue.put(message)
            elif line[0] == "local_reference": # local_reference(node1, node2)
                try:
                    end_points = eval("(" + line[1])
                    print(f"trying to connect nodes {end_points}")
                except:
                    print("invalid input")
                    continue
                message = Message("local_reference", message=end_points)
                self.graph_message_queue.put(message)
            elif line[0] == "remote_reference": # remote_reference(node1, node2, server2):
                try:
                    end_points = eval("(" + line[1])
                except:
                    print("invalid input")
                    continue
                message = Message("remote_reference", message=end_points)
                self.graph_message_queue.put(message)
            elif line[0] == "drop":
                line = line[1][:len(line[1]) - 1]
                message = Message("drop", message=line)


if __name__ == '__main__':
    server = Server(int(sys.argv[1]))
    server.start()
